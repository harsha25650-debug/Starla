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
from discord import Streaming

logging.basicConfig(level=logging.INFO)

# --- 🚀 HEALTH SERVER ---
def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"NovaX Alive")
        def log_message(self, format, *args): 
            return # Terminal logs clean rakhne ke liye
            
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
    # Agar database initialize ho chuka hai toh wahan se uthayega, nahi toh default "!"
    if hasattr(bot, 'db') and bot.db:
        return bot.db.get(f"prefix.{message.guild.id}", "!")
    return "!"

# --- 🤖 BOT CLASS ---
class NovaX(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=get_prefix, # 🔥 Hardcoded "!" ki jagah dynamic function link kiya
            intents=intents, 
            help_command=None,
            case_insensitive=True
        )
        self.db = None
    
    async def setup_hook(self):
        # Background thread mein Health Server start karna
        threading.Thread(target=run_health_server, daemon=True).start()
        
        # 📁 Data directory fix
        os.makedirs("data", exist_ok=True)
        db_path = "data/database.json"
        if not os.path.exists(db_path):
            with open(db_path, "w") as f: 
                json.dump({}, f)
        
        # FFmpeg background installation
        install_ffmpeg()
        
        # Database attach karna
        from database import Database
        self.db = Database(db_path)
        print("💾 Database connected successfully.")
        
        # Extension Loading
        for f in os.listdir('./'):
            if f.endswith('.py') and f not in ['main.py', 'database.py']:
                try:
                    await self.load_extension(f[:-3])
                    print(f"✅ Loaded extension: {f}")
                except Exception as e:
                    print(f"❌ Failed to load extension {f}: {e}")

    async def on_ready(self):
        print(f"---")
        print(f"✅ {self.user.name} is Online & Fully Overloaded!")
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
        status_text = f"NovaX v11 | {len(self.guilds)} Servers"
        await self.change_presence(activity=Streaming(name=status_text, url="https://twitch.tv/novax_bot"))

    # Commands Process handler
    async def on_message(self, message):
        if message.author.bot: 
            return
        # Isse normal text commands aur database prefix dono smooth chalenge
        await self.process_commands(message)

if __name__ == "__main__":
    bot = NovaX()
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Error: TOKEN environment variable nahi mila!")
        
