import discord
from discord.ext import commands
from discord import app_commands
import asyncio

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
    @commands.hybrid_command(name="clear", aliases=["purge", "c"], description="Delete messages in bulk, optionally targeting a specific user.")
    @app_commands.describe(amount="Number of messages to delete (Max 1000)", user="Optional member to filter and delete messages from")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int, user: discord.Member = None):
        """
        Purge messages smoothly.
        Usage:
        !clear 20                 (Deletes last 20 messages)
        !clear 20 @User           (Deletes last 20 messages from that user only)
        """
        # --- 🗑️ STEP 1: HANDLE COMMAND TRIGGER SOURCE ---
        if ctx.interaction is None:
            try:
                await ctx.message.delete()
            except Exception:
                pass
        else:
            # Ephemeral response to avoid interaction state block
            await ctx.interaction.response.defer(ephemeral=True)

        # --- ❌ STEP 2: PARSE & VALIDATE QUANTITY BOUNDS ---
        if amount <= 0:
            return await ctx.send(f"{self.cross} **Value Error:** Amount parameter must be greater than 0.", delete_after=5)

        if amount > 1000:
            return await ctx.send(f"{self.cross} **System Bound:** Maximum limit per sweep is capped at 1000 messages.", delete_after=5)

        # --- 🧹 STEP 3: EXECUTE DYNAMIC PURGE LOGIC ---
        try:
            if user:
                def is_user(m):
                    return m.author.id == user.id

                # User target filtering execution
                deleted = await ctx.channel.purge(limit=amount, check=is_user)
                actual_deleted = len(deleted)
            else:
                # Direct structural mass purge execution
                deleted = await ctx.channel.purge(limit=amount)
                actual_deleted = len(deleted)

            # --- 📢 SUCCESS OUTCOME EMBED (Starla Theme Pink) ---
            embed = discord.Embed(
                description=f"{self.dot_pink} **Successfully purged `{actual_deleted}` message(s)**" + (f" from {user.mention}." if user else "."),
                color=0x2b2d31
            )
            
            # Send message safely based on application state context
            if ctx.interaction:
                await ctx.interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(embed=embed, delete_after=5)

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

    # ❗ CLEAN ACTION ERROR HANDLER
    @clear.error
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
                title=f"{self.yes} Clear Command Protocol",
                description=f"{self.arrow} **Global Clear:** `{p}clear 50`\n"
                            f"{self.arrow} **Target Filter:** `{p}clear 50 @user`",
                color=0x2b2d31
            )
            await ctx.send(embed=embed, delete_after=8)
        else:
            await ctx.send(f"{self.cross} **Operational Exception:** Check arguments configuration matrix.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Clear(bot))
    
