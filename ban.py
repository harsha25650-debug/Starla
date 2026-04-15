import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True
            return ctx.author.guild_permissions.ban_members
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

    # 🔨 BAN COMMAND
    @commands.hybrid_command(name="ban", description="Ban a user")
    @app_commands.describe(user="User to ban", reason="Reason")
    @has_perm_or_owner()
    async def ban(self, ctx, user: discord.User, *, reason: str = "No reason provided"):

        if user.id == ctx.author.id:
            return await ctx.send("❌ You cannot ban yourself.")

        # already banned check
        try:
            await ctx.guild.fetch_ban(user)
            return await ctx.send(f"❌ {user} is already banned.")
        except discord.NotFound:
            pass

        case_id = self.get_next_case(ctx.guild.id)

        # DM
        try:
            await user.send(
                f"🚫 You were banned from **{ctx.guild.name}**\n"
                f"Reason: {reason}\n"
                f"Case: #{case_id}"
            )
        except:
            pass

        try:
            await ctx.guild.ban(user, reason=f"Case #{case_id} | {reason}")

            # 💾 SAVE CASE
            self.save_case(ctx.guild.id, case_id, "Ban", user, ctx.author, reason)

            embed = discord.Embed(
                title="🚫 User Banned",
                description=f"{user} has been banned",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission or target is higher.")
        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user")
    @app_commands.describe(user="User ID or Name#Tag", reason="Reason")
    @has_perm_or_owner()
    async def unban(self, ctx, user: str, *, reason: str = "No reason provided"):

        case_id = self.get_next_case(ctx.guild.id)

        banned_users = [entry async for entry in ctx.guild.bans()]
        target_user = None

        for ban_entry in banned_users:
            if (
                user == str(ban_entry.user)
                or user == str(ban_entry.user.id)
                or user.lower() == ban_entry.user.name.lower()
            ):
                target_user = ban_entry.user
                break

        if target_user is None:
            return await ctx.send("❌ User not found in ban list.")

        try:
            await ctx.guild.unban(target_user, reason=f"Case #{case_id} | {reason}")

            # 💾 SAVE CASE
            self.save_case(ctx.guild.id, case_id, "Unban", target_user, ctx.author, reason)

            embed = discord.Embed(
                title="🔓 User Unbanned",
                description=f"{target_user} has been unbanned",
                color=discord.Color.green()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban.")

    # ❗ ERROR HANDLER
    @ban.error
    @unban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission.")
        else:
            await ctx.send("⚠️ Error occurred. Check permissions / hierarchy.")

async def setup(bot):
    await bot.add_cog(Ban(bot))
