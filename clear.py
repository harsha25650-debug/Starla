import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK (OWNER BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True

            return ctx.author.guild_permissions.manage_messages

        return commands.check(predicate)

    # 🧹 CLEAR COMMAND (PREFIX + SLASH)
    @commands.hybrid_command(name="clear", description="Delete messages in bulk")
    @app_commands.describe(amount="Number of messages to delete")
    @has_perm_or_owner()
    async def clear(self, ctx, amount: int):

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        if amount > 1000:
            return await ctx.send("⚠️ Max 1000 messages at once.")

        deleted = await ctx.channel.purge(limit=amount + 1)

        msg = await ctx.send(f"✅ {len(deleted)-1} messages deleted successfully")

        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass

    # ❗ ERROR HANDLER
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please enter a valid number.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Clear(bot))
