import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import io
import datetime
import sqlite3

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

class BackupCoreModule(commands.Cog):
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

    # --- AUTOMATED BACKGROUND LOOP (Interval changed to 30 Minutes) ---
    @tasks.loop(minutes=30)
    async def auto_backup(self):
        for guild in self.bot.guilds:
            await self.process_and_send_backup(guild, reason="Automated 30-Min Snapshot Cycle")

    @auto_backup.before_loop
    async def before_auto_backup(self):
        await self.bot.wait_until_ready()

    # ==========================================
    # 📝 MANUAL GENERATION COMMANDS (serverbackup)
    # ==========================================
    @commands.command(name="serverbackup", aliases=["makebackup", "createbackup"])
    @commands.has_permissions(administrator=True)
    async def prefix_server_backup(self, ctx):
        status_msg = await ctx.send(f"{EMOJIS['dot_yellow']} Processing secure server structure analysis...")
        status = await self.process_and_send_backup(ctx.guild, reason=f"Manually Triggered by {ctx.author}", target_channel=ctx.channel)
        if status:
            await status_msg.delete()
        else:
            await status_msg.edit(content=f"{EMOJIS['cross']} Secure extraction routine failed. Check bot execution permissions.")

    @app_commands.command(name="server_backup", description="Generate a real-time layout snapshot and return the compiled backup JSON file.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_server_backup(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Generator processes file directly to specific target
        backup_data = await self.generate_server_backup(interaction.guild)
        json_string = json.dumps(backup_data, indent=4, ensure_ascii=False)
        self.save_latest_backup_json(interaction.guild.id, json_string)

        file_data = io.BytesIO(json_string.encode('utf-8'))
        filename = f"backup_{interaction.guild.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        discord_file = discord.File(file_data, filename=filename)

        total_channels_saved = sum(len(cat["channels"]) for cat in backup_data["categories"]) + len(backup_data["orphaned_channels"])

        embed = discord.Embed(
            title=f"{EMOJIS['info']} On-Demand Layout Snapshot Delivered",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.description = f"{EMOJIS['arrow']} **Status:** Secure manifest packet successfully generated."
        embed.add_field(name=f"{EMOJIS['dot_blue']} Server", value=interaction.guild.name, inline=True)
        embed.add_field(name=f"{EMOJIS['dot_yellow']} Channels", value=f"Total: {total_channels_saved}", inline=True)
        embed.add_field(name=f"{EMOJIS['dot_orange']} Roles", value=str(len(backup_data["roles"])), inline=True)
        
        embed.set_footer(text="Starla Security System", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)

        await interaction.followup.send(embed=embed, file=discord_file)

    # ==========================================
    # SET & CREATE CHANNELS
    # ==========================================
    @commands.command(name="setbackupchannel", aliases=["setbackup"])
    @commands.has_permissions(administrator=True)
    async def prefix_set_channel(self, ctx, channel: discord.TextChannel):
        self.set_backup_channel_id(ctx.guild.id, channel.id)
        await ctx.send(f"{EMOJIS['yes']} Backup channel set to {channel.mention} successfully!")

    @app_commands.command(name="set_server_backup_channel", description="Set an existing channel for automated backups.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.set_backup_channel_id(interaction.guild.id, channel.id)
        await interaction.response.send_message(f"{EMOJIS['yes']} Backup channel set to {channel.mention} successfully!", ephemeral=True)

    @commands.command(name="createbackupchannel", aliases=["setupbackup"])
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
        new_channel = await interaction.guild.create_text_channel(name="svstarlabackup🌸", overwrites=overwrites)
        self.set_backup_channel_id(interaction.guild.id, new_channel.id)
        await interaction.followup.send(f"{EMOJIS['mod']} Created and locked backup channel: {new_channel.mention}")

async def setup(bot):
    await bot.add_cog(BackupCoreModule(bot))
            
