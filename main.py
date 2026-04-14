import discord
import os
import asyncio
import json
from discord.ext import commands

# --- PREFIX LOGIC ---
def get_prefix(bot, message):
    if not message.guild:
        return "!"  # Default prefix for DMs

    try:
        # data/prefixes.json se prefix uthayega
        with open("./data/prefixes.json", "r") as f:
            prefixes = json.load(f)
        return prefixes.get(str(message.guild.id), "!") 
    except (FileNotFoundError, json.JSONDecodeError):
        return "!"  # Agar file na mile toh default "!"

# --- BOT SETUP ---
intents = discord.Intents.all() # Moderation bots ke liye 'all' intents best rehte hain

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user}")

    # 🔥 Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# --- EXTENSION LOADER ---
async def load_extensions():
    # Folder check for 'data' directory (used by your modules)
    if not os.path.exists("./data"):
        os.makedirs("./data")

    # Extension loading logic
    for filename in os.listdir('./'):
        # Sirf .py files aur jo main files nahi hain unhe load karega
        if filename.endswith('.py') and filename not in ['main.py', 'db.py']:
            try:
                await bot.load_extension(f'{filename[:-3]}')
                print(f'✅ Loaded extension: {filename}')
            except Exception as e:
                print(f'❌ Failed to load {filename}: {e}')

async def main():
    async with bot:
        await load_extensions()
        # Token ko environment variable ya direct string se replace karein
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
        
