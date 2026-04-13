import discord
from discord.ext import commands
import os
import importlib

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# AUTO LOAD ALL PY FILES EXCEPT MAIN
for file in os.listdir():
    if file.endswith(".py") and file != "main.py":
        module_name = file[:-3]
        module = importlib.import_module(module_name)

        if hasattr(module, "setup"):
            module.setup(bot)

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")

bot.run(os.getenv("TOKEN"))
