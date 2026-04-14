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
        # Path for Railway Volume
        self.db_path = "/data"
        self.db_file = "/data/cases.json"
        
        # FIX: Agar folder nahi hai toh bana do
        if not os.path.exists(self.db_path):
            try:
                os.makedirs(self.db_path, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
                # Fallback to local if /data is not accessible
                self.db_file = "cases.json"

        # FIX: Agar file nahi hai toh empty json bana do
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
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
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
        with open(self.db_file, "r") as f:
            data = json.load(f)
        return data.get("case_count", 0) + 1

    @commands.hybrid_command(name="mute", description="Mute a member (Permanent by default)")
    @app_commands.describe(member="Member to mute", duration="Optional: 10m, 1h, etc.", reason="Reason for mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        actual_duration = duration if duration else "Permanent"
        seconds = self.convert_time(duration) if duration else None

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await member.add_roles(muted_role)
        self.save_case(case_id, "Mute", member, ctx.author, f"{reason} | Duration: {actual_duration}")
        
        try:
            await member.send(f"🔇 You were muted in **{ctx.guild.name}**\n**Duration:** {actual_duration}\n**Reason:** {reason}\n**Case:** #{case_id}")
        except: pass

        await ctx.send(f"✅ **Muted {member.name}** | **{actual_duration}** (Case #{case_id}) (user notified with a direct message)")

        if seconds:
            await asyncio.sleep(seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)

async def setup(bot):
    await bot.add_cog(Mute(bot))
        
        
        
