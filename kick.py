import discord
from discord.ext import commands
import json
import os

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "cases.json"

    def save_case(self, case_id, action, target, moderator, reason):
        # Database load aur update karne ke liye logic
        if not os.path.exists(self.db_file):
            data = {"case_count": 0}
        else:
            with open(self.db_file, "r") as f:
                data = json.load(f)
        
        data[str(case_id)] = {
            "action": action,
            "target": f"{target.name}#{target.discriminator}" if hasattr(target, 'discriminator') else str(target),
            "moderator": str(moderator),
            "reason": reason
        }
        data["case_count"] = case_id
        
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        # Case ID counter check
        if not os.path.exists(self.db_file):
            case_id = 1
        else:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            case_id = data.get("case_count", 0) + 1

        # Self kick aur bot kick check
        if member == ctx.author:
            return await ctx.send("❌ You cannot kick yourself!")
        
        # DM notification photo ki tarah
        try:
            await member.send(f"👢 You have been kicked from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except:
            pass

        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")
            
            # Database mein save karna
            self.save_case(case_id, "Kick", member, ctx.author, reason)

            # Server response bilkul Zeppelin style
            await ctx.send(f"✅ **Kicked {member.name}** (Case #{case_id}) (user notified with a direct message)")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this user.")

async def setup(bot):
    await bot.add_cog(Kick(bot))
        
