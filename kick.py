import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data"
        self.db_file = "./data/cases.json"
        
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({}, f) # Empty dict for guild-based mapping

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
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        # Initialize guild data if it doesn't exist
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

    @commands.hybrid_command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick (Optional)")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            return await ctx.send("❌ You cannot kick yourself.")
        
        # Pass Guild ID to get the correct case number for THIS server
        case_id = await self.get_next_case(ctx.guild.id)
        
        dm_status = ""
        try:
            await member.send(f"👢 You were kicked from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified)"

        try:
            await member.kick(reason=f"Case #{case_id} | {reason}")
            
            # Save using Guild ID
            self.save_case(ctx.guild.id, case_id, "Kick", member, ctx.author, reason)
            
            await ctx.send(f"✅ **Kicked {member.name}** (Case #{case_id}) {dm_status}")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this user (check role hierarchy).")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Kick(bot))
