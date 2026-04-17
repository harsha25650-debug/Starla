import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import zipfile
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from discord.ext import commands, tasks
from discord import Streaming # 👈 Streaming status ke liye zaroori hai

logging.basicConfig(level=logging.INFO)

# --- 🚀 HEALTH SERVER ---
def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"NovaX Alive")
        def log_message(self, format, *args): return
    
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), Handler)
        server.serve_forever()
    except: pass

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
            print("✅ FFmpeg Installed!")
            os.remove("ffmpeg.zip")
        except Exception as e: print(f"❌ FFmpeg Error: {e}")

# --- 🤖 BOT CLASS ---
class NovaX(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", 
            intents=discord.Intents.all(), 
            help_command=None
        )
    
    async def setup_hook(self):
        # 1. Background Health Server
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # 2. Setup Folders
        os.makedirs("data", exist_ok=True)
        db_path = "data/database.json"
        if not os.path.exists(db_path):
            with open(db_path, "w") as f:
                json.dump({}, f)
        
        # 3. FFmpeg & Database
        install_ffmpeg()
        from database import Database
        self.db = Database(db_path)
        
        # 4. Load Extensions
        for f in os.listdir('./'):
            if f.endswith('.py') and f not in ['main.py', 'database.py']:
                try:
                    await self.load_extension(f[:-3])
                    print(f"✅ Loaded: {f}")
                except Exception as e:
                    print(f"❌ Failed to load {f}: {e}")

    # --- 🔄 AUTO STATUS LOOP (Purple Badge Fix) ---
    @tasks.loop(minutes=5)
    async def update_status(self):
        if self.is_ready():
            # Purple Badge ke liye Streaming activity zaroori hai
            status_text = f"NovaX Music | {len(self.guilds)} Servers"
            await self.change_presence(
                activity=Streaming(
                    name=status_text, 
                    url="https://www.twitch.tv/novax_music" # Twitch URL se purple badge aata hai
                )
            )

    async def on_ready(self):
        print(f"---")
        print(f"✅ {self.user} is Online | Version 1.10")
        print(f"---")
        
        # Status loop start karna
        if not self.update_status.is_running():
            self.update_status.start()
            
        # Slash Commands Sync
        try:
            await self.tree.sync()
            print("✅ Slash commands synced!")
        except Exception as e:
            print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    bot = NovaX()
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ No TOKEN found!")
