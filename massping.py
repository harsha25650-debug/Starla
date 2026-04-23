import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    def get_global_access(self):
        return self.bot.db.get("mpaccess.global", [])

    def add_global_access(self, user_id):
        users = self.get_global_access()
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set("mpaccess.global", users)

    def remove_global_access(self, user_id):
        users = self.get_global_access()
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set("mpaccess.global", users)

    async def check_permissions(self, ctx):
        user = ctx.author if hasattr(ctx, "author") else ctx.user
        if await self.bot.is_owner(user):
            return True
        return user.id in self.get_global_access()

    # =========================
    # 🔑 ACCESS COMMANDS
    # =========================
    @commands.hybrid_command(name="mpaccess")
    async def mpaccess(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("<a:spider_red_dot:1494179666133516411> Only owner allowed.")
        self.add_global_access(member.id)
        await ctx.reply(f"<a:greentick:1494180392440303777> {member} given access.")

    @commands.hybrid_command(name="mpremove")
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("<a:spider_red_dot:1494179666133516411> Access denied.")
        self.remove_global_access(member.id)
        await ctx.reply(f"<a:spider_red_dot:1494179666133516411> Removed access from {member}.")

    # =========================
    # 🚀 MASSPING
    # =========================
    @commands.hybrid_command(name="massping")
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_red_dot:1494179666133516411> Access denied.")

        amount = min(amount, 500)

        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ Already running here.")

        self.active[channel_id] = True
        await ctx.reply(f"<a:spider_red_dot:1494179666133516411> Starting {amount} pings...")

        sent = 0
        batch_size = 5

        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                remaining = amount - sent
                current = min(batch_size, remaining)

                msg = " ".join([member.mention] * current)
                await ctx.send(msg)

                sent += current
                await asyncio.sleep(1.2)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break

        self.active[channel_id] = False
        await ctx.send("<a:greentick:1494180392440303777> Mass ping completed.")

    # =========================
    # 👻 GHOSTPING
    # =========================
    @commands.hybrid_command(name="ghostping")
    async def ghostping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_red_dot:1494179666133516411> Access denied.")

        amount = min(amount, 100)

        channel_id = ctx.channel.id
        self.active[channel_id] = True

        await ctx.reply(f"<a:spider_red_dot:1494179666133516411> Ghost pinging {amount} times...", ephemeral=True)

        for _ in range(amount):
            if not self.active.get(channel_id):
                break

            try:
                msg = await ctx.send(member.mention)
                await asyncio.sleep(0.5)
                await msg.delete()
                await asyncio.sleep(1.0)
            except:
                pass

        self.active[channel_id] = False

    # =========================
    # ⚡ FAST BURST
    # =========================
    @commands.hybrid_command(name="mpfast")
    async def mpfast(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return

        amount = min(amount, 80)
        msg = " ".join([member.mention] * amount)
        await ctx.send(msg)

    # =========================
    # 🛑 STOP
    # =========================
    @commands.hybrid_command(name="mpstop")
    async def mpstop(self, ctx):
        self.active[ctx.channel.id] = False
        await ctx.reply("<a:greentick:1494180392440303777> Stopped.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
