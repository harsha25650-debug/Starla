import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spam = {}

    @commands.command(name="spam")
    @commands.is_owner()
    async def spam(self, ctx, *, args=None):
        """
        Usage: !spam hello 10
        """

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

        # mark spam active
        self.active_spam[ctx.channel.id] = True

        await ctx.message.delete()

        for _ in range(amount):
            # check if stopped
            if not self.active_spam.get(ctx.channel.id):
                break

            await ctx.send(message)
            await asyncio.sleep(0.3)

        # cleanup after finish
        self.active_spam.pop(ctx.channel.id, None)


    @commands.command(name="spstop")
    @commands.is_owner()
    async def spstop(self, ctx):
        """
        Stops active spam in current channel
        """

        if self.active_spam.get(ctx.channel.id):
            self.active_spam[ctx.channel.id] = False
            await ctx.send("🛑 Spam stopped.")
        else:
            await ctx.send("⚠️ No active spam in this channel.")

        await ctx.message.delete()


    # 🔒 Error Handler
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
