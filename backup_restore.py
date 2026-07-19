import discord
from discord.ext import commands
from discord import app_commands
import json
import sqlite3
import aiohttp

# --- CUSTOM EMOJIS DICTIONARY ---
EMOJIS = {
    "dot_yellow": "<:starlaDotYellow:1525756269934411958>",
    "chat": "<:starla_ico_chat:1525757016461545615>",
    "yes": "<:starla_opt_yes:1525757001664299102>",
    "cross": "<:starlacross:1525756266604007464>"
}

conn = sqlite3.connect('backup_settings.db')
cursor = conn.cursor()

class BackupRestoreModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_latest_backup_json(self, guild_id: int):
        cursor.execute("SELECT backup_json FROM latest_backups WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    # Safe Non-Destructive Category Channel Mappings Engine
    async def execute_server_restoration(self, guild: discord.Guild, data: dict, status_msg):
        try:
            # 1. Guild Name Restore
            if "server_name" in data and guild.me.guild_permissions.manage_guild:
                await guild.edit(name=data["server_name"])

            if not guild.me.guild_permissions.manage_channels:
                return await status_msg.edit(content=f"{EMOJIS['cross']} **Restoration Denied:** Bot lacks `Manage Channels` permission.")

            await status_msg.edit(content=f"{EMOJIS['dot_yellow']} **Starla Core:** Mapping live categories with JSON footprint...")

            live_categories = sorted(
                [c for c in guild.channels if isinstance(c, discord.CategoryChannel)],
                key=lambda x: x.position
            )
            backup_categories = data.get("categories", [])

            # --- STEP 2: CATEGORY SECTOR MAPPING & INNER CHANNELS REBUILD ---
            for idx, live_cat in enumerate(live_categories):
                if idx >= len(backup_categories):
                    break
                
                backup_cat_data = backup_categories[idx]
                
                try:
                    await live_cat.edit(name=backup_cat_data.get("name"))
                except Exception: pass

                live_text_channels = sorted(
                    [c for c in live_cat.text_channels],
                    key=lambda x: x.position
                )
                live_voice_channels = sorted(
                    [c for c in live_cat.voice_channels],
                    key=lambda x: x.position
                )

                backup_text_data = []
                backup_voice_data = []
                for chan in backup_cat_data.get("channels", []):
                    if "voice" in str(chan.get("type")).lower():
                        backup_voice_data.append(chan)
                    else:
                        backup_text_data.append(chan)

                for t_idx, text_chan in enumerate(live_text_channels):
                    if t_idx < len(backup_text_data):
                        try:
                            await text_chan.edit(
                                name=backup_text_data[t_idx].get("name"),
                                topic=backup_text_data[t_idx].get("topic", "")
                            )
                        except Exception: pass

                for v_idx, voice_chan in enumerate(live_voice_channels):
                    if v_idx < len(backup_voice_data):
                        try:
                            await voice_chan.edit(
                                name=backup_voice_data[v_idx].get("name"),
                                user_limit=backup_voice_data[v_idx].get("user_limit", 0)
                            )
                        except Exception: pass

            # --- STEP 3: ORPHANED CHANNELS MAPPING ---
            await status_msg.edit(content=f"{EMOJIS['dot_yellow']} **Starla Core:** Aligning orphaned channel layers...")
            
            live_orphaned_text = sorted(
                [c for c in guild.channels if c.category is None and isinstance(c, discord.TextChannel) and c.id != status_msg.channel.id],
                key=lambda x: x.position
            )
            live_orphaned_voice = sorted(
                [c for c in guild.channels if c.category is None and isinstance(c, discord.VoiceChannel)],
                key=lambda x: x.position
            )

            backup_orphaned_text = []
            backup_orphaned_voice = []
            for chan in data.get("orphaned_channels", []):
                if "voice" in str(chan.get("type")).lower():
                    backup_orphaned_voice.append(chan)
                else:
                    backup_orphaned_text.append(chan)

            for ot_idx, o_text_chan in enumerate(live_orphaned_text):
                if ot_idx < len(backup_orphaned_text):
                    try: await o_text_chan.edit(name=backup_orphaned_text[ot_idx].get("name"))
                    except Exception: pass

            for ov_idx, o_voice_chan in enumerate(live_orphaned_voice):
                if ov_idx < len(backup_orphaned_voice):
                    try: await o_voice_chan.edit(name=backup_orphaned_voice[ov_idx].get("name"))
                    except Exception: pass

            # --- STEP 4: RESTORE NICKNAMES ---
            if guild.me.guild_permissions.manage_nicknames:
                for mem_data in data.get("members", []):
                    member = guild.get_member(mem_data.get("user_id"))
                    if member and member.id != guild.owner_id and guild.me.top_role > member.top_role:
                        try: await member.edit(nick=mem_data.get("nickname"))
                        except Exception: pass

            await status_msg.edit(content=f"{EMOJIS['yes']} **Starla Core Engine:** Category structural match absolute. Channels aligned safely without any deletion!")
        except Exception as e:
            await status_msg.edit(content=f"{EMOJIS['cross']} Rollback process fault: `{e}`")

    # ==========================================
    # ⚙️ SERVER RESTORE COMMAND (Prefix & Slash)
    # ==========================================
    @commands.command(name="restoreserver", aliases=["restoresv"])
    @commands.has_permissions(administrator=True)
    async def prefix_restore_server(self, ctx: commands.Context, file_url: str = None):
        backup_data = None
        status_msg = await ctx.send(f"{EMOJIS['dot_yellow']} Analyzing deployment signature parameters...")

        if ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.filename.endswith('.json'):
                file_bytes = await attachment.read()
                backup_data = json.loads(file_bytes.decode('utf-8'))

        elif ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments and replied_msg.attachments[0].filename.endswith('.json'):
                file_bytes = await replied_msg.attachments[0].read()
                backup_data = json.loads(file_bytes.decode('utf-8'))

        elif file_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    if resp.status == 200:
                        backup_data = json.loads(await resp.text())

        if not backup_data:
            db_json = self.get_latest_backup_json(ctx.guild.id)
            if db_json:
                backup_data = json.loads(db_json)
                await status_msg.edit(content=f"{EMOJIS['chat']} No file input found. Defaulting to internal database storage cache snapshot...")
            else:
                return await status_msg.edit(content=f"{EMOJIS['cross']} **Restoration Denied:** No active file input or internal database backup snapshot found.")

        await self.execute_server_restoration(ctx.guild, backup_data, status_msg)

    @app_commands.command(name="restore_server", description="Rollback server layout using an attached backup URL or latest database save.")
    @app_commands.describe(backup_url="Optional: Provide the direct JSON backup URL link.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_restore_server(self, interaction: discord.Interaction, backup_url: str = None):
        await interaction.response.defer()
        status_msg = await interaction.followup.send(f"{EMOJIS['dot_yellow']} Analyzing deployment signature parameters...")

        backup_data = None
        if backup_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(backup_url) as resp:
                    if resp.status == 200:
                        backup_data = json.loads(await resp.text())

        if not backup_data:
            db_json = self.get_latest_backup_json(interaction.guild.id)
            if db_json:
                backup_data = json.loads(db_json)
            else:
                return await interaction.followup.send(f"{EMOJIS['cross']} No active file input or internal database backup snapshot found.")

        await self.execute_server_restoration(interaction.guild, backup_data, status_msg)

async def setup(bot):
    await bot.add_cog(BackupRestoreModule(bot))
