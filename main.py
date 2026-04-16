import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request  # 👈 wget ki jagah ye use karenge
import tarfile         # 👈 tar command ki jagah logic handle karne ke liye

from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming
from database import Database

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)

# --- ☢️ FINAL FFMPEG INSTALLER (No Wget Required) ---
def install_ffmpeg():
    # Check agar ffmpeg pehle se folder mein hai ya system mein
    local_ffmpeg = "./ffmpeg"
    if not os.path.exists(local_ffmpeg) and not shutil.which("ffmpeg"):
        print("📥 FFmpeg not found, downloading static binary via urllib...")
        try:
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            archive_name = "ffmpeg.tar.xz"
            
            # 1. Download using urllib
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(archive_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            
            # 2. Extract using subprocess (Railway usually has tar)
            subprocess.run(f"tar -xf {archive_name}", shell=True)
            
            # 3. Binary ko dhoond kar move karna
            extracted_dir = None
            for item in os.listdir('.'):
                if os.path.isdir(item) and item.startswith("ffmpeg-"):
                    extracted_dir = item
                    break
            
            if extracted_dir:
                shutil.move(f"{extracted_dir}/ffmpeg", "./ffmpeg")
                shutil.move(f"{extracted_dir}/ffprobe", "./ffprobe")
                subprocess.run("chmod +x ffmpeg ffprobe", shell=True)
                
                # Cleanup
                shutil.rmtree(extracted_dir)
                os.remove(archive_name)
                print("✅ FFmpeg installed successfully in bot directory!")
            else:
                print("❌ Error: Extracted directory not found.")
                
        except Exception as e:
            print(f"❌ Failed to install FFmpeg: {e}")
    else:
        print("🔍 FFmpeg is already available.")

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
        # Start hote hi FFmpeg installer run karein
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
