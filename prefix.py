import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data"
        self.prefix_file = "./data/prefixes.json"
        
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        if not os.path.exists(self.prefix_file):
            with open(self.prefix_file, "w") as f:
                json.dump({}, f)

    def save_prefix(self, guild_id, prefix):
        with open(self.prefix_file, "r") as f:
            prefixes = json.load(f)
        
        prefixes[str(guild_id)] = prefix
        
        with open(self.prefix_file, "w") as f:
            json.dump(prefixes, f, indent=4)

    @commands.hybrid_command(name="setprefix", description="Change the bot's prefix for this server")
    @app_commands.describe(new_prefix="The new prefix you want to use")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, new_prefix: str):
        if len(new_prefix) > 5:
            return await ctx.send("❌ Prefix 5 characters se zyada lamba nahi ho sakta.")

        self.save_prefix(ctx.guild.id, new_prefix)
        await ctx.send(f"✅ **Prefix updated!** New prefix is: `{new_prefix}`")

async def setup(bot):
    await bot.add_cog(Prefix(bot))
  
