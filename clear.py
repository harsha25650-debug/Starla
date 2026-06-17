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

    # 🧹 HYBRID CLEAR COMMAND
    @commands.hybrid_command(name="clear", description="Delete messages in bulk, optionally targeting a specific user.")
    @app_commands.describe(amount="Number of messages to scan/delete", user="The user whose messages you want to delete")
    @has_perm_or_owner()
    async def clear(self, ctx, amount: int, user: discord.Member = None):
        """
        Purge messages smoothly.
        Usage:
        !clear 20          (Deletes last 20 messages)
        !clear 20 @User    (Deletes last 20 messages sent ONLY by that user)
        """
        # Defer response for slash commands to prevent timeouts during large purges
        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        # ❌ Validation checks
        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.", delete_after=5)

        if amount > 1000:  # Kept at 1000 to prevent API rate limits / cloud container freezing
            return await ctx.send("⚠️ Maximum limit per sweep is 1000 messages.", delete_after=5)

        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send("❌ NovaX lacks the `Manage Messages` permission.", delete_after=5)

        try:
            # If a specific user is targeted
            if user:
                def is_user(m):
                    return m.author.id == user.id

                # If it's a context menu/prefix command, we account for the command trigger message itself
                limit_check = amount + 1 if ctx.interaction is None else amount
                deleted = await ctx.channel.purge(limit=limit_check, check=is_user)
                actual_deleted = len(deleted)
            
            # General clean up (No specific user)
            else:
                limit_check = amount + 1 if ctx.interaction is None else amount
                deleted = await ctx.channel.purge(limit=limit_check)
                # Subtracting 1 to exclude the user's invocation command message
                actual_deleted = len(deleted) - 1 if ctx.interaction is None else len(deleted)

            # Prevent displaying negative counts if edge cases occur
            actual_deleted = max(0, actual_deleted)

            embed = discord.Embed(
                description=f"✅ Successfully purged **{actual_deleted}** messages" + (f" from {user.mention}." if user else "."),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=5)

        except discord.Forbidden:
            await ctx.send("❌ Missing access permissions to clear messages in this channel.", delete_after=5)

        except discord.HTTPException as e:
            await ctx.send(f"⚠️ Failed to delete some messages (Discord limitation: Messages older than 14 days cannot be bulk purged).", delete_after=5)

    # ❗ CLEAN LOCAL ERROR HANDLER
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You do not have the required permissions (`Manage Messages`) to use this command.", delete_after=5)

        elif isinstance(error, commands.MissingRequiredArgument):
            prefix = ctx.prefix
            await ctx.send(f"❌ Syntax Error. Correct Format:\n`{prefix}clear <amount>`\n`{prefix}clear <amount> @user`", delete_after=5)

        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please enter a valid number and mention a correct server member.", delete_after=5)
            
        else:
            print(f"Clear Command Error: {error}")
            await ctx.send("⚠️ An unhandled exception occurred during execution.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
            
