import discord
import os
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user}")

    # 🔥 Sync slash commands (IMPORTANT)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally")
    except Exception as e:
        print(f"❌ Sync failed: {e}")


# Load all extension files
async def load_extensions():
    for filename in os.listdir('./'):
        if filename.endswith('.py') and filename not in ['main.py', 'db.py', 'requirements.txt']:
            try:
                await bot.load_extension(f'{filename[:-3]}')
                print(f'✅ Loaded extension: {filename}')
            except Exception as e:
                print(f'❌ Failed to load {filename}: {e}')


async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    asyncio.run(main())
