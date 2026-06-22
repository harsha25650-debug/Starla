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
        print(f"---")
        print(f"✅ {self.user.name} is Online & Fully Overloaded! 💞")
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
        status_text = f"Starla Cutie 🎀 | {len(self.guilds)} Servers"
        await self.change_presence(activity=Streaming(name=status_text, url="https://twitch.tv/starla_bot"))

    # --- 💬 CLEAN MENTION HANDLER ---
    async def on_message(self, message):
        if message.author.bot: 
            return

        bot_mentioned = self.user in message.mentions
        
        if bot_mentioned:
            content = message.content.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "")
            content = content.lower().strip()
            
            # 1️⃣ Who is Harsh?
            if "harsh" in content:
                await message.reply("**Harsh** is my boss, developer, and the absolute mastermind behind Starla! 😎👑")
                return
                
            # 2️⃣ Owner / Creator Info
            elif any(word in content for word in ["owner", "creator", "banaya", "maker"]):
                await message.reply("My heart and full control belong entirely to my creator, **Harsh**! 💖")
                return
                
            # 3️⃣ Just a plain @mention with no specific keywords (Intro Fallback)
            elif content == "":
                current_prefix = self.command_prefix(self, message)
                await message.reply(f"Hello! I am **Starla** 🎀, a powerful and cute community bot built by **Harsh**! My prefix here is `{current_prefix}`. Type `{current_prefix}help` to view my commands! ✨")
                return

        await self.process_commands(message)

if __name__ == "__main__":
    bot = Starla()
    
    @bot.command(name="ping")
    async def ping(ctx):
        loading_emoji = "<a:spider_red_dot:1494179666133516411>"
        
        start_time = asyncio.get_event_loop().time()
        msg = await ctx.send(f"{loading_emoji} *Calculating network response...*")
        end_time = asyncio.get_event_loop().time()
        
        rest_latency = round((end_time - start_time) * 1000)
        websocket_latency = round(bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=discord.Color.red()
        )
        embed.add_field(name="🌐 WebSocket Latency", value=f"`{websocket_latency}ms`", inline=True)
        embed.add_field(name="⚡ REST API Latency", value=f"`{rest_latency}ms`", inline=True)
        embed.set_footer(text="Starla • Performance Stable")
        
        await msg.edit(content=None, embed=embed)

    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Error: TOKEN environment variable nahi mila!")
                    
