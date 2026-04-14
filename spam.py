import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spam = {}
        self.allowed_users = set()  # ✅ access list

    def has_access(self, ctx):
        return ctx.author.id == self.bot.owner_id or ctx.author.id in self.allowed_users

    # ✅ GIVE ACCESS
    @commands.command(name="spaccess")
    @commands.is_owner()
    async def spaccess(self, ctx, member: discord.Member):
        self.allowed_users.add(member.id)
        await ctx.send(f"✅ Spam access granted for {member.mention}")

    # ❌ REMOVE ACCESS
    @commands.command(name="spremove")
    @commands.is_owner()
    async def spremove(self, ctx, member: discord.Member):
        self.allowed_users.discard(member.id)
        await ctx.send(f"❌ Spam access removed for {member.mention}")

    # 🚀 SPAM COMMAND
    @commands.command(name="spam")
    async def spam(self, ctx, *, args=None):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if not args:
            return await ctx.send("❌ Usage: !spam <message> <amount>")

        try:
            parts = args.rsplit(" ", 1)
            message = parts[0]
            amount = int(parts[1])
        except:
            return await ctx.send("❌ Invalid format. Example: !spam hello 10")

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        if amount > 500:
            return await ctx.send("⚠️ Limit exceeded! Max allowed is 500.")

        self.active_spam[ctx.channel.id] = True

        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            if not self.active_spam.get(ctx.channel.id):
                break

            await ctx.send(message)
            await asyncio.sleep(0.3)

        self.active_spam.pop(ctx.channel.id, None)

    # 🛑 STOP SPAM
    @commands.command(name="spstop")
    async def spstop(self, ctx):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if self.active_spam.get(ctx.channel.id):
            self.active_spam[ctx.channel.id] = False
            await ctx.send("🛑 Spam stopped.")
        else:
            await ctx.send("⚠️ No active spam in this channel.")

        try:
            await ctx.message.delete()
        except:
            pass

    # 🔒 ERROR HANDLER
    @spam.error
    @spstop.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("⛔ Access denied: Bot owner only command.")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing arguments. Usage: !spam <message> <amount>")

        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid input. Please enter a valid number.")

        else:
            await ctx.send("⚠️ Unexpected error occurred.")

async def setup(bot):
    await bot.add_cog(Spam(bot))
