import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming

from database import Database

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)

# --- ☢️ NUCLEAR FFMPEG INSTALLER FOR RAILWAY ---
def install_ffmpeg():
    # Check agar ffmpeg pehle se folder mein hai ya system mein
    if not os.path.exists("./ffmpeg") and not shutil.which("ffmpeg"):
        print("📥 FFmpeg not found, downloading static binary for Railway...")
        try:
            # Static build download kar rahe hain jo har Linux environment mein chalta hai
            url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            subprocess.run(f"wget -q {url}", shell=True)
            subprocess.run("tar -xf ffmpeg-release-amd64-static.tar.xz", shell=True)
            
            # Binary ko main directory mein move karna
            subprocess.run("mv ffmpeg-*-amd64-static/ffmpeg .", shell=True)
            subprocess.run("mv ffmpeg-*-amd64-static/ffprobe .", shell=True)
            
            # Permissions set karna
            subprocess.run("chmod +x ffmpeg ffprobe", shell=True)
            
            # Cleanup
            subprocess.run("rm -rf ffmpeg-*-amd64-static* ffmpeg-release-amd64-static.tar.xz", shell=True)
            print("✅ FFmpeg installed successfully in bot directory!")
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
        # Pehle FFmpeg install karein start hone se pehle
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
