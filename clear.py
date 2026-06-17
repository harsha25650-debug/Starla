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
    @app_commands.describe(flag="Use '-user' to target a member", user="The member whose messages you want to delete", amount="Number of messages to delete")
    @has_perm_or_owner()
    async def clear(self, ctx, flag: str = None, user: discord.Member = None, amount: int = None):
        """
        Purge messages smoothly.
        Usage:
        !clear 20                    (Deletes last 20 messages)
        !clear -user @User 20        (Deletes specified amount from that user only)
        """
        # --- 🗑️ STEP 1: IMMEDIATELY DELETE THE USER'S COMMAND MESSAGE ---
        if ctx.interaction is None: # If it's a prefix command (!clear)
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass # Avoid crashing if bot lacks permission to delete your specific message
        else:
            # Defer slash command to prevent timeouts
            await ctx.interaction.response.defer(ephemeral=True)

        # --- ⚙️ STEP 2: PARSE ARGUMENTS FOR YOUR EXACT SYNTAX ---
        target_user = None
        purge_amount = 0

        # Case A: User ran exact syntax -> !clear -user @User 20
        if flag == "-user" and user is not None and amount is not None:
            target_user = user
            purge_amount = amount
        
        # Case B: User ran standard syntax -> !clear 20 (amount passes into the first argument 'flag')
        elif flag is not None and flag.isdigit():
            purge_amount = int(flag)
            target_user = None
        
        # Case C: Wrong syntax fallback
        else:
            prefix = ctx.prefix
            return await ctx.send(
                f"❌ **Invalid Syntax!** Use:\n`{prefix}clear <amount>`\n`{prefix}clear -user @user <amount>`", 
                delete_after=5
            )

        # --- ❌ STEP 3: VALIDATION CHECKS ---
        if purge_amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.", delete_after=5)

        if purge_amount > 1000:
            return await ctx.send("⚠️ Maximum limit per sweep is 1000 messages.", delete_after=5)

        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send("❌ NovaX lacks the `Manage Messages` permission.", delete_after=5)

        # --- 🧹 STEP 4: EXECUTE PURGE ---
        try:
            if target_user:
                def is_user(m):
                    return m.author.id == target_user.id

                deleted = await ctx.channel.purge(limit=purge_amount, check=is_user)
                actual_deleted = len(deleted)
            else:
                deleted = await ctx.channel.purge(limit=purge_amount)
                actual_deleted = len(deleted)

            # Modern Response Embed
            embed = discord.Embed(
                description=f"✅ Successfully purged **{actual_deleted}** messages" + (f" from {target_user.mention}." if target_user else "."),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed, delete_after=5)

        except discord.Forbidden:
            await ctx.send("❌ Missing access permissions to clear messages in this channel.", delete_after=5)
        except discord.HTTPException:
            await ctx.send("⚠️ Clean complete. (Note: Messages older than 14 days were skipped due to Discord limits).", delete_after=5)

    # ❗ CLEAN LOCAL ERROR HANDLER
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You do not have the required permissions (`Manage Messages`) to use this command.", delete_after=5)
        else:
            print(f"Clear Command Error: {error}")
            await ctx.send("⚠️ An execution error occurred or arguments were misaligned.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
    
