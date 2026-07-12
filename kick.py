import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_orange = "<:starlaDotOrange:1525756452487168121>"
        self.ico_bonk = "<:starla_ico_bonk:1525756094776082523>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 STANDARDIZED PERMISSION CHECK
    def has_kick_perms():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            perms = ctx.author.guild_permissions
            return perms.kick_members or perms.administrator
        return commands.check(predicate)

    # 📌 CASE ID SYSTEM
    def get_next_case(self, guild_id):
        path = f"cases.{guild_id}.case_count"
        case_id = self.bot.db.get(path, 0) + 1
        self.bot.db.set(path, case_id)
        return case_id

    def save_case(self, guild_id, case_id, action, target, moderator, reason):
        case_data = {
            "action": action,
            "target_id": target.id,
            "target_name": str(target),
            "moderator": str(moderator),
            "reason": reason,
            "timestamp": str(datetime.datetime.now(datetime.timezone.utc))
        }
        self.bot.db.set(f"cases.{guild_id}.cases.{case_id}", case_data)

    # 👢 KICK COMMAND
    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @has_kick_perms()
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):

        # 🚨 HIERARCHY & SAFETY CHECKS
        if member.id == ctx.author.id:
            return await ctx.send(f"{self.cross} **Error:** You cannot kick yourself.")

        if member.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} **Error:** You cannot kick the Server Owner.")

        # Executor vs Target Hierarchy check
        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot kick someone with a higher or equal role.")

        # Bot vs Target Hierarchy check
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user to kick them.")

        case_id = self.get_next_case(ctx.guild.id)

        # 📩 DM NOTIFICATION (Sleek Clean Style)
        try:
            dm_embed = discord.Embed(
                title=f"{self.ico_bonk} Kicked from {ctx.guild.name}",
                description=f"{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** #{case_id}",
                color=0xffa500
            )
            await member.send(embed=dm_embed)
        except:
            pass  # User ke DMs close ho sakte hain

        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Kick", member, ctx.author, reason)

            # 📢 SUCCESS RESPONSE EMBED (Sleek Modern Dark)
            embed = discord.Embed(
                description=f"{self.dot_orange} **{member.mention} has been kicked from the server**",
                color=0x2b2d31
            )
            embed.add_field(
                name=f"{self.ico_info} Details", 
                value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n"
                      f"{self.arrow} **Reason:** {reason}\n"
                      f"{self.arrow} **Case ID:** `#{case_id}`", 
                inline=False
            )
            embed.set_footer(text=f"Action taken by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} I don't have permission to kick this member.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # ❗ CLEAN UPGRADED ERROR HANDLER
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You need `Kick Members` or `Administrator` permission to use this command.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I am missing the **Kick Members** permission required for this action.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.cross} **Missing Argument:** Please specify a valid member. `!kick <@user> [reason]`")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Kick(bot))
                                                          
