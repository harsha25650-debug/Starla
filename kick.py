import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Path configuration to avoid permission errors
        self.db_path = "./data"
        self.db_file = "./data/cases.json"
        
        # Ensure the directory and file exist on startup
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({"case_count": 0}, f)

    def save_case(self, case_id, action, target, moderator, reason):
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
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

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick (Optional)")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        # Prevent the bot from kicking itself or the user kicking themselves
        if member.id == ctx.author.id:
            return await ctx.send("❌ You cannot kick yourself.")
        
        case_id = await self.get_next_case()
        
        # Handle DM Notification
        dm_status = ""
        try:
            await member.send(f"👢 You were kicked from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified)"

        # Perform the actual kick
        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")
            
            # Save the case to JSON only if the kick was successful
            self.save_case(case_id, "Kick", member, ctx.author, reason)
            
            # Output matching the Zeppelin style from your image
            await ctx.send(f"✅ **Kicked {member.name}** (Case #{case_id}) {dm_status}")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this user (check role hierarchy).")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Kick(bot))
    
