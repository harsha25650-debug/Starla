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

    # 🔨 UPDATED BAN COMMAND (Works for IDs of people not in server)
    @commands.hybrid_command(name="ban", description="Ban a user (works with ID even if they aren't in the server)")
    @app_commands.describe(user="User to ban (ID or @mention)", reason="Reason for the ban (Optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason: str = "No reason provided"):
        if user.id == ctx.author.id:
            return await ctx.send("❌ You cannot ban yourself.")
        
        # Check if user is already banned to prevent duplicate cases
        try:
            await ctx.guild.fetch_ban(user)
            return await ctx.send(f"❌ **{user.name}** is already banned.")
        except discord.NotFound:
            pass

        case_id = await self.get_next_case()
        
        # DM Notification (Will only work if they share a server with the bot)
        dm_status = ""
        try:
            await user.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified)"

        try:
            # Using ctx.guild.ban because 'user' is a discord.User object
            await ctx.guild.ban(user, reason=f"Case #{case_id} | {reason}")
            self.save_case(case_id, "Ban", user, ctx.author, reason)
            
            await ctx.send(f"✅ **Banned {user.name}** (Case #{case_id}) {dm_status}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this user.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user from the server")
    @app_commands.describe(user="User ID or Name#Tag", reason="Reason for unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
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
            self.save_case(case_id, "Unban", target_user, ctx.author, reason)
            await ctx.send(f"✅ **Unbanned {target_user.name}** (Case #{case_id})")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

async def setup(bot):
    await bot.add_cog(Ban(bot))
    
