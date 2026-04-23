import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spam = {}

    def get_access(self, guild_id):
        return self.bot.db.get(f"spaccess.{guild_id}", [])

    def add_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    def remove_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    async def has_access(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        if ctx.guild:
            users = self.get_access(ctx.guild.id)
            return ctx.author.id in users
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="spaccess")
    @commands.is_owner()
    async def spaccess(self, ctx, member: discord.User):
        if not ctx.guild:
            return await ctx.send("<a:spider_red_dot:1494179666133516411> Use this in a server.")
        self.add_access(ctx.guild.id, member.id)
        await ctx.send(f"<a:greentick:1494180392440303777> Access granted to {member.mention}")

    @commands.command(name="spremove")
    @commands.is_owner()
    async def spremove(self, ctx, member: discord.User):
        if not ctx.guild:
            return await ctx.send("<a:spider_red_dot:1494179666133516411> Use this in a server.")
        self.remove_access(ctx.guild.id, member.id)
        await ctx.send(f"<a:spider_red_dot:1494179666133516411> Access removed from {member.mention}")

    @commands.command(name="spam")
    async def spam(self, ctx, *, args=None):

        if not await self.has_access(ctx):
            return await ctx.send("<a:spider_red_dot:1494179666133516411> No permission.")

        if not args:
            return await ctx.send("<a:spider_red_dot:1494179666133516411> Usage: !spam <message> <amount>")

        try:
            parts = args.rsplit(" ", 1)
            message = parts[0]
            amount = int(parts[1])
        except:
            return await ctx.send("<a:spider_red_dot:1494179666133516411> Example: !spam hello 10")

        if amount <= 0:
            return await ctx.send("<a:spider_red_dot:1494179666133516411> Amount must be > 0")

        amount = min(amount, 300)

        channel_id = ctx.channel.id
        if self.active_spam.get(channel_id):
            return await ctx.send("⚠️ Already running.")

        self.active_spam[channel_id] = True

        try:
            await ctx.message.delete()
        except:
            pass

        sent = 0
        batch_size = 3

        while sent < amount:
            if not self.active_spam.get(channel_id):
                break

            try:
                remaining = amount - sent
                current = min(batch_size, remaining)

                msg = "\n".join([message] * current)
                await ctx.send(msg)

                sent += current
                await asyncio.sleep(1.1)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break

        self.active_spam.pop(channel_id, None)
        await ctx.send("<a:greentick:1494180392440303777> Done.")

    @commands.command(name="spstop")
    async def spstop(self, ctx):

        if not await self.has_access(ctx):
            return await ctx.send("<a:spider_red_dot:1494179666133516411> No permission.")

        if self.active_spam.get(ctx.channel.id):
            self.active_spam[ctx.channel.id] = False
            await ctx.send("<a:greentick:1494180392440303777> Stopped.")
        else:
            await ctx.send("⚠️ No active spam.")

        try:
            await ctx.message.delete()
        except:
            pass

    @spam.error
    @spstop.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("<a:spider_red_dot:1494179666133516411> Owner only.")
        else:
            await ctx.send("<a:spider_red_dot:1494179666133516411> Error occurred.")

async def setup(bot):
    await bot.add_cog(Spam(bot))
