import discord
from discord.ext import commands
import asyncio
import random

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    def is_running(self, channel_id):
        return self.active.get(channel_id, False)

    # 🚀 1. SAFE UNLIMITED MASSPING
    @commands.command()
    @commands.is_owner()
    async def massping(self, ctx, member: discord.Member, amount: int):

        if amount <= 0:
            return await ctx.send("❌ Invalid amount.")

        if self.is_running(ctx.channel.id):
            return await ctx.send("⚠️ Already running.")

        self.active[ctx.channel.id] = True
        await ctx.send(f"⚡ Starting mass ping x{amount}")

        sent = 0

        while sent < amount:
            if not self.is_running(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            batch = min(5, amount - sent)

            for _ in range(batch):
                if not self.is_running(ctx.channel.id):
                    return await ctx.send("🛑 Stopped.")

                await ctx.send(member.mention)
                sent += 1

            await asyncio.sleep(0.5)

        self.active[ctx.channel.id] = False
        await ctx.send("✅ Done.")

    # ⚡ 2. FAST LOOP
    @commands.command()
    @commands.is_owner()
    async def mploop(self, ctx, member: discord.Member, amount: int):

        if amount > 500:
            return await ctx.send("❌ Max limit is 500.")

        if amount <= 0:
            return await ctx.send("❌ Invalid amount.")

        self.active[ctx.channel.id] = True
        await ctx.send(f"⚡ Fast loop ping x{amount}")

        for i in range(amount):
            if not self.is_running(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            await ctx.send(member.mention)

            if i % 5 == 0:
                await asyncio.sleep(0.2)

        self.active[ctx.channel.id] = False
        await ctx.send("✅ Done.")

    # 🚀 3. SINGLE MESSAGE FAST PING
    @commands.command()
    @commands.is_owner()
    async def mpfast(self, ctx, member: discord.Member, amount: int):

        if amount > 87:
            return await ctx.send("❌ Max 87 per message.")

        if amount <= 0:
            return

        self.active[ctx.channel.id] = True

        msg = ""
        for i in range(amount):
            if not self.is_running(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            msg += member.mention + " "

        await ctx.send(msg)

        self.active[ctx.channel.id] = False

    # 👻 4. GHOST PING (STOP SUPPORT ADDED)
    @commands.command()
    @commands.is_owner()
    async def ghostping(self, ctx, member: discord.Member, amount: int):

        if amount > 500:
            return await ctx.send("❌ Max 500 ghost pings.")

        if amount <= 0:
            return

        self.active[ctx.channel.id] = True

        # delete command message
        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            if not self.is_running(ctx.channel.id):
                return

            msg = await ctx.send(member.mention)

            await asyncio.sleep(random.uniform(0.15, 0.3))

            try:
                await msg.delete()
            except:
                pass

        self.active[ctx.channel.id] = False

    # 🛑 5. STOP COMMAND (GLOBAL)
    @commands.command()
    @commands.is_owner()
    async def mpstop(self, ctx):

        if self.is_running(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send("🛑 All ping tasks stopped.")
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
