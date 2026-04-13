import discord
from discord.ext import commands
import json
import os

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "cases.json"

    def get_data(self):
        if not os.path.exists(self.db_file):
            return {"case_count": 0, "user_warns": {}}
        with open(self.db_file, "r") as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if member.bot:
            return await ctx.send("❌ You cannot warn a bot.")
        
        data = self.get_data()
        
        # Case ID update
        case_id = data.get("case_count", 0) + 1
        data["case_count"] = case_id
        
        # User warns count update
        user_id = str(member.id)
        if "user_warns" not in data:
            data["user_warns"] = {}
            
        current_warns = data["user_warns"].get(user_id, 0) + 1
        data["user_warns"][user_id] = current_warns
        
        # Case detail save karna
        data[str(case_id)] = {
            "action": "Warn",
            "target": str(member),
            "moderator": str(ctx.author),
            "reason": f"{reason} (Warn #{current_warns})"
        }
        
        self.save_data(data)

        # Photo jaisa response
        await ctx.send(f"✅ **Warned {member.name}** (Case #{case_id}) (user notified with a direct message)")

        # DM Notification
        try:
            await member.send(f"⚠️ You have been warned in **{ctx.guild.name}**\n**Reason:** {reason}\n**Warning Count:** {current_warns}/3\n**Case:** #{case_id}")
        except:
            pass

        # AUTO-KICK LOGIC (3 Warns hone par)
        if current_warns >= 3:
            try:
                await member.kick(reason="Exceeded 3 warnings limit.")
                await ctx.send(f"👢 **{member.name}** has been automatically kicked for reaching 3 warnings.")
                # Warn counter reset kar dena kick ke baad
                data["user_warns"][user_id] = 0
                self.save_data(data)
            except:
                await ctx.send(f"❌ Could not auto-kick {member.name}. Check my permissions.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member: discord.Member):
        data = self.get_data()
        user_id = str(member.id)
        
        if user_id in data.get("user_warns", {}) and data["user_warns"][user_id] > 0:
            data["user_warns"][user_id] -= 1
            self.save_data(data)
            await ctx.send(f"✅ Removed 1 warning from **{member.name}**. Total warns: {data['user_warns'][user_id]}")
        else:
            await ctx.send(f"❌ **{member.name}** has no warnings.")

async def setup(bot):
    await bot.add_cog(Warn(bot))
            
