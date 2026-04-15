import discord
from discord.ext import commands
from discord import app_commands
import datetime
import re
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True

            perms = ctx.author.guild_permissions
            return perms.manage_roles or perms.moderate_members

        return commands.check(predicate)

    # ⏱ TIME CONVERTER
    def convert_time(self, time_str):
        if not time_str:
            return None

        time_str = time_str.lower().strip()
        patterns = {
            r"(\d+)\s*(s|sec|second)": 1,
            r"(\d+)\s*(m|min|minute)": 60,
            r"(\d+)\s*(h|hr|hour)": 3600,
            r"(\d+)\s*(d|day)": 86400
        }

        for pattern, multiplier in patterns.items():
            match = re.match(pattern, time_str)
            if match:
                return int(match.group(1)) * multiplier

        return None

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

    # 🔇 MUTE COMMAND
    @commands.hybrid_command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="10m, 5h, 1d", reason="Reason")
    @has_perm_or_owner()
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):

        case_id = self.get_next_case(ctx.guild.id)

        display_duration = f"for {duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        # 🔁 Try timeout first
        if ctx.author.guild_permissions.moderate_members:
            try:
                if seconds:
                    until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
                    await member.timeout(until, reason=reason)
                else:
                    await member.timeout(datetime.timedelta(days=28), reason=reason)

                action_used = "Timeout"
            except:
                action_used = "Mute Role"
        else:
            action_used = "Mute Role"

        # 🔇 Role mute fallback
        if action_used == "Mute Role":
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")

                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)

            await member.add_roles(muted_role)

        # 💾 SAVE CASE
        self.save_case(ctx.guild.id, case_id, action_used, member, ctx.author, f"{reason} | Duration: {display_duration}")

        # 📩 DM
        try:
            await member.send(
                f"🔇 You were {action_used.lower()} in **{ctx.guild.name}**\n"
                f"Duration: {display_duration}\n"
                f"Reason: {reason}\n"
                f"Case: #{case_id}"
            )
        except:
            pass

        # 📢 RESPONSE
        embed = discord.Embed(
            title="🔇 Member Muted",
            description=f"{member.mention} has been **{action_used.lower()}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Duration", value=display_duration, inline=True)
        embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

        # ⏳ AUTO UNMUTE (only role mute)
        if seconds and action_used == "Mute Role":
            await asyncio.sleep(seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)

    # 🔊 UNMUTE
    @commands.hybrid_command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute", reason="Reason")
    @has_perm_or_owner()
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        case_id = self.get_next_case(ctx.guild.id)

        # remove timeout
        try:
            await member.timeout(None)
        except:
            pass

        # remove role
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)

        # 💾 SAVE CASE
        self.save_case(ctx.guild.id, case_id, "Unmute", member, ctx.author, reason)

        embed = discord.Embed(
            title="🔊 Member Unmuted",
            description=f"{member.mention} has been unmuted",
            color=discord.Color.green()
        )
        embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ❗ ERROR HANDLER
    @mute.error
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission.")
        else:
            await ctx.send("⚠️ Error occurred. Check permissions / hierarchy.")

async def setup(bot):
    await bot.add_cog(Mute(bot))
