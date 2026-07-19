import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import io
import datetime
import sqlite3
import aiohttp

# --- CUSTOM EMOJIS DICTIONARY ---
EMOJIS = {
    "dot_black": "<:starlaDotBlack:1525756435089063948>",
    "dot_blue": "<:starlaDotBlue:1525756437224099862>",
    "dot_green": "<:starlaDotGreen:1525756444782104597>",
    "dot_orange": "<:starlaDotOrange:1525756452487168121>",
    "dot_red": "<:starlaDotRed:1525756464692596886>",
    "dot_yellow": "<:starlaDotYellow:1525756269934411958>",
    "bonk": "<:starla_ico_bonk:1525756094776082523>",
    "chat": "<:starla_ico_chat:1525757016461545615>",
    "delete": "<:starla_ico_delete:1525756992327516191>",
    "heart": "<:starla_ico_heart:1525757023277289603>",
    "info": "<:starla_ico_info:1525756986283524238>",
    "mod": "<:starla_ico_mod:1525757006823161897>",
    "no": "<:starla_opt_no:1525756996886986885>",
    "yes": "<:starla_opt_yes:1525757001664299102>",
    "cross": "<:starlacross:1525756266604007464>",
    "arrow": "<:starlalyf_arrowglow:1525757297475850320>",
    "dot_pink": "<:topggDotPink:1525756454345375764>"
}

