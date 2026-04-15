import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True
            return ctx.author.guild_permissions.kick_members
        return commands.check(predicate)

    # 📌 GET NEXT CASE ID
    def get_next_case(self, guild_id):
        path = f"cases.{guild_id}.case_count"
        case_id = self.bot.db.get(path, 0) + 1
        self.bot.db.set(path, case_id)
        return case_id

    # 💾 SAVE CASE
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
    @commands.hybrid_command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @has_perm_or_owner()
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):

        if member.id == ctx.author.id:
            return await ctx.send("❌ You cannot kick yourself.")

        # 🚨 ROLE CHECK
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot kick this user (role hierarchy issue).")

        case_id = self.get_next_case(ctx.guild.id)

        # 📩 DM
        try:
            await member.send(
                f"👢 You were kicked from **{ctx.guild.name}**\n"
                f"Reason: {reason}\n"
                f"Case: #{case_id}"
            )
        except:
            pass

        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")

            # 💾 SAVE CASE
            self.save_case(ctx.guild.id, case_id, "Kick", member, ctx.author, reason)

            # 🎨 EMBED
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"{member.mention} has been kicked",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission.")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    # ❗ ERROR HANDLER
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Kick(bot))
