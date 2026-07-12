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
    
    if not message.author:
        return default_prefix

    # 1. ROOT OVERRIDE: Owner always bypasses prefix constraints (Always Premium/No-Prefix)
    # Using bot.owner_id if loaded, or checks is_owner asynchronously (fallback via application registry checks)
    is_root_owner = False
    if bot.owner_id and message.author.id == bot.owner_id:
        is_root_owner = True
    elif bot.owner_ids and message.author.id in bot.owner_ids:
        is_root_owner = True

    # 2. Check Premium Database status for standard user accounts
    is_premium_user = False
    if hasattr(bot, 'db') and bot.db:
        premium_users = bot.db.get("premium.users", [])
        if message.author.id in premium_users:
            is_premium_user = True

    # 3. Apply Empty Token Prefix mapping if either condition is met
    if is_root_owner or is_premium_user:
        if message.guild:
            guild_prefix = bot.db.get(f"prefix.{message.guild.id}", default_prefix)
            return [guild_prefix, ""]
        return [default_prefix, ""]

    # 4. Standard server prefix tracking routing maps
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
        # Force cache owner ids array data into internal memory profile definitions
        if not self.owner_id and not self.owner_ids:
            try:
                app_info = await self.application_info()
                if app_info.team:
                    self.owner_ids = {m.id for m in app_info.team.members}
                else:
                    self.owner_id = app_info.owner.id
            except Exception as e:
                print(f"⚠️ App Info Fetch Error: {e}")

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
        embed.add_field(name=f"{f_purple} Gateway REST API", value=f"```ansi\n\u001b[2;35m{rest_latency}ms\u001b[0m\n
        
