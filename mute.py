import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
import re
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data"
        self.db_file = "./data/cases.json"
        
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({}, f)

    # 🔐 PERMISSION CHECK (OWNER BYPASS + ROLE/TIMEOUT)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True

            perms = ctx.author.guild_permissions
            return perms.manage_roles or perms.moderate_members

        return commands.check(predicate)

    def convert_time(self, time_str):
        if not time_str: return None
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

    async def get_next_case(self, guild_id):
        guild_id = str(guild_id)
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            return data.get(guild_id, {}).get("case_count", 0) + 1
        except:
            return 1

    def save_case(self, guild_id, case_id, action, target, moderator, reason):
        guild_id = str(guild_id)
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
        except:
            data = {}

        if guild_id not in data:
            data[guild_id] = {"case_count": 0, "cases": {}}

        data[guild_id]["cases"][str(case_id)] = {
            "action": action,
            "target_id": target.id,
            "target_name": str(target),
            "moderator": str(moderator),
            "reason": reason,
            "timestamp": str(datetime.datetime.now(datetime.timezone.utc))
        }
        data[guild_id]["case_count"] = case_id
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    # 🔇 MUTE COMMAND
    @commands.hybrid_command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="Example: 10m, 5h, 1d", reason="Reason for mute")
    @has_perm_or_owner()
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):

        case_id = await self.get_next_case(ctx.guild.id)

        display_duration = f"for {duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        # 🔁 If user has timeout permission → use timeout
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

        # 🔇 fallback to muted role
        if action_used == "Mute Role":
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False)

            await member.add_roles(muted_role)

        self.save_case(ctx.guild.id, case_id, action_used, member, ctx.author, f"{reason} | Duration: {display_duration}")

        try:
            await member.send(
                f"🔇 You were {action_used.lower()} in **{ctx.guild.name}**\n"
                f"**Duration:** {display_duration}\n"
                f"**Reason:** {reason}\n"
                f"**Case:** #{case_id}"
            )
        except:
            pass

        await ctx.send(f"✅ **{action_used} {member.name}** {display_duration} (Case #{case_id})")

        # ⏳ auto unmute for role mute
        if seconds and action_used == "Mute Role":
            await asyncio.sleep(seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)

    # 🔊 UNMUTE
    @commands.hybrid_command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute", reason="Reason for unmute")
    @has_perm_or_owner()
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        case_id = await self.get_next_case(ctx.guild.id)

        # remove timeout if exists
        try:
            await member.timeout(None)
        except:
            pass

        # remove role mute
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)

        self.save_case(ctx.guild.id, case_id, "Unmute", member, ctx.author, reason)

        await ctx.send(f"✅ **Unmuted {member.name}** (Case #{case_id})")

    # ❗ ERROR HANDLER
    @mute.error
    @unmute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send("⚠️ Error occurred. Check permissions / role hierarchy.")

async def setup(bot):
    await bot.add_cog(Mute(bot))
