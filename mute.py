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
                json.dump({"case_count": 0}, f)

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

    def save_case(self, case_id, action, target, moderator, reason):
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
        except:
            data = {"case_count": 0}
        
        data[str(case_id)] = {
            "action": action,
            "target_id": target.id,
            "target_name": str(target),
            "moderator": str(moderator),
            "reason": reason,
            "timestamp": str(datetime.datetime.now(datetime.timezone.utc))
        }
        data["case_count"] = case_id
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    async def get_next_case(self):
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            return data.get("case_count", 0) + 1
        except:
            return 1

    @commands.hybrid_command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="Example: 10m, 5h, 1d", reason="Reason for mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
        display_duration = f"for {duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await member.add_roles(muted_role)
        self.save_case(case_id, "Mute", member, ctx.author, f"{reason} | Duration: {display_duration}")
        
        dm_status = ""
        try:
            await member.send(f"🔇 You were muted in **{ctx.guild.name}**\n**Duration:** {display_duration}\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified via DM)"

        await ctx.send(f"✅ **Muted {member.name}** {display_duration} (Case #{case_id}) {dm_status}")

        if seconds:
            await asyncio.sleep(seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)

    @commands.hybrid_command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute", reason="Reason for unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role or muted_role not in member.roles:
            return await ctx.send("❌ This user is not muted.")

        case_id = await self.get_next_case()
        await member.remove_roles(muted_role)
        self.save_case(case_id, "Unmute", member, ctx.author, reason)

        await ctx.send(f"✅ **Unmuted {member.name}** (Case #{case_id})")

async def setup(bot):
    await bot.add_cog(Mute(bot))
