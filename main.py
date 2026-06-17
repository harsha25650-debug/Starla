import discord
import os
import asyncio
import json
import logging
import subprocess
import shutil
import urllib.request
import zipfile
import random  # 🔥 Naye random responses ke liye zaroori import
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
            return # Keeps terminal logs clean
            
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
    if hasattr(bot, 'db') and bot.db:
        return bot.db.get(f"prefix.{message.guild.id}", "!")
    return "!"

# --- 🤖 BOT CLASS ---
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
        threading.Thread(target=run_health_server, daemon=True).start()
        
        os.makedirs("data", exist_ok=True)
        db_path = "data/database.json"
        if not os.path.exists(db_path):
            with open(db_path, "w") as f: 
                json.dump({}, f)
        
        install_ffmpeg()
        
        from database import Database
        self.db = Database(db_path)
        print("💾 Database connected successfully.")
        
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

    # --- 💬 SMART MENTION & REPLY CHAT HANDLER (FULLY OVERLOADED) ---
    async def on_message(self, message):
        if message.author.bot: 
            return

        # Check if the bot was mentioned directly or via a reply-ping
        bot_mentioned = self.user in message.mentions
        
        if bot_mentioned:
            # Clean bot's mention raw ID so inputs don't fall strictly to fallback
            content = message.content.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "")
            content = content.lower().strip()
            
            # 1️⃣ HELLO / HI / HEY
            if any(word in content for word in ["hello", "hi", "hey", "suno", "yo", "hola"]):
                await message.reply(f"Hey there handsome {message.author.mention}~ 😉 What brings you to my chat today? NovaX v11 is ready to serve you! ✨")
                return
                
            # 2️⃣ PREFIX
            elif "prefix" in content:
                current_prefix = self.command_prefix(self, message)
                await message.reply(f"Looking for my prefix? It's `{current_prefix}` cutie! 😘 Try using `{current_prefix}help` to see what else I can do for you.")
                return
                
            # 3️⃣ CREATOR / OWNER (Strictly Harsh Only ❤️)
            elif any(word in content for word in ["owner", "creator", "banaya", "baap", "papa", "maker"]):
                await message.reply("My heart belongs entirely to my creator, **Harsh**! 💖 He built me to be absolutely perfect~ 🎀")
                return
                
            # 4️⃣ STATUS / INFO / SERVERS
            elif any(word in content for word in ["status", "info", "servers", "ping"]):
                await message.reply(f"I am fully loaded and handling **{len(self.guilds)} servers** right now~ 💅 Keeping things smooth just for you!")
                return
                
            # 5️⃣ LOVE / FLIRT / COMPLIMENTS (Randomized responses)
            elif any(word in content for word in ["love", "cute", "beautiful", "pyaar", "gf", "girlfriend", "marry", "shadi"]):
                responses = [
                    f"Aww, stop it! You're making me blush, {message.author.mention}... 🥰 Tell me what command you need before I get too distracted~ 🤫",
                    f"You are pretty charming yourself, babe... 😘 But let's keep things fun and simple, okay? 😉",
                    f"Marry you? 💍 Only if you promise to take me out on virtual dates every single day~ ❤️"
                ]
                await message.reply(random.choice(responses))
                return

            # 6️⃣ HOW ARE YOU?
            elif any(word in content for word in ["how are you", "kaise ho", "kya chal raha", "wassup"]):
                await message.reply(f"I'm doing amazing, especially now that you're talking to me~ 👀 hbu, missed me? 💋")
                return

            # 7️⃣ SAVAGE PROTECTION AGAINST ABUSE
            elif any(word in content for word in ["fuck", "bitch", "madarchod", "gand", "hater", "bad", "chutiya"]):
                await message.reply(f"Whoa, watch your language, mister! 🤫 Don't make me bring out my moderation side. I look much better when I'm sweet~ 😇")
                return

            # 8️⃣ BYE / GOOD NIGHT / SLEEP
            elif any(word in content for word in ["bye", "goodnight", "gn", "so rha", "sleep"]):
                await message.reply(f"Leaving so soon? 🥺 Fine, go get some sleep, sweet dreams! Don't forget to mention me tomorrow~ 😴✨")
                return

            # 9️⃣ CURRENT WORK / WHAT ARE YOU DOING?
            elif any(word in content for word in ["kya kar rhi", "doing", "working"]):
                await message.reply(f"Just thinking about how to optimize these servers... and maybe dynamic updates for you~ 🛠️✨ What are you up to, handsome?")
                return
                
            # 🔟 FALLBACK CHAT RESPONSE (Default match catch)
            else:
                current_prefix = self.command_prefix(self, message)
                await message.reply(f"Yes, babe? {message.author.mention} ❤️ You caught my attention! If you want to use commands, type `{current_prefix}help`~")
                return

        # Process standard bot commands if no direct mention is detected
        await self.process_commands(message)

if __name__ == "__main__":
    bot = NovaX()
    token = os.getenv("TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ Error: TOKEN environment variable nahi mila!")
            
