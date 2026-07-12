import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_red = "<:starlaDotRed:1525756464692596886>"
        self.dot_green = "<:starlaDotGreen:1525756444782104597>"
        self.ico_mod = "<:starla_ico_mod:1525757006823161897>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 STANDARDIZED PERMISSION CHECK
    def has_ban_perms():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            perms = ctx.author.guild_permissions
            return perms.ban_members or perms.administrator
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

    # 🔨 BAN COMMAND
    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @app_commands.describe(user="Member to ban", reason="Reason for the ban")
    @has_ban_perms()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):

        # 🚨 HIERARCHY & SAFETY CHECKS
        if user.id == ctx.author.id:
            return await ctx.send(f"{self.cross} **Error:** You cannot ban yourself.")

        if user.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} **Error:** You cannot ban the Server Owner.")

        # User vs Executor Hierarchy check
        if ctx.author.id != ctx.guild.owner_id and user.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot ban someone with a higher or equal role.")

        # User vs Bot Hierarchy check
        if user.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user to ban them.")

        case_id = self.get_next_case(ctx.guild.id)

        # 📩 DM NOTIFICATION (Using Info & Caution theme)
        try:
            dm_embed = discord.Embed(
                title=f"{self.ico_mod} Banned from {ctx.guild.name}",
                description=f"{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** #{case_id}",
                color=0xff0000
            )
            await user.send(embed=dm_embed)
        except:
            pass  # User ke DMs closed ho sakte hain

        try:
            await ctx.guild.ban(user, reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Ban", user, ctx.author, reason)

            # 📢 SUCCESS RESPONSE EMBED (Sleek Dark Look)
            embed = discord.Embed(
                description=f"{self.dot_red} **{user.mention} has been banned from the server**",
                color=0x2b2d31  # Modern dark color
            )
            embed.add_field(name=f"{self.ico_info} Details", value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** `#{case_id}`", inline=False)
            embed.set_footer(text=f"Action taken by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} I don't have permission to ban this member.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user by their User ID")
    @app_commands.describe(user_id="The Discord ID of the user to unban", reason="Reason for the unban")
    @has_ban_perms()
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        
        # Parse ID safely
        try:
            uid = int(user_id)
            target_user = await self.bot.fetch_user(uid)
        except (ValueError, discord.NotFound):
            return await ctx.send(f"{self.cross} **Error:** Invalid User ID or user not found.")

        # Check if actually banned
        try:
            await ctx.guild.fetch_ban(target_user)
        except discord.NotFound:
            return await ctx.send(f"{self.cross} This user is not banned in this server.")

        case_id = self.get_next_case(ctx.guild.id)

        try:
            await ctx.guild.unban(target_user, reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Unban", target_user, ctx.author, reason)

            # 📢 SUCCESS UNBAN EMBED
            embed = discord.Embed(
                description=f"{self.dot_green} **{target_user.name}#{target_user.discriminator} has been unbanned**",
                color=0x2b2d31
            )
            embed.add_field(name=f"{self.ico_info} Details", value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** `#{case_id}`", inline=False)
            embed.set_footer(text=f"Action taken by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # ❗ CLEAN & UPGRADED ERROR HANDLER
    @ban.error
    @unban.error
    async def moderation_errors(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You need `Ban Members` or `Administrator` permission to use this command.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I am missing the **Ban Members** permission required for this action.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.cross} **Missing Argument:** Please specify a valid user/ID.")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Ban(bot))
            
