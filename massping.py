import discord
from discord.ext import commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="massping")
    @commands.has_permissions(manage_messages=True)

    # ⏳ COOLDOWN: 1 use per user every 30 seconds
    @commands.cooldown(1, 30, commands.BucketType.user)

    async def massping(self, ctx, member: discord.Member, amount: int):

        # ❌ limit check
        if amount > 10:
            return await ctx.send("❌ Maximum limit is 10 pings.")

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        embed = discord.Embed(
            description=f"🔔 Pinging {member.mention} {amount} times...",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

        # 🔁 ping loop
        for i in range(amount):
            await ctx.send(member.mention)
            await asyncio.sleep(1)

        done = discord.Embed(
            description=f"✅ Done pinging {member.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=done)

    # ❗ Cooldown error handler
    @massping.error
    async def massping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Wait {round(error.retry_after, 1)} seconds before using this again."
            )

async def setup(bot):
    await bot.add_cog(MassPing(bot))
