import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from collections import Counter

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_pink = "<:topggDotPink:1525756454345375764>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 PERMISSION CHECK (OWNER & STAFF BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            return ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)

    # 🧹 UPGRADED HYBRID CLEAR COMMAND
    @commands.hybrid_command(name="clear", aliases=["purge", "c"], description="Delete messages in bulk, targeting a user, bots, or everyone.")
    @app_commands.describe(amount="Number of messages to delete (Max 1000)", user_or_filter="Optional: Mention user OR type 'bots'")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, user_or_filter: str = None):
        """
        Purge messages smoothly with user stats breakdown.
        Usage:
        !clear 20                 (Deletes last 20 messages)
        !clear 20 @User           (Deletes last 20 messages from that user only)
        !clear 20 bots            (Deletes last 20 messages from ANY bot profile)
        """
        # --- 🗑️ STEP 1: HANDLE COMMAND TRIGGER SOURCE ---
        if ctx.interaction is None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        else:
            await ctx.interaction.response.defer(ephemeral=True)

        # --- ❌ STEP 2: PARSE & VALIDATE QUANTITY BOUNDS ---
        if amount <= 0:
            return await ctx.send(f"{self.cross} **Value Error:** Amount parameter must be greater than 0.", delete_after=5)

        if amount > 1000:
            return await ctx.send(f"{self.cross} **System Bound:** Maximum limit per sweep is capped at 1000 messages.", delete_after=5)

        # --- 🧹 STEP 3: EXECUTE DYNAMIC PURGE LOGIC ---
        try:
            # Stats dictionary for keeping track of deleted accounts mapping
            deleted_stats = Counter()

            def purge_filter(m):
                if not user_or_filter:
                    deleted_stats[m.author] += 1
                    return True
                
                if user_or_filter.lower() in ["bots", "bot", "pb"]:
                    if m.author.bot:
                        deleted_stats[m.author] += 1
                        return True
                    return False
                
                if ctx.message and ctx.message.mentions:
                    target = ctx.message.mentions[0]
                    if m.author.id == target.id:
                        deleted_stats[m.author] += 1
                        return True
                    return False
                
                clean_target = user_or_filter.replace("<@", "").replace(">", "").replace("!", "")
                if str(m.author.id) == clean_target:
                    deleted_stats[m.author] += 1
                    return True
                return False

            deleted = await ctx.channel.purge(limit=amount, check=purge_filter)
            actual_deleted = len(deleted)

            # Target filter logging configuration
            target_text = "."
            if user_or_filter:
                if user_or_filter.lower() in ["bots", "bot", "pb"]:
                    target_text = " from **any active Bot** profile."
                else:
                    target_text = f" from the specified user target."

            # --- 📢 SUCCESS OUTCOME EMBED WITH SUMMARY METRICS ---
            embed = discord.Embed(
                description=f"{self.dot_pink} **Successfully purged `{actual_deleted}` message(s)**{target_text}",
                color=0x2b2d31
            )
            
            # Formulate user stats logs dynamically inside embed block
            if deleted_stats:
                stats_lines = []
                # Top 8 users sorted by most deleted messages to prevent embed overflow limits
                for user_obj, count in deleted_stats.most_common(8):
                    stats_lines.append(f"{self.arrow} {user_obj.mention} : `{count} message(s)`")
                
                if len(deleted_stats) > 8:
                    stats_lines.append(f"*...and {len(deleted_stats) - 8} more user profile(s).*")
                    
                embed.add_field(name="📊 Deletion Summary Breakdown", value="\n".join(stats_lines), inline=False)

            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed, delete_after=7) # Output window slightly increased to 7s for better readability

        except discord.Forbidden:
            err_msg = f"{self.cross} Missing structural visibility/write channel control clearance permissions."
            if ctx.interaction:
                await ctx.interaction.followup.send(content=err_msg, ephemeral=True)
            else:
                await ctx.send(err_msg, delete_after=5)
                
        except discord.HTTPException:
            warn_msg = f"{self.dot_pink} **Sweep complete.** *(Note: Messages older than 14 days skipped due to Discord engine limits).* "
            if ctx.interaction:
                await ctx.interaction.followup.send(content=warn_msg, ephemeral=True)
            else:
                await ctx.send(warn_msg, delete_after=6)

    # 🤖 FAST BOT PURGE SHORTCUT COMMAND (!pb / !purgebot)
    @commands.command(name="purgebot", aliases=["pb"], description="Shortcut to clear messages specifically from all bots.")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def purgebot(self, ctx, amount: int = 50):
        """Shortcut command to clean bot messages instantly: !pb 30"""
        await self.clear(ctx, amount=amount, user_or_filter="bots")

    # ❗ CLEAN ACTION ERROR HANDLER
    @clear.error
    @purgebot.error
    async def clear_error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** `Manage Messages` authorization clearance token verification failed.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, delete_after=5)
            
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} **System Failure:** I am missing `Manage Messages` channel operational permissions.", delete_after=5)
            
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            p = ctx.prefix
            embed = discord.Embed(
                title=f"{self.yes} Clear/Purge Protocol Guide",
                description=f"{self.arrow} **Global Clear:** `{p}clear 50`\n"
                            f"{self.arrow} **User Filter:** `{p}clear 50 @user`\n"
                            f"{self.arrow} **Bot Filter:** `{p}clear 50 bots` or `{p}pb 50`",
                color=0x2b2d31
            )
            await ctx.send(embed=embed, delete_after=8)
        else:
            await ctx.send(f"{self.cross} **Operational Exception:** Check arguments configuration matrix.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
                    
