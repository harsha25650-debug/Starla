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
            return ctx.author.id == ctx.guild.owner_id or ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)

    # 🧹 CLEAR COMMAND
    @commands.hybrid_command(name="clear", description="Delete messages in bulk")
    @app_commands.describe(amount="Number of messages to delete")
    @has_perm_or_owner()
    async def clear(self, ctx, amount: int):

        # ❌ Invalid amount
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.", delete_after=5)

        if amount > 10000:
            return await ctx.send("⚠️ Max limit is 10000 messages.", delete_after=5)

        # ⚠️ Bot permission check
        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send("❌ I need 'Manage Messages' permission.", delete_after=5)

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)

            msg = await ctx.send(
                f"✅ Deleted {len(deleted)-1} messages",
                delete_after=5
            )

        except discord.Forbidden:
            await ctx.send("❌ I can't delete messages here.", delete_after=5)

        except discord.HTTPException:
            await ctx.send("⚠️ Failed to delete some messages (maybe too old).", delete_after=5)

    # ❗ ERROR HANDLER
    @clear.error
    async def clear_error(self, ctx, error):

        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission.", delete_after=5)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: !clear <amount>", delete_after=5)

        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Enter a valid number.", delete_after=5)

        else:
            await ctx.send("⚠️ Error occurred.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
