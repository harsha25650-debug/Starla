import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import zipfile # 👈 Python's internal zip handler
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming
from database import Database

logging.basicConfig(level=logging.INFO)

def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is Alive!")
        def log_message(self, format, *args): return

    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

# --- ☢️ FFmpeg ZIP Installer (Bypasses Tar/XZ Errors) ---
def install_ffmpeg():
    local_ffmpeg = "./ffmpeg"
    if not os.path.exists(local_ffmpeg):
        print("📥 FFmpeg not found, downloading ZIP build...")
        try:
            # Using ffbinaries ZIP build (Compatible with all Linux)
            url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-linux-64.zip"
            zip_name = "ffmpeg.zip"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(zip_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # Extract using Python's zipfile (No system command needed)
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

# --- Prefix & Bot Class remain same ---
def get_prefix(bot, message):
    if not message.guild: return "!"
    return bot.db.get(f"prefix.{message.guild.id}", "!")

class NovaX(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=discord.Intents.all(), help_command=None)
        self.db = None

    async def setup_hook(self):
        threading.Thread(target=run_health_server, daemon=True).start()
        install_ffmpeg()
        os.makedirs("./data", exist_ok=True)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f: json.dump({}, f)
        self.db = Database("data/database.json")
        await self.load_extensions()

    async def load_extensions(self):
        for filename in os.listdir('./'):
            if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
                try: await self.load_extension(filename[:-3])
                except Exception as e: print(f'❌ Failed {filename}: {e}')

    async def on_ready(self):
        print(f"✅ NovaX v1.10 Online | {self.user}")
        if not self.update_status.is_running(): self.update_status.start()
        await self.tree.sync()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status_text = f"NovaX | {len(self.guilds)} Servers"
        await self.change_presence(activity=discord.Streaming(name=status_text, url="https://twitch.tv/novax_bot"))

async def run_bot():
    bot = NovaX()
    token = os.getenv("TOKEN")
    async with bot: await bot.start(token)

if __name__ == "__main__":
    asyncio.run(run_bot())
