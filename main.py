import discord
import os
import asyncio
import json
import logging
import urllib.request
import zipfile
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from discord.ext import commands, tasks
from discord import Streaming, app_commands

logging.basicConfig(level=logging.INFO)

# --- 🚀 HEALTH SERVER ---
def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Starla Operational")
        def log_message(self, format, *args): 
            return 
            
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), Handler)
        print(f"🌐 Health Server running on port {port}")
        server.serve_forever()
    except Exception as e: 
        print(f"⚠️ Health Server Error: {e}")

# --- ☢️ FFMPEG INSTALLER ---
def install_ffmpeg():
    if not os.path.exists("./ffmpeg"):
        print("📥 Downloading FFmpeg...")
        try:
            url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-linux-64.zip"
            urllib.request.urlretrieve(url, "ffmpeg.zip")
            with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.chmod("./ffmpeg", 0o755)
            print("✅ FFmpeg Installed successfully!")
            os.remove("ffmpeg.zip")
        except Exception as e: 
            print(f"❌ FFmpeg Error: {e}")

# --- ⚙️ DYNAMIC PREMIUM & GUILD PREFIX LOGIC ---
def get_prefix(bot, message):
    default_prefix = "!"
    
    # 1. Check if user is registered in the Premium database
    if hasattr(bot, 'db') and bot.db:
        premium_users = bot.db.get("premium.users", [])
        if message.author and message.author.id in premium_users:
            # Grants empty string prefix (No-Prefix) alongside server default
            if message.guild:
                guild_prefix = bot.db.get(f"prefix.{message.guild.id}", default_prefix)
                return [guild_prefix, ""]
            return [default_prefix, ""]

    # 2. Standard server prefix logic for non-premium users
    if message.guild and hasattr(bot, 'db') and bot.db:
        return bot.db.get(f"prefix.{message.guild.id}", default_prefix)
        
    return default_prefix

# --- 🤖 BOT CLASS ---
class Starla(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.dm_messages = True
        intents.message_content = True
        
        super().__init__(
            command_prefix=get_prefix, 
            intents=intents, 
            help_command=None,
            case_insensitive=True
        )
        self.db = None
        
        # --- 🎭 GLOBAL EMOJI REGISTRY WITH IDs ---
        self.emojis_dict = {
            "fire_light_blue": "<a:fire_light_blue:1431635464338538496>",
            "fire_purple": "<a:fire_purple:1431635390661525555>",
            "fire_red_pastel": "<a:fire_red_pastel:1431635439328038974>",
            "fire_white": "<a:fire_white:1431635384491577414>",
            "verified": "<a:verified:1434044320830459935>",
            "text_heart": "<:TextHeart:1438571558837817475>",
            "air_admin": "<:AIR_ADMIN:1433735851027857572>",
            "bd_sword": "<:bd_sword:1495476833720729836>",
            "devil_crown": "<:irl_read_devil_crown:1433507516712620093>",
            "mor": "<:mor:1433524239167783124>",
            "spider_cross": "<a:spider_cross:1494181311525687347>",
            "spider_red_dot": "<a:spider_red_dot:1494179666133516411>"
        }
    
    async def setup_hook(self):
        threading.Thread(target=run_health_server, daemon=True).start()
        
        os.makedirs("data", exist_ok=True)
        db_path = "data/database.json"
        if not os.path.exists(db_path):
            with open(db_path, "w") as f: 
                json.dump({}, f)
        
        install_ffmpeg()
        
        from database import Database
        self.db = Database(db_path)
        print("💾 Database connected successfully.")
        
        # Internal Cog Registrations
        await self.add_cog(CoreCommands(self))
        await self.add_cog(PremiumSystem(self))
        
        # External Extensions Load
        for f in os.listdir('./'):
            if f.endswith('.py') and f not in ['main.py', 'database.py']:
                try:
                    await self.load_extension(f[:-3])
                    print(f"✅ Loaded extension: {f}")
                except Exception as e:
                    print(f"❌ Failed to load extension {f}: {e}")

    async def on_ready(self):
        print(f"---")
        print(f"Logged in as {self.user}")
        print(f"Bot is active in {len(self.guilds)} servers")
        print(f"---")
        
        for guild in self.guilds:
            print(f"{guild.name} ({guild.id})")
        print(f"---")
        
        if not self.update_status.is_running():
            self.update_status.start()
        
        try:
            synced = await self.tree.sync()
            print(f"✨ Synced {len(synced)} Hybrid Application Commands Globally")
        except Exception as e:
            print(f"⚠️ Sync Error: {e}")

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"Starla | {len(self.guilds)} Connected Networks"
        await self.change_presence(activity=Streaming(name=status_text, url="https://twitch.tv/starla_bot"))

    # --- 💬 MENTION HANDLER ---
    async def on_message(self, message):
        if message.author.bot: 
            return

        bot_mentioned = self.user in message.mentions
        
        if bot_mentioned:
            content = message.content.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "")
            content = content.lower().strip()
            
            v = self.emojis_dict["verified"]
            crown = self.emojis_dict["devil_crown"]
            heart = self.emojis_dict["text_heart"]
            admin = self.emojis_dict["air_admin"]
            mor = self.emojis_dict["mor"]
            
            if "harsh" in content:
                await message.reply(f"{crown} **Harsh** is the authorized software architect and core platform systems developer for Starla.")
                return
                
            elif any(word in content for word in ["owner", "creator", "maker"]):
                await message.reply(f"{admin} This enterprise system infrastructure is strictly managed, deployed, and owned by **Harsh**.")
                return
                
            elif content == "":
                prefix_data = self.command_prefix(self, message)
                current_prefix = prefix_data[0] if isinstance(prefix_data, list) else prefix_data
                await message.reply(f"{v} Greetings. I am **Starla**, an automated application network optimized by **Harsh**. Your configuration prefix is `{current_prefix}`. Use `{current_prefix}help` to access service modules. {heart} {mor}")
                return

        await self.process_commands(message)

