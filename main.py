import discord
import os
import asyncio
import json
import logging
from discord.ext import commands, tasks
from discord import Activity, ActivityType, Streaming # 👈 Streaming add kiya

from database import Database

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)

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

    # --- DYNAMIC STATUS LOOP (Purple Dot) ---
    @tasks.loop(minutes=5)
    async def update_status(self):
        server_count = len(self.guilds)
        status_text = f"NovaX v1.10 | {server_count} Servers"
        
        # 🟣 Purple Dot (Streaming Status)
        # Note: URL dena zaroori hai tabhi purple color aayega
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
