import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Custom Icons
        self.caution = "<:spider_okjinwoo:1494216934613319691>"
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.success = "<a:greentick:1494180392440303777>"
        self.cross = "<a:spider_cross:1494181311525687347>"

    # 🔐 STANDARDIZED PERMISSION CHECK
    def has_kick_perms():
        async def predicate(ctx):
            # Allow Bot Owner, Server Owner, or users with Administrator/Kick Members
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
            return await ctx.send(f"{self.cross} You cannot kick yourself.")

        if member.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} You cannot kick the Server Owner.")

        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user.")

        case_id = self.get_next_case(ctx.guild.id)

        # 📩 DM (Using requested OkJinwoo emoji)
        try:
            await member.send(
                f"{self.caution} **You were kicked from {ctx.guild.name}**\n"
                f"**Reason:** {reason}\n"
                f"**Case:** #{case_id}"
            )
        except:
            pass

        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")
            self.save_case(ctx.guild.id, case_id, "Kick", member, ctx.author, reason)

            # 📢 RESPONSE (Black Embed)
            embed = discord.Embed(
                description=f"{self.loading} **{member.mention} has been kicked**",
                color=0x000000
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} I don't have permission to kick this member.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Error:** `{e}`")

    # ❗ ERROR HANDLER
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.cross} **Access denied | owner/premiumUser only command**", 
                color=0x000000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I am missing the **Kick Members** permission.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.cross} **Usage:** `!kick <@user> [reason]`")
        else:
            await ctx.send(f"{self.cross} **Error:** `{error}`")

async def setup(bot):
    await bot.add_cog(Kick(bot))
