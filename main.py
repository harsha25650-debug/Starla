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

logging.basicConfig(level=logging.INFO)

def run_health_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"NovaX Alive")
        def log_message(self, format, *args): return
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

def install_ffmpeg():
    if not os.path.exists("./ffmpeg"):
        print("📥 Downloading FFmpeg ZIP...")
        try:
            url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.4.1/ffmpeg-4.4.1-linux-64.zip"
            urllib.request.urlretrieve(url, "ffmpeg.zip")
            with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.chmod("./ffmpeg", 0o755)
            print("✅ FFmpeg Installed!")
            os.remove("ffmpeg.zip")
        except Exception as e: print(f"❌ FFmpeg Error: {e}")

class NovaX(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all(), help_command=None)
    
    async def setup_hook(self):
        threading.Thread(target=run_health_server, daemon=True).start()
        install_ffmpeg()
        from database import Database
        self.db = Database("data/database.json")
        for f in os.listdir('./'):
            if f.endswith('.py') and f not in ['main.py', 'database.py']:
                await self.load_extension(f[:-3])

    async def on_ready(self):
        print(f"✅ {self.user} is Online")
        await self.tree.sync()

if __name__ == "__main__":
    bot = NovaX()
    bot.run(os.getenv("TOKEN"))