# --- DATABASE SETUP ---
conn = sqlite3.connect('backup_settings.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS backup_channels (
        guild_id INTEGER PRIMARY KEY,
        channel_id INTEGER
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS latest_backups (
        guild_id INTEGER PRIMARY KEY,
        backup_json TEXT
    )
''')
conn.commit()

class BackupModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_backup.start()

    def cog_unload(self):
        self.auto_backup.cancel()

    # Database Helpers
    def get_backup_channel_id(self, guild_id: int):
        cursor.execute("SELECT channel_id FROM backup_channels WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def set_backup_channel_id(self, guild_id: int, channel_id: int):
        cursor.execute("INSERT OR REPLACE INTO backup_channels (guild_id, channel_id) VALUES (?, ?)", (guild_id, channel_id))
        conn.commit()

    def save_latest_backup_json(self, guild_id: int, json_str: str):
        cursor.execute("INSERT OR REPLACE INTO latest_backups (guild_id, backup_json) VALUES (?, ?)", (guild_id, json_str))
        conn.commit()

    def get_latest_backup_json(self, guild_id: int):
        cursor.execute("SELECT backup_json FROM latest_backups WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_channel_overwrites(self, channel):
        overwrites_list = []
        for target, overwrite in channel.overwrites.items():
            overwrites_list.append({
                "target_id": target.id,
                "target_type": "role" if isinstance(target, discord.Role) else "member",
                "target_name": target.name,
                "allow": overwrite.pair()[0].value,
                "deny": overwrite.pair()[1].value
            })
        return overwrites_list

    # Core Backup Generator Function
    async def generate_server_backup(self, guild: discord.Guild):
        all_fetched_channels = await guild.fetch_channels()

        backup_data = {
            "server_name": guild.name,
            "server_id": guild.id,
            "icon_url": str(guild.icon.url) if guild.icon else None,
            "banner_url": str(guild.banner.url) if guild.banner else None,
            "verification_level": str(guild.verification_level),
            "backup_time": str(datetime.datetime.now()),
            "roles": [],
            "categories": [],
            "orphaned_channels": [],
            "members": []
        }

        for role in reversed(guild.roles):
            if role.is_default():
                continue
            backup_data["roles"].append({
                "id": role.id,
                "name": role.name,
                "color": str(role.color),
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "permissions": role.permissions.value
            })

        categories = [c for c in all_fetched_channels if isinstance(c, discord.CategoryChannel)]
        text_and_voice = [c for c in all_fetched_channels if not isinstance(c, discord.CategoryChannel)]

        for category in sorted(categories, key=lambda x: x.position):
            cat_info = {
                "id": category.id,
                "name": category.name,
                "position": category.position,
                "overwrites": self.get_channel_overwrites(category),
                "channels": []
            }
            category_channels = [c for c in text_and_voice if c.category_id == category.id]
            for channel in sorted(category_channels, key=lambda x: x.position):
                chan_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "nsfw": channel.nsfw if isinstance(channel, discord.TextChannel) else False,
                    "topic": channel.topic if isinstance(channel, discord.TextChannel) else None,
                    "slowmode_delay": channel.slowmode_delay if isinstance(channel, discord.TextChannel) else 0,
                    "user_limit": channel.user_limit if isinstance(channel, discord.VoiceChannel) else 0,
                    "overwrites": self.get_channel_overwrites(channel)
                }
                cat_info["channels"].append(chan_info)
            backup_data["categories"].append(cat_info)

        for channel in text_and_voice:
            if channel.category_id is None:
                chan_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "nsfw": channel.nsfw if isinstance(channel, discord.TextChannel) else False,
                    "topic": channel.topic if isinstance(channel, discord.TextChannel) else None,
                    "overwrites": self.get_channel_overwrites(channel)
                }
                backup_data["orphaned_channels"].append(chan_info)

        try:
            for member in guild.members:
                if member.bot:
                    continue
                backup_data["members"].append({
                    "user_id": member.id,
                    "username": member.name,
                    "nickname": member.nick,
                    "roles": [role.id for role in member.roles if not role.is_default()]
                })
        except Exception:
            pass

        return backup_data

    # Main Backup Processor
    async def process_and_send_backup(self, guild: discord.Guild, reason="Scheduled", target_channel=None):
        try:
            if not target_channel:
                channel_id = self.get_backup_channel_id(guild.id)
                if not channel_id:
                    return False
                try:
                    target_channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
                except (discord.NotFound, discord.Forbidden):
                    return False

            backup_data = await self.generate_server_backup(guild)
            json_string = json.dumps(backup_data, indent=4, ensure_ascii=False)
            self.save_latest_backup_json(guild.id, json_string)

            file_data = io.BytesIO(json_string.encode('utf-8'))
            filename = f"backup_{guild.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            discord_file = discord.File(file_data, filename=filename)

            total_channels_saved = sum(len(cat["channels"]) for cat in backup_data["categories"]) + len(backup_data["orphaned_channels"])

            embed = discord.Embed(
                title=f"{EMOJIS['info']} Advanced Server Backup Processed",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            embed.description = f"{EMOJIS['arrow']} **Status:** Live API snapshot saved to local database.\n{EMOJIS['arrow']} **Reason:** {reason}"
            embed.add_field(name=f"{EMOJIS['dot_blue']} Server Name", value=guild.name, inline=True)
            embed.add_field(name=f"{EMOJIS['dot_yellow']} Saved Channels", value=f"Total: {total_channels_saved}", inline=True)
            embed.add_field(name=f"{EMOJIS['dot_orange']} Total Roles", value=str(len(backup_data["roles"])), inline=True)
            
            embed.set_footer(text="Starla Security System", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            if guild.icon: embed.set_thumbnail(url=guild.icon.url)

            await target_channel.send(embed=embed, file=discord_file)
            return True
        except Exception as e:
            print(f"Backup Error for {guild.name}: {e}")
            return False

    # Core Structural Server Restoration Engine (FIXED CHANNELS MAPPING TYPE SAFETY)
    async def execute_server_restoration(self, guild: discord.Guild, data: dict, status_msg):
        try:
            # 1. Guild Name Revert
            if "server_name" in data and guild.me.guild_permissions.manage_guild:
                await guild.edit(name=data["server_name"])

            # 2. Strict Type-Safe Channel Mapping Loop
            if guild.me.guild_permissions.manage_channels:
                live_channels = await guild.fetch_channels()
                
                nuked_channels = [c for c in live_channels if "nuked" in c.name.lower() or "starla" in c.name.lower()]
                if not nuked_channels:
                    nuked_channels = live_channels

                backup_categories = [cat for cat in data.get("categories", [])]
                backup_text_channels = []
                backup_voice_channels = []

                for cat in backup_categories:
                    for chan in cat.get("channels", []):
                        if "voice" in str(chan.get("type")).lower():
                            backup_voice_channels.append(chan)
                        else:
                            backup_text_channels.append(chan)

                for chan in data.get("orphaned_channels", []):
                    if "voice" in str(chan.get("type")).lower():
                        backup_voice_channels.append(chan)
                    else:
                        backup_text_channels.append(chan)

                cat_idx = 0
                text_idx = 0
                voice_idx = 0

                for channel in nuked_channels:
                    try:
                        if isinstance(channel, discord.CategoryChannel):
                            if cat_idx < len(backup_categories):
                                await channel.edit(name=backup_categories[cat_idx].get("name"))
                                cat_idx += 1

                        elif isinstance(channel, discord.VoiceChannel):
                            if voice_idx < len(backup_voice_channels):
                                await channel.edit(name=backup_voice_channels[voice_idx].get("name"))
                                voice_idx += 1

                        elif isinstance(channel, (discord.TextChannel, discord.StageChannel, discord.ForumChannel)):
                            if text_idx < len(backup_text_channels):
                                await channel.edit(name=backup_text_channels[text_idx].get("name"))
                                text_idx += 1

                        if guild.me.guild_permissions.manage_permissions:
                            await channel.set_permissions(guild.default_role, view_channel=True)
                    except Exception:
                        pass

            # 3. Restore Members Nicknames safely
            if guild.me.guild_permissions.manage_nicknames:
                for mem_data in data.get("members", []):
                    member = guild.get_member(mem_data.get("user_id"))
                    if member and member.id != guild.owner_id and guild.me.top_role > member.top_role:
                        try:
                            await member.edit(nick=mem_data.get("nickname"))
                        except Exception: pass

            await status_msg.edit(content=f"{EMOJIS['yes']} **Starla Core Engine:** Server structure successfully matched and fixed from file template configurations!")
        except Exception as e:
            await status_msg.edit(content=f"{EMOJIS['cross']} Rollback process fault: `{e}`")

    # ==========================================
    # ⚙️ SERVER RESTORE COMMAND (Prefix & Slash)
    # ==========================================
    @commands.command(name="restoreserver", aliases=["restore server", "restoresv"])
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

    # ==========================================
    # SET & CREATE CHANNELS
    # ==========================================
    @commands.command(name="setbackupchannel", aliases=["set server backup channel", "setbackup"])
    @commands.has_permissions(administrator=True)
    async def prefix_set_channel(self, ctx, channel: discord.TextChannel):
        self.set_backup_channel_id(ctx.guild.id, channel.id)
        await ctx.send(f"{EMOJIS['yes']} Backup channel set to {channel.mention} successfully!")

    @app_commands.command(name="set_server_backup_channel", description="Set an existing channel for automated backups.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.set_backup_channel_id(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"{EMOJIS['yes']} Backup channel set to {channel.mention} successfully!", ephemeral=True)

    @commands.command(name="createbackupchannel", aliases=["create server backup channel", "createbackup"])
    @commands.has_permissions(administrator=True)
    async def prefix_create_channel(self, ctx):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        new_channel = await ctx.guild.create_text_channel(name="svstarlabackup🌸", overwrites=overwrites)
        self.set_backup_channel_id(ctx.guild.id, new_channel.id)
        await ctx.send(f"{EMOJIS['mod']} Created and locked backup channel: {new_channel.mention}")

    @app_commands.command(name="create_server_backup_channel", description="Create a new private channel for backups.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_create_channel(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        new_channel = await ctx.guild.create_text_channel(name="svstarlabackup🌸", overwrites=overwrites)
        self.set_backup_channel_id(interaction.guild.id, new_channel.id)
        await interaction.followup.send(f"{EMOJIS['mod']} Created and locked backup channel: {new_channel.mention}", ephemeral=True)

    @commands.command(name="serverbackup", aliases=["server backup", "backup"])
    @commands.has_permissions(administrator=True)
    async def prefix_instant_backup(self, ctx):
        await ctx.send(f"{EMOJIS['dot_yellow']} Generating instant backup, please wait...")
        status = await self.process_and_send_backup(ctx.guild, reason=f"Manual Trigger by {ctx.author}", target_channel=ctx.channel)
        if not status:
            await ctx.send(f"{EMOJIS['cross']} Something went wrong while generating backup.")

    @app_commands.command(name="server_backup", description="Generates and sends an instant backup file in the current channel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_instant_backup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        status = await self.process_and_send_backup(interaction.guild, reason=f"Manual Slash Trigger by {interaction.user}", target_channel=interaction.channel)
        if status:
            await interaction.followup.send(f"{EMOJIS['yes']} Backup file generated and sent successfully!")
        else:
            await interaction.followup.send(f"{EMOJIS['cross']} Failed to generate backup.")

        # ==========================================
    # AUTOMATED TIMERS & LOOPS
    # ==========================================
    @tasks.loop(minutes=30.0)
    async def auto_backup(self):
        if self.auto_backup.current_loop > 0:
            for guild in self.bot.guilds:
                await self.process_and_send_backup(guild, reason="30-Min Auto Timer")

    @auto_backup.before_loop
    async def before_auto_backup(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot online! Starting startup backups...")
        await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=5))
        for guild in self.bot.guilds:
            await self.process_and_send_backup(guild, reason="Bot Restart / Redeploy")

async def setup(bot):
    await bot.add_cog(BackupModule(bot))
    
