import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Custom Icons
        self.caution = "<a:GF_Caution:1494212827865415730>"
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.success = "<a:greentick:1494180392440303777>"
        self.cross = "<a:spider_cross:1494181311525687347>"

    # 🔐 STANDARDIZED PERMISSION CHECK
    def has_ban_perms():
        async def predicate(ctx):
            # Bot Owner, Server Owner, or Administrator/Ban permission
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
            return await ctx.send(f"{self.cross} You cannot ban yourself.")

        if user.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} You cannot ban the Server Owner.")

        if user.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user.")

        case_id = self.get_next_case(ctx.guild.id)

        # 📩 DM (Using Caution Emoji)
        try:
            await user.send(
                f"{self.caution} **You were banned from {ctx.guild.name}**\n"
                f"**Reason:** {reason}\n"
                f"**Case:** #{case_id}"
            )
        except:
            pass

        try:
            await ctx.guild.ban(user, reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Ban", user, ctx.author, reason)

            # 📢 RESPONSE (Black Embed)
            embed = discord.Embed(
                description=f"{self.loading} **{user.mention} has been banned**",
                color=0x000000
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} I don't have permission to ban this member.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user by ID or Name")
    @has_ban_perms()
    async def unban(self, ctx, user_id: str, *, reason: str = "No reason provided"):
        
        target_user = None
        async for entry in ctx.guild.bans(limit=None):
            if user_id in (str(entry.user.id), str(entry.user)):
                target_user = entry.user
                break

        if not target_user:
            return await ctx.send(f"{self.cross} User not found in the ban list.")

        case_id = self.get_next_case(ctx.guild.id)

        try:
            await ctx.guild.unban(target_user, reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Unban", target_user, ctx.author, reason)

            embed = discord.Embed(
                description=f"{self.success} **{target_user} has been unbanned**",
                color=0x000000
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # ❗ ERROR HANDLER
    @ban.error
    @unban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.cross} **Access denied | owner/premiumUser only command**", 
                color=0x000000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I am missing the **Ban Members** permission.")
        else:
            await ctx.send(f"{self.cross} **Error:** `{error}`")

async def setup(bot):
    await bot.add_cog(Ban(bot))
