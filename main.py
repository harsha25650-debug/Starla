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
        def log_message(self, format, *args):
            return # Silent logs to keep it clean

    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(('0.0.0.0', port), Handler)
        print(f"🌍 Health server running on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server error: {e}")

# --- ☢️ STABLE FFMPEG INSTALLER (Fix for Code -11 & Path Errors) ---
def install_ffmpeg():
    local_ffmpeg = "./ffmpeg"
    if not os.path.exists(local_ffmpeg):
        print("📥 FFmpeg not found, downloading stable master build...")
        try:
            # Code -11 fix ke liye ye build sabse stable hai Linux containers ke liye
            url = "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz"
            archive_name = "ffmpeg.tar.xz"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(archive_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # Extract using system tar (Railway containers usually have this)
            subprocess.run(f"tar -xf {archive_name}", shell=True)
            
            # Binary dhoond kar main folder mein move karna
            found = False
            for root, dirs, files in os.walk("."):
                if "ffmpeg" in files and "bin" in root:
                    ffmpeg_src = os.path.join(root, "ffmpeg")
                    shutil.move(ffmpeg_src, "./ffmpeg")
                    found = True
                    break
            
            if found:
                os.chmod("./ffmpeg", 0o755)
                print("✅ Stable FFmpeg installed successfully!")
            
            # Cleanup
            if os.path.exists(archive_name): os.remove(archive_name)
            for item in os.listdir("."):
                if os.path.isdir(item) and "ffmpeg-master" in item:
                    shutil.rmtree(item)
                
        except Exception as e:
            print(f"❌ Failed to install FFmpeg: {e}")
    else:
        print("🔍 FFmpeg is already available in directory.")

# --- PREFIX LOGIC ---
def get_prefix(bot, message):
    if not message.guild: return "!"
    return bot.db.get(f"prefix.{message.guild.id}", "!")

# --- BOT CLASS SETUP ---
class NovaX(commands.Bot):
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
        # 1. Start Health Server in background thread
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # 2. Install FFmpeg before loading music cog
        install_ffmpeg()
        
        # 3. Database & Extensions
        os.makedirs("./data", exist_ok=True)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f: json.dump({}, f)
        
        self.db = Database("data/database.json")
        print("💾 Database connected.")
        await self.load_extensions()

    async def load_extensions(self):
        for filename in os.listdir('./'):
            if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
                try: 
                    await self.load_extension(filename[:-3])
                    print(f"✅ Loaded Extension: {filename}")
                except Exception as e: 
                    print(f'❌ Failed to load {filename}: {e}')

    async def on_ready(self):
        print(f"---")
        print(f"✅ NovaX v1.10 Online | Logged in as: {self.user}")
        print(f"---")
        if not self.update_status.is_running(): 
            self.update_status.start()
        await self.tree.sync()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"NovaX v1.10 | {len(self.guilds)} Servers"
        await self.change_presence(
            activity=discord.Streaming(
                name=status_text, 
                url="https://twitch.tv/novax_bot"
            )
        )

# --- RUNNING THE BOT ---
async def run_bot():
    bot = NovaX()
    token = os.getenv("TOKEN")
    if not token:
        print("❌ CRITICAL: No TOKEN found in environment variables!")
        return

    async with bot:
        try:
            await bot.start(token)
        except KeyboardInterrupt:
            print("🔴 Shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
