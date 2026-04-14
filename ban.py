import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Ban(commands.Cog):
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

    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban (Optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
        # Notify User
        try:
            await member.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except: pass

        # Perform Ban
        await member.ban(reason=f"Case #{case_id} | {reason}")
        
        # Save to Database
        self.save_case(case_id, "Ban", member, ctx.author, reason)
        
        # Zeppelin Style Response
        await ctx.send(f"✅ **Banned {member.name}** (Case #{case_id}) (user notified with a direct message)")

async def setup(bot):
    await bot.add_cog(Ban(bot))
                           
    
    
