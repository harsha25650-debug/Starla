import discord
from discord.ext import commands
import json
import os

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "cases.json"

    def save_case(self, case_id, action, target, moderator, reason):
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        data[str(case_id)] = {
            "action": action,
            "target": str(target),
            "moderator": str(moderator),
            "reason": reason
        }
        data["case_count"] = case_id
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        with open(self.db_file, "r") as f:
            data = json.load(f)
        case_id = data.get("case_count", 0) + 1

        await member.ban(reason=reason)
        self.save_case(case_id, "Ban", member, ctx.author, reason)

        await ctx.send(f"✅ **Banned {member.name}** (Case #{case_id}) (user notified with a DM)")

        try:
            await member.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except:
            pass

async def setup(bot):
    await bot.add_cog(Ban(bot))
    
