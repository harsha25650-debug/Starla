import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import zipfile
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from discord.ext import commands, tasks
from discord import Streaming

logging.basicConfig(level=logging.INFO)

# --- 🚀 HEALTH SERVER ---
def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Starla Alive")
        def log_message(self, format, *args): 
            return # Keeps terminal logs clean
            
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

# --- ⚙️ DYNAMIC PREFIX LOGIC ---
def get_prefix(bot, message):
    if not message.guild:
        return "!"
    if hasattr(bot, 'db') and bot.db:
        return bot.db.get(f"prefix.{message.guild.id}", "!")
    return "!"

# --- 🤖 BOT CLASS ---
class Starla(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
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
        
        for f in os.listdir('./'):
            if f.endswith('.py') and f not in ['main.py', 'database.py']:
                try:
                    await self.load_extension(f[:-3])
                    print(f"✅ Loaded extension: {f}")
                except Exception as e:
                    print(f"❌ Failed to load extension {f}: {e}")

    async def on_ready(self):
        v = self.emojis_dict["verified"]
        dot = self.emojis_dict["spider_red_dot"]
        
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
            print(f"✨ Synced {len(synced)} Slash Commands")
        except Exception as e:
            print(f"⚠️ Sync Error: {e}")

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"Starla | {len(self.guilds)} Connected Networks"
        await self.change_presence(activity=Streaming(name=status_text, url="https://twitch.tv/starla_bot"))

    # --- 💬 PROFESSIONAL MENTION HANDLER ---
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
                current_prefix = self.command_prefix(self, message)
                await message.reply(f"{v} Greetings. I am **Starla**, an automated application network optimized by **Harsh**. Your guild prefix is configuration `{current_prefix}`. Use `{current_prefix}help` to access service modules. {heart} {mor}")
                return

        await self.process_commands(message)

if __name__ == "__main__":
    bot = Starla()
    
    # --- 🏓 ADVANCED PING COMMAND ---
    @bot.command(name="ping")
    async def ping(ctx):
        dot = bot.emojis_dict["spider_red_dot"]
        cross = bot.emojis_dict["spider_cross"]
        sword = bot.emojis_dict["bd_sword"]
        f_blue = bot.emojis_dict["fire_light_blue"]
        f_purple = bot.emojis_dict["fire_purple"]
        
        start_time = asyncio.get_event_loop().time()
        msg = await ctx.send(f"{dot} *Executing asynchronous system diagnostic handshakes...*")
        end_time = asyncio.get_event_loop().time()
        
        rest_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(bot.latency * 1000)
        
        embed = discord.Embed(
            title=f"{cross} Core Diagnostic Matrix Status",
            color=discord.Color.from_rgb(47, 49, 54),
            description="System nodes and execution clusters operating inside safe operational bounds."
        )
        embed.add_field(name=f"{f_blue} WebSocket Protocol", value=f"```ansi\n\u001b[2;34m{websocket_latency}ms\u001b[0m\n```", inline=True)
        embed.add_field(name=f"{f_purple} Gateway REST API", value=f"```ansi\n\u001b[2;35m{rest_latency}ms\u001b[0m\n```", inline=True)
        embed.set_footer(text="Starla Secure Framework Core Execution Engine", icon_url=ctx.author.display_avatar.url)
        
        await msg.edit(content=f"{sword} **System Analytics Fetched:**", embed=embed)

    # --- 📑 OWNER ONLY: SERVER LIST COMMAND ---
    @bot.command(name="serverlist")
    @commands.is_owner()
    async def serverlist(ctx):
        admin = bot.emojis_dict["air_admin"]
        sword = bot.emojis_dict["bd_sword"]
        f_white = bot.emojis_dict["fire_white"]
        f_red = bot.emojis_dict["fire_red_pastel"]

        if not bot.guilds:
            await ctx.send(f"{f_red} System alert: This automation matrix is not assigned to any virtual network frameworks.")
            return

        msg_list = []
        current_msg = f"{admin} **Connected Network Guild Infrastructures ({len(bot.guilds)}):**\n\n"
        
        for i, guild in enumerate(bot.guilds, 1):
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
    async def serverlist_error(ctx, error):
        if isinstance(error, commands.NotOwner):
            f_red = bot.emojis_dict["fire_red_pastel"]
            await ctx.send(f"{f_red} **Access Restriction Fault:** The requested action requires elevation privileges matching the system root developer.")

    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Fatal Error: Environment variable configuration token missing.")
            
