import discord
from discord.ext import commands
import asyncio
import random

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}
        self.allowed_users = set()  # ✅ access list

    def is_running(self, channel_id):
        return self.active.get(channel_id, False)

    def has_access(self, ctx):
        return ctx.author.id == self.bot.owner_id or ctx.author.id in self.allowed_users

    # ✅ GIVE ACCESS
    @commands.command()
    @commands.is_owner()
    async def mpaccess(self, ctx, member: discord.Member):
        self.allowed_users.add(member.id)
        await ctx.send(f"✅ MP access granted for {member.mention}")

    # ❌ REMOVE ACCESS
    @commands.command()
    @commands.is_owner()
    async def mpremove(self, ctx, member: discord.Member):
        self.allowed_users.discard(member.id)
        await ctx.send(f"❌ MP access removed for {member.mention}")

    # 🚀 MASSPING
    @commands.command()
    async def massping(self, ctx, member: discord.Member, amount: int):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if amount <= 0:
            return await ctx.send("Invalid amount.")

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

    # ⚡ FAST LOOP
    @commands.command()
    async def mploop(self, ctx, member: discord.Member, amount: int):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if amount > 500:
            return await ctx.send("Max limit is 500.")

        if amount <= 0:
            return await ctx.send("Invalid amount.")

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

    # 🚀 FAST MESSAGE
    @commands.command()
    async def mpfast(self, ctx, member: discord.Member, amount: int):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if amount > 87:
            return await ctx.send("Max 87 per message.")

        if amount <= 0:
            return

        self.active[ctx.channel.id] = True

        msg = ""
        for _ in range(amount):
            if not self.is_running(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            msg += member.mention + " "

        await ctx.send(msg)
        self.active[ctx.channel.id] = False

    # 👻 GHOSTPING
    @commands.command()
    async def ghostping(self, ctx, member: discord.Member, amount: int):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if amount > 500:
            return await ctx.send("Max 500 ghost pings.")

        if amount <= 0:
            return

        self.active[ctx.channel.id] = True

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

    # 🛑 STOP
    @commands.command()
    async def mpstop(self, ctx):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if self.is_running(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send("🛑 All ping tasks stopped.")
        else:
            await ctx.send("Nothing running.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
