import discord
from discord.ext import commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_pings = {}  # channel_id: running status

    @commands.command(name="massping")
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 20, commands.BucketType.user)

    async def massping(self, ctx, member: discord.Member, amount: int):

        if amount > 25:
            return await ctx.send("❌ Maximum limit is 25 pings.")

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        # mark active
        self.active_pings[ctx.channel.id] = True

        await ctx.send(f"⚡ Starting fast ping for {member.mention} ({amount}x)")

        for i in range(amount):
            # stop check
            if not self.active_pings.get(ctx.channel.id):
                return await ctx.send("⛔ Mass ping stopped.")

            await ctx.send(member.mention)

            # ⚡ fastest safe delay
            await asyncio.sleep(0.15)

        self.active_pings[ctx.channel.id] = False
        await ctx.send(f"✅ Done pinging {member.mention}")

    # 🛑 STOP COMMAND
    @commands.command(name="mpstop")
    @commands.has_permissions(manage_messages=True)
    async def mpstop(self, ctx):

        if self.active_pings.get(ctx.channel.id):
            self.active_pings[ctx.channel.id] = False
            await ctx.send("🛑 Mass ping stopped successfully.")
        else:
            await ctx.send("❌ No active mass ping running.")

    # cooldown error
    @massping.error
    async def massping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Wait {round(error.retry_after, 1)} seconds.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
