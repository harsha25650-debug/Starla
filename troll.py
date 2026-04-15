import discord
from discord.ext import commands
import asyncio
import random

class Troll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    def is_active(self, channel_id):
        return self.active.get(channel_id, False)

    # 😈 FAKE NUKE START
    @commands.command()
    @commands.is_owner()
    async def nuke(self, ctx):

        if self.is_active(ctx.channel.id):
            return await ctx.send("⚠️ Already running.")

        self.active[ctx.channel.id] = True

        msg = await ctx.send("⚠️ Initializing Nuke Protocol...")

        steps = [
            "🔍 Scanning server...",
            "📡 Connecting to Discord API...",
            "💣 Injecting payload...",
            "🔥 Deleting channels...",
            "⚡ Bypassing security...",
            "💥 Finalizing..."
        ]

        for step in steps:
            if not self.is_active(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            await asyncio.sleep(2)
            await msg.edit(content=step)

        # fake progress bar
        for i in range(0, 101, 10):
            if not self.is_active(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            await asyncio.sleep(1)
            await msg.edit(content=f"🔥 Nuking server... {i}%")

        await asyncio.sleep(1)
        await msg.edit(content="💀 Server Nuked Successfully! (Just Kidding 😈)")

        self.active[ctx.channel.id] = False

    # 💬 CONTROLLED SPAM
    @commands.command()
    @commands.is_owner()
    async def trollspam(self, ctx, *, args=None):

        if not args:
            return await ctx.send("❌ Usage: !trollspam <message> <amount>")

        try:
            parts = args.rsplit(" ", 1)
            message = parts[0]
            amount = int(parts[1])
        except:
            return await ctx.send("❌ Example: !trollspam hello 10")

        if amount > 50:
            return await ctx.send("⚠️ Max 50 messages allowed.")

        self.active[ctx.channel.id] = True

        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            if not self.is_active(ctx.channel.id):
                break

            await ctx.send(message)
            await asyncio.sleep(0.4)

        self.active[ctx.channel.id] = False

    # 😂 RANDOM TROLL MESSAGES
    @commands.command()
    @commands.is_owner()
    async def troll(self, ctx, member: discord.Member):

        messages = [
            f"{member.mention} system hacked 😈",
            f"{member.mention} your data leaked 💀",
            f"{member.mention} FBI is watching 👀",
            f"{member.mention} password exposed 🔓",
            f"{member.mention} run... too late 🏃"
        ]

        await ctx.send(random.choice(messages))

    # 🏷️ NICKNAME TROLL
    @commands.command()
    @commands.is_owner()
    async def trollnick(self, ctx, member: discord.Member, *, name):

        try:
            await member.edit(nick=name)
            await ctx.send(f"😈 Nickname changed for {member.mention}")
        except:
            await ctx.send("❌ Failed (missing permissions)")

    # 🛑 STOP ALL
    @commands.command()
    @commands.is_owner()
    async def trollstop(self, ctx):

        if self.is_active(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send("🛑 Troll actions stopped.")
        else:
            await ctx.send("Nothing running.")

async def setup(bot):
    await bot.add_cog(Troll(bot))
