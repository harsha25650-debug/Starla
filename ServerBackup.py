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

    # Helper: Channel ki customized permission overwrites extract karne ke liye
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

    # Core Backup Generator Function (MAX ASSETS INCLUDED)
    def generate_server_backup(self, guild: discord.Guild):
        backup_data = {
            "server_name": guild.name,
            "server_id": guild.id,
            "icon_url": str(guild.icon.url) if guild.icon else None,
            "banner_url": str(guild.banner.url) if guild.banner else None,
            "verification_level": str(guild.verification_level),
            "explicit_content_filter": str(guild.explicit_content_filter),
            "default_notifications": str(guild.default_notifications),
            "backup_time": str(datetime.datetime.now()),
            "roles": [],
            "categories": [],
            "orphaned_channels": [], # Jo channels kisi category ke andar nahi hain
            "members": [] # Nicknames aur roles data
        }

        # 1. ROLES SYSTEM
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

        # 2. CATEGORIES & INSIDE CHANNELS
        for category in guild.categories:
            cat_info = {
                "id": category.id,
                "name": category.name,
                "position": category.position,
                "overwrites": self.get_channel_overwrites(category),
                "channels": []
            }
            for channel in category.channels:
                chan_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "nsfw": channel.nsfw if isinstance(channel, discord.TextChannel) else False,
                    "topic": channel.topic if isinstance(channel, discord.TextChannel) else None,
                    "slowmode_delay": channel.slowmode_delay if isinstance(channel, discord.TextChannel) else 0,
                    "user_limit": channel.user_limit if isinstance(channel, discord.VoiceChannel) else 0,
                    "bitrate": channel.bitrate if isinstance(channel, discord.VoiceChannel) else 64000,
                    "overwrites": self.get_channel_overwrites(channel)
                }
                cat_info["channels"].append(chan_info)
            backup_data["categories"].append(cat_info)

        # 3. ORPHANED CHANNELS (Bina category wale saare channels)
        for channel in guild.channels:
            if channel.category is None and not isinstance(channel, discord.CategoryChannel):
                chan_info = {
                    "id": channel.id,
                    "name": channel.name,
                    "type": str(channel.type),
                    "position": channel.position,
                    "nsfw": channel.nsfw if isinstance(channel, discord.TextChannel) else False,
                    "topic": channel.topic if isinstance(channel, discord.TextChannel) else None,
                    "slowmode_delay": channel.slowmode_delay if isinstance(channel, discord.TextChannel) else 0,
                    "overwrites": self.get_channel_overwrites(channel)
                }
                backup_data["orphaned_channels"].append(chan_info)

        # 4. ALL MEMBERS DETAILS (NICKS & ROLES MAP)
        for member in guild.members:
            if member.bot:
                continue # Bots ko chhod kar
            backup_data["members"].append({
                "user_id": member.id,
                "username": member.name,
                "nickname": member.nick, # Member ka custom nickname save karega
                "roles": [role.id for role in member.roles if not role.is_default()]
            })

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

            backup_data = self.generate_server_backup(guild)
            json_string = json.dumps(backup_data, indent=4, ensure_ascii=False)
            file_data = io.BytesIO(json_string.encode('utf-8'))
            filename = f"backup_{guild.id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            discord_file = discord.File(file_data, filename=filename)

            embed = discord.Embed(
                title=f"{EMOJIS['info']} Advanced Server Backup Processed",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            embed.description = f"{EMOJIS['arrow']} **Status:** Full infrastructure database snapshot compiled.\n{EMOJIS['arrow']} **Reason:** {reason}"
            
            embed.add_field(name=f"{EMOJIS['dot_blue']} Server Name", value=guild.name, inline=True)
            embed.add_field(name=f"{EMOJIS['dot_yellow']} Categories & Channels", value=f"Cats: {len(backup_data['categories'])}\nOrphans: {len(backup_data['orphaned_channels'])}", inline=True)
            embed.add_field(name=f"{EMOJIS['dot_orange']} Total Roles", value=str(len(backup_data["roles"])), inline=True)
            embed.add_field(name=f"{EMOJIS['dot_pink']} Saved User Nodes", value=f"{len(backup_data['members'])} Members", inline=True)
            
            embed.set_footer(text="Starla Security System", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)

            await target_channel.send(embed=embed, file=discord_file)
            return True
        except Exception as e:
            print(f"Backup Error for {guild.name}: {e}")
            return False

    # ==========================================
    # 1. SET BACKUP CHANNEL (Prefix & Slash)
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

    # ==========================================
    # 2. CREATE BACKUP CHANNEL (Prefix & Slash)
    # ==========================================
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
        new_channel = await interaction.guild.create_text_channel(name="svstarlabackup🌸", overwrites=overwrites)
        self.set_backup_channel_id(interaction.guild.id, new_channel.id)
        await interaction.followup.send(f"{EMOJIS['mod']} Created and locked backup channel: {new_channel.mention}", ephemeral=True)

    # ==========================================
    # 3. INSTANT BACKUP COMMAND (Prefix & Slash)
    # ==========================================
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
        
