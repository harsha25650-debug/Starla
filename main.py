import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import tarfile
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming
from database import Database

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)

# --- 🚀 HEALTH CHECK BYPASS (Railway "Stopping Container" Fix) ---
def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Alive!")

    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), Handler)
    server.serve_forever()

# --- ☢️ DIRECT FFMPEG INSTALLER ---
def install_ffmpeg():
    local_ffmpeg = "./ffmpeg"
    if not os.path.exists(local_ffmpeg):
        print("📥 FFmpeg not found, downloading direct build...")
        try:
            # Direct link to a stable static build
            url = "https://github.com/eugeneware/ffmpeg-static/releases/download/b4.4/linux-x64"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open("ffmpeg", 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            os.chmod("./ffmpeg", 0o755)
            print("✅ FFmpeg (Direct Binary) installed successfully!")
                
        except Exception as e:
            print(f"❌ Failed to install FFmpeg: {e}")
    else:
        print("🔍 FFmpeg is ready.")

# --- PREFIX LOGIC ---
def get_prefix(bot, message):
    if not message.guild: return "!"
    return bot.db.get(f"prefix.{message.guild.id}", "!")

# --- BOT CLASS SETUP ---
class NovaX(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix=get_prefix, intents=intents, help_command=None)
        self.db = None

    async def setup_hook(self):
        # 1. Start Health Server in background
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # 2. Install FFmpeg
        install_ffmpeg()
        
        os.makedirs("./data", exist_ok=True)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f: json.dump({}, f)
        
        self.db = Database("data/database.json")
        await self.load_extensions()

    async def load_extensions(self):
        for filename in os.listdir('./'):
            if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
                try: await self.load_extension(f'{filename[:-3]}')
                except Exception as e: print(f'❌ Failed {filename}: {e}')

    async def on_ready(self):
        print(f"✅ NovaX v1.10 Online | {self.user}")
        if not self.update_status.is_running(): self.update_status.start()
        await self.tree.sync()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"NovaX v1.10 | {len(self.guilds)} Servers"
        await self.change_presence(activity=discord.Streaming(name=status_text, url="https://twitch.tv/novax_bot"))

# --- RUNNING THE BOT ---
async def run_bot():
    bot = NovaX()
    token = os.getenv("TOKEN")
    async with bot: await bot.start(token)

if __name__ == "__main__":
    asyncio.run(run_bot())
