import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import zipfile  # Python's internal zip handler
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
            self.wfile.write(b"NovaX is Alive!")
        def log_message(self, format, *args): return # Keep logs clean

    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), Handler)
        print(f"🌍 Health server active on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server error: {e}")

# --- ☢️ FFmpeg ZIP Installer (Bypasses Tar/XZ Errors) ---
def install_ffmpeg():
    local_ffmpeg = "./ffmpeg"
    if not os.path.exists(local_ffmpeg):
        print("📥 FFmpeg not found, downloading ZIP build...")
        try:
            # Using ffbinaries ZIP build (Most compatible with Railway)
            url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-linux-64.zip"
            zip_name = "ffmpeg.zip"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(zip_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # Extract using Python's internal zip library
            with zipfile.ZipFile(zip_name, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            if os.path.exists("./ffmpeg"):
                os.chmod("./ffmpeg", 0o755)
                print("✅ FFmpeg (ZIP) installed successfully!")
            
            if os.path.exists(zip_name): os.remove(zip_name)
                
        except Exception as e:
            print(f"❌ Failed to install FFmpeg: {e}")
    else:
        print("🔍 FFmpeg is ready.")

# --- BOT CLASS SETUP ---
class NovaX(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=lambda bot, msg: bot.db.get(f"prefix.{msg.guild.id}", "!") if msg.guild else "!",
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.db = None

    async def setup_hook(self):
        # 1. Start Health Server
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # 2. Install FFmpeg
        install_ffmpeg()
        
        # 3. Database Init
        os.makedirs("./data", exist_ok=True)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f: json.dump({}, f)
        self.db = Database("data/database.json")
        
        # 4. Load Extensions
        for filename in os.listdir('./'):
            if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
                try: 
                    await self.load_extension(filename[:-3])
                    print(f"✅ Loaded: {filename}")
                except Exception as e: 
                    print(f'❌ Failed {filename}: {e}')

    async def on_ready(self):
        print(f"---")
        print(f"✅ NovaX v1.10 Online | {self.user}")
        print(f"---")
        if not self.update_status.is_running(): self.update_status.start()
        await self.tree.sync()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"NovaX | {len(self.guilds)} Servers"
        await self.change_presence(activity=discord.Streaming(name=status_text, url="https://twitch.tv/novax_bot"))

if __name__ == "__main__":
    bot = NovaX()
    bot.run(os.getenv("TOKEN"))
