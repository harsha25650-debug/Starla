import discord
from discord.ext import commands
import asyncio
import random

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 🚀 1. SAFE UNLIMITED MASSPING
    @commands.command()
    @commands.is_owner()
    async def massping(self, ctx, member: discord.Member, amount: int):

        if amount <= 0:
            return await ctx.send("❌ Invalid amount.")

        if self.active.get(ctx.channel.id):
            return await ctx.send("⚠️ Already running.")

        self.active[ctx.channel.id] = True
        await ctx.send(f"⚡ Starting mass ping x{amount}")

        sent = 0

        while sent < amount:
            if not self.active.get(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            batch = min(5, amount - sent)

            for _ in range(batch):
                await ctx.send(member.mention)
                sent += 1

            await asyncio.sleep(0.5)

        self.active[ctx.channel.id] = False
        await ctx.send("✅ Done.")

    # ⚡ 2. FAST LOOP (MAX 50)
    @commands.command()
    @commands.is_owner()
    async def mploop(self, ctx, member: discord.Member, amount: int):

        if amount > 50:
            return await ctx.send("❌ Max limit is 50.")

        if amount <= 0:
            return await ctx.send("❌ Invalid amount.")

        await ctx.send(f"⚡ Fast loop ping x{amount}")

        for i in range(amount):
            await ctx.send(member.mention)

            if i % 5 == 0:
                await asyncio.sleep(0.2)

        await ctx.send("✅ Done.")

    # 🚀 3. SINGLE MESSAGE FAST PING
    @commands.command()
    @commands.is_owner()
    async def mpfast(self, ctx, member: discord.Member, amount: int):

        if amount > 100:
            return await ctx.send("❌ Max 100 per message.")

        msg = " ".join([member.mention for _ in range(amount)])
        await ctx.send(msg)

    # 👻 4. GHOST PING (UPDATED)
    @commands.command()
    @commands.is_owner()
    async def ghostping(self, ctx, member: discord.Member, amount: int):

        if amount > 20:
            return await ctx.send("❌ Max 20 ghost pings.")

        if amount <= 0:
            return

        # 🧹 delete command message
        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            msg = await ctx.send(member.mention)

            # random delay (more natural)
            await asyncio.sleep(random.uniform(0.15, 0.3))

            await msg.delete()

    # 🛑 5. STOP COMMAND
    @commands.command()
    @commands.is_owner()
    async def mpstop(self, ctx):

        if self.active.get(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send("🛑 Stopped successfully.")
        else:
            await ctx.send("❌ Nothing running.")

    # ❗ ERROR HANDLER
    @massping.error
    @mploop.error
    @mpfast.error
    @ghostping.error
    async def error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("❌ Only bot owner can use this.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
