import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "./data"
        self.db_file = "./data/cases.json"
        
        # Ensure the directory and file exist
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

    # 🔨 BAN COMMAND
    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban (Optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            return await ctx.send("❌ You cannot ban yourself.")
        
        case_id = await self.get_next_case()
        
        dm_status = ""
        try:
            await member.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified)"

        try:
            await member.ban(reason=f"Case #{case_id} | {reason}")
            self.save_case(case_id, "Ban", member, ctx.author, reason)
            await ctx.send(f"✅ **Banned {member.name}** (Case #{case_id}) {dm_status}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this user.")

    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user from the server")
    @app_commands.describe(user="User ID or Name#Tag", reason="Reason for unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
        # Fetch ban list
        banned_users = [entry async for entry in ctx.guild.bans()]
        target_user = None

        for ban_entry in banned_users:
            if user == str(ban_entry.user) or user == str(ban_entry.user.id) or user == ban_entry.user.name:
                target_user = ban_entry.user
                break

        if target_user is None:
            return await ctx.send("❌ User not found in server ban list.")

        try:
            await ctx.guild.unban(target_user, reason=f"Case #{case_id} | {reason}")
            
            # Try to DM the user (often fails as they aren't in the server)
            try:
                await target_user.send(f"🥀 You were unbanned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            except:
                pass

            self.save_case(case_id, "Unban", target_user, ctx.author, reason)
            await ctx.send(f"✅ **Unbanned {target_user.name}** (Case #{case_id})")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

async def setup(bot):
    await bot.add_cog(Ban(bot))
    
