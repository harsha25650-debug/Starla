import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        if amount > 50:
            return await ctx.send("⚠️ Limit exceeded! Max allowed is 50.")

        await ctx.message.delete()

        for _ in range(amount):
            await ctx.send(message)
            await asyncio.sleep(0.3)


    # 🔒 Custom Error Handler
    @spam.error
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
