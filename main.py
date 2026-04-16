import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import tarfile         # 👈 Python internal extraction ke liye

from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming
from database import Database

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)

# --- ☢️ UNIVERSAL FFMPEG INSTALLER (Gzip + Python Extract) ---
def install_ffmpeg():
    local_ffmpeg = "./ffmpeg"
    # Check agar local folder mein ffmpeg pehle se hai
    if not os.path.exists(local_ffmpeg):
        print("📥 FFmpeg not found, downloading Gzip build for Railway...")
        try:
            # Gzip build link (xz error bypass karne ke liye)
            url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-linux-64.tar.gz"
            archive_name = "ffmpeg.tar.gz"
            
            # 1. Download using urllib
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(archive_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # 2. Extract using Python's tarfile (Bypass system tar/xz errors)
            print("📦 Extracting FFmpeg...")
            with tarfile.open(archive_name, "r:gz") as tar:
                tar.extractall(path=".")
            
            # 3. Permissions set karna
            if os.path.exists("./ffmpeg"):
                os.chmod("./ffmpeg", 0o755)
                print("✅ FFmpeg (Gzip) installed successfully!")
            
            # Cleanup
            if os.path.exists(archive_name): 
                os.remove(archive_name)
                
        except Exception as e:
            print(f"❌ Failed to install FFmpeg: {e}")
    else:
        print("🔍 FFmpeg is already available in directory.")

# --- PREFIX LOGIC ---
def get_prefix(bot, message):
    if not message.guild:
        return "!"
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
        # Bot start hote hi installer chalao
        install_ffmpeg()
        
        os.makedirs("./data", exist_ok=True)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f:
                json.dump({}, f)
        
        self.db = Database("data/database.json")
        print("💾 Database connected.")
        await self.load_extensions()

    async def load_extensions(self):
        for filename in os.listdir('./'):
            if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
                try:
                    await self.load_extension(f'{filename[:-3]}')
                    print(f'✅ Loaded: {filename}')
                except Exception as e:
                    print(f'❌ Failed {filename}: {e}')

    async def on_ready(self):
        print(f"---")
        print(f"✅ NovaX v1.10 is Online")
        print(f"🤖 User: {self.user}")
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
        server_count = len(self.guilds)
        status_text = f"NovaX v1.10 | {server_count} Servers"
        
        await self.change_presence(
            activity=discord.Streaming(
                name=status_text,
                url="https://www.twitch.tv/novax_bot" 
            )
        )

# --- RUNNING THE BOT ---
async def run_bot():
    bot = NovaX()
    
    token = os.getenv("TOKEN")
    if not token:
        print("❌ Error: TOKEN environment variable nahi mila!")
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
