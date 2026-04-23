import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # =========================
    # 🔑 ACCESS SYSTEM
    # =========================
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
    # 🚀 MASSPING (FAST SINGLE)
    # =========================
    @commands.hybrid_command(name="massping")
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_red_dot:1494179666133516411> Access denied.")

        amount = min(amount, 200)

        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ Already running here.")

        self.active[channel_id] = True
        await ctx.reply(f"<a:spider_red_dot:1494179666133516411> Starting fast ping...")

        sent = 0

        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                await ctx.send(member.mention)
                sent += 1

                # ⚡ fastest safe delay
                await asyncio.sleep(0.8)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

        self.active[channel_id] = False
        await ctx.send("<a:greentick:1494180392440303777> Mass ping completed.")

    # =========================
    # 👻 GHOSTPING (SILENT)
    # =========================
    @commands.hybrid_command(name="ghostping")
    async def ghostping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            try:
                await ctx.message.delete()
            except:
                pass
            return

        amount = min(amount, 100)

        channel_id = ctx.channel.id
        self.active[channel_id] = True

        # delete command message
        try:
            await ctx.message.delete()
        except:
            pass

        sent = 0

        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                msg = await ctx.send(member.mention)
                sent += 1

                await asyncio.sleep(0.4)
                await msg.delete()

                await asyncio.sleep(0.9)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

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
