import discord
from discord.ext import commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="massping")
    @commands.has_permissions(manage_messages=True)

    # ⏳ cooldown (20 sec)
    @commands.cooldown(1, 20, commands.BucketType.user)

    async def massping(self, ctx, member: discord.Member, amount: int):

        # ❌ limit check
        if amount > 30:
            return await ctx.send("❌ Maximum limit is 30 pings.")

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        embed = discord.Embed(
            description=f"⚡ Pinging {member.mention} {amount} times...",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed)

        # ⚡ FAST LOOP (optimized delay)
        for i in range(amount):
            await ctx.send(member.mention)
            await asyncio.sleep(0.3)  # ⚡ fast but safe

        done = discord.Embed(
            description=f"✅ Done pinging {member.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=done)

    # ❗ cooldown error
    @massping.error
    async def massping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⏳ Wait {round(error.retry_after, 1)} seconds."
            )

async def setup(bot):
    await bot.add_cog(MassPing(bot))
