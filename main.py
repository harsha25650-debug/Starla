import discord
import os
import asyncio
import json
from discord.ext import commands

from database import Database


# --- PREFIX LOGIC (DATABASE BASED) ---
def get_prefix(bot, message):
    if not message.guild:
        return "!"
    
    return bot.db.get(f"prefix.{message.guild.id}", "!")


# --- BOT SETUP ---
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user}")
    print("💾 Database loaded successfully")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


# --- EXTENSION LOADER ---
async def load_extensions():

    # 📁 Ensure data folder exists
    os.makedirs("./data", exist_ok=True)

    # 🔄 Load all cogs
    for filename in os.listdir('./'):
        if filename.endswith('.py') and filename not in ['main.py', 'database.py']:
            try:
                await bot.load_extension(f'{filename[:-3]}')
                print(f'✅ Loaded extension: {filename}')
            except Exception as e:
                print(f'❌ Failed to load {filename}: {e}')


async def main():
    async with bot:

        # 📁 Ensure data folder exists
        os.makedirs("./data", exist_ok=True)

        # 📁 Ensure database file exists (🔥 FIX)
        if not os.path.exists("./data/database.json"):
            with open("./data/database.json", "w") as f:
                json.dump({}, f)

        # ✅ DATABASE attach (🔥 IMPORTANT FIX)
        bot.db = Database("data/database.json")

        await load_extensions()

        token = os.getenv("TOKEN")
        if token:
            await bot.start(token)
        else:
            print("❌ Error: TOKEN environment variable nahi mila!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🔴 Bot is shutting down...")
