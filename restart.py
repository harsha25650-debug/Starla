import discord
from discord.ext import commands
import os
import sys

class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="restart")
    async def restart(self, ctx):
        # Yahan apni User ID daalein (Owner Check)
        owner_id = 1140926535935725711  # <--- Apni ID yahan badlein

        # Agar message bhejne wala owner nahi hai, toh bot kuch nahi karega
        if ctx.author.id != owner_id:
            return 

        await ctx.send("🔄 **Restarting bot...**")
        
        # Bot ke saare connections close karne ke liye
        await self.bot.close()
        
        # Current python script ko dobara execute karne ke liye
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot):
    await bot.add_cog(Restart(bot))