# --- ⚙️ HYBRID ROUTING COG INTEGRATION ---
class CoreCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 🏓 HYBRID PING COMMAND ---
    @commands.hybrid_command(name="ping", description="Checks the application system responsiveness metrics.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ping(self, ctx):
        dot = self.bot.emojis_dict["spider_red_dot"]
        cross = self.bot.emojis_dict["spider_cross"]
        sword = self.bot.emojis_dict["bd_sword"]
        f_blue = self.bot.emojis_dict["fire_light_blue"]
        f_purple = self.bot.emojis_dict["fire_purple"]
        
        await ctx.defer()
        
        start_time = asyncio.get_event_loop().time()
        msg = await ctx.send(f"{dot} *Executing asynchronous system diagnostic handshakes...*")
        end_time = asyncio.get_event_loop().time()
        
        rest_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title=f"{cross} Core Diagnostic Matrix Status",
            color=discord.Color.from_rgb(47, 49, 54),
            description="System nodes and execution clusters operating inside safe operational bounds."
        )
        embed.add_field(name=f"{f_blue} WebSocket Protocol", value=f"```ansi\n\u001b[2;34m{websocket_latency}ms\u001b[0m\n```", inline=True)
        embed.add_field(name=f"{f_purple} Gateway REST API", value=f"```ansi\n\u001b[2;35m{rest_latency}ms\u001b[0m\n```", inline=True)
        
        avatar_url = ctx.author.display_avatar.url if ctx.author else None
        embed.set_footer(text="Starla Secure Framework Core Execution Engine", icon_url=avatar_url)
        
        await msg.edit(content=f"{sword} **System Analytics Fetched:**", embed=embed)

    # --- 📑 HYBRID SERVER LIST COMMAND ---
    @commands.hybrid_command(name="serverlist", description="Owner Only: Displays connected cluster network guild items.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def serverlist(self, ctx):
        admin = self.bot.emojis_dict["air_admin"]
        sword = self.bot.emojis_dict["bd_sword"]
        f_white = self.bot.emojis_dict["fire_white"]
        f_red = self.bot.emojis_dict["fire_red_pastel"]

        await ctx.defer()

        if not self.bot.guilds:
            await ctx.send(f"{f_red} System alert: This automation matrix is not assigned to any virtual network frameworks.")
            return

        msg_list = []
        current_msg = f"{admin} **Connected Network Guild Infrastructures ({len(self.bot.guilds)}):**\n\n"
        
        for i, guild in enumerate(self.bot.guilds, 1):
            line = f"{sword} `{i:02d}.` **{guild.name}** (ID: `{guild.id}`) │ Structural Node Count: `{guild.member_count}` {f_white}\n"
            if len(current_msg) + len(line) > 1950:
                msg_list.append(current_msg)
                current_msg = ""
            current_msg += line
            
        if current_msg:
            msg_list.append(current_msg)

        for page in msg_list:
            await ctx.send(page)

    @serverlist.error
    async def serverlist_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            f_red = self.bot.emojis_dict["fire_red_pastel"]
            await ctx.send(f"{f_red} **Access Restriction Fault:** The requested action requires elevation privileges matching the system root developer.")

    # --- 🔗 HYBRID GENERATE INVITE LINK COMMAND ---
    @commands.hybrid_command(name="invitelink", description="Owner Only: Generates localized temporary access tokens using a guild ID string.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def invitelink(self, ctx, guild_id: str):
        f_red = self.bot.emojis_dict["fire_red_pastel"]
        f_blue = self.bot.emojis_dict["fire_light_blue"]
        v = self.bot.emojis_dict["verified"]
        sword = self.bot.emojis_dict["bd_sword"]
        
        await ctx.defer()
        
        try:
            parsed_id = int(guild_id)
        except ValueError:
            f_purple = self.bot.emojis_dict["fire_purple"]
            await ctx.send(f"{f_purple} **Parsing Exception:** Target parameter must represent a clean numeric snowflake ID layout string.")
            return

        guild = self.bot.get_guild(parsed_id)
        if not guild:
            await ctx.send(f"{f_red} **System Error:** Invalid structural node parameter. No guild found matching ID `{guild_id}`.")
            return

        target_channel = None
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                target_channel = channel
                break
                
        if not target_channel:
            await ctx.send(f"{f_red} **Access Permission Denied:** Missing core permission protocols (`CREATE_INSTANT_INVITE`) inside structural network node **{guild.name}**.")
            return

        try:
            invite = await target_channel.create_invite(max_age=300, max_uses=1, unique=True, reason="Owner extraction protocol triggered.")
            await ctx.send(f"{v} **Invite Authentication Token Generated Successfully:**\n{sword} **Server:** {guild.name}\n{f_blue} **Link:** {invite.url}")
        except Exception as e:
            await ctx.send(f"{f_red} **Execution Fault:** An error occurred generating the gateway token: `{str(e)}`")

    @invitelink.error
    async def invitelink_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            f_red = self.bot.emojis_dict["fire_red_pastel"]
            await ctx.send(f"{f_red} **Access Restriction Fault:** The requested action requires elevation privileges matching the system root developer.")
        elif isinstance(error, commands.MissingRequiredArgument):
            f_purple = self.bot.emojis_dict["fire_purple"]
            await ctx.send(f"{f_purple} **Argument Missing:** Command requires a specific target guild ID parameter configuration.")

# --- 💎 PREMIUM & NO-PREFIX SYSTEM COG ---
class PremiumSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_premium_users(self):
        if self.bot.db:
            return self.bot.db.get("premium.users", [])
        return []

    def save_premium_users(self, users_list):
        if self.bot.db:
            self.bot.db.set("premium.users", users_list)

    @commands.hybrid_group(name="premium", description="Owner Only: Administrative hub for managing Premium No-Prefix privileges.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def premium(self, ctx):
        if ctx.invoked_subcommand is None:
            f_purple = self.bot.emojis_dict.get("fire_purple", "⚠️")
            await ctx.send(f"{f_purple} **Usage:** `!premium add <user>` | `!premium remove <user>` | `!premium list`")

    @premium.command(name="add", description="Owner Only: Grants premium no-prefix execution access to a user.")
    @app_commands.describe(user="The target user to authorize.")
    @commands.is_owner()
    async def add(self, ctx, user: discord.User):
        v = self.bot.emojis_dict.get("verified", "✅")
        sword = self.bot.emojis_dict.get("bd_sword", "🛡️")
        f_purple = self.bot.emojis_dict.get("fire_purple", "⚠️")
        
        users = self.get_premium_users()
        if user.id in users:
            return await ctx.send(f"{f_purple} User `{user.name}` is already registered in the Premium No-Prefix database.")

        users.append(user.id)
        self.save_premium_users(users)
        await ctx.send(f"{v} **Premium Activated:** `{user.name}` can now execute commands without any prefix. {sword}")

    @premium.command(name="remove", description="Owner Only: Revokes premium no-prefix access from a user.")
    @app_commands.describe(user="The target user to deauthorize.")
    @commands.is_owner()
    async def remove(self, ctx, user: discord.User):
        f_red = self.bot.emojis_dict.get("fire_red_pastel", "❌")
        dot = self.bot.emojis_dict.get("spider_red_dot", "⚠️")
        
        users = self.get_premium_users()
        if user.id not in users:
            return await ctx.send(f"{dot} User `{user.name}` does not have active Premium status.")

        users.remove(user.id)
        self.save_premium_users(users)
        await ctx.send(f"{f_red} **Premium Revoked:** No-Prefix mode disabled for user `{user.name}`.")

    @premium.command(name="list", description="Owner Only: Lists all current Premium No-Prefix users.")
    @commands.is_owner()
    async def list_users(self, ctx):
        admin = self.bot.emojis_dict.get("air_admin", "🛡️")
        f_white = self.bot.emojis_dict.get("fire_white", "🔹")
        
        users = self.get_premium_users()
        if not users:
            return await ctx.send("No users are currently registered in the Premium database.")

        msg = f"{admin} **Registered Premium Users ({len(users)}):**\n\n"
        for uid in users:
            u = self.bot.get_user(uid)
            uname = u.name if u else f"ID: {uid}"
            msg += f"{f_white} • **{uname}** (`{uid}`)\n"

        await ctx.send(msg)

    @premium.error
    @add.error
    @remove.error
    @list_users.error
    async def premium_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            f_red = self.bot.emojis_dict.get("fire_red_pastel", "❌")
            await ctx.send(f"{f_red} **Access Restriction Fault:** The requested action requires elevation privileges matching the system root developer.")

if __name__ == "__main__":
    bot = Starla()
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Fatal Error: Environment variable configuration token missing.")
        
