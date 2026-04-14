import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "/data/cases.json"

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

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        try:
            await member.send(f"👢 You were kicked from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except: pass

        await member.kick(reason=f"Case #{case_id} | {reason}")
        self.save_case(case_id, "Kick", member, ctx.author, reason)
        await ctx.send(f"✅ **Kicked {member.name}** (Case #{case_id}) (user notified with a direct message)")

async def setup(bot):
    await bot.add_cog(Kick(bot))
    
        
