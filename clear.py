import discord
from discord.ext import commands
import asyncio

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1) # +1 ctx message ke liye
        msg = await ctx.send(f"✅ {amount} messages deleted successfully")
        await asyncio.sleep(5) # 5 second baad notification delete ho jayegi
        await msg.delete()

async def setup(bot):
    await bot.add_cog(Clear(bot))
