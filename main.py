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
    print(f"✅ Bot Online Hai: {bot.user}")

# Files load karne ka naya tarika (Direct files ke liye)
async def load_extensions():
    for filename in os.listdir('./'):
        # Sirf .py files lega, lekin main.py aur baki faltu files chhod dega
        if filename.endswith('.py') and filename not in ['main.py', 'db.py', 'requirements.txt']:
            try:
                # Yahan 'commands.' hata diya gaya hai
                await bot.load_extension(f'{filename[:-3]}')
                print(f'✅ {filename} load ho gayi!')
            except Exception as e:
                print(f'❌ {filename} load nahi hui! Error: {e}')

async def main():
    async with bot:
        await load_extensions()
        # Railway ke liye TOKEN env variable se lega
        await bot.start(os.getenv("TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
    
