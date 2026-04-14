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
                json.dump({}, f) # Empty dictionary for guild-based mapping

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

    # 🔨 BAN COMMAND
    @commands.hybrid_command(name="ban", description="Ban a user (works with ID even if they aren't in the server)")
    @app_commands.describe(user="User to ban (ID or @mention)", reason="Reason for the ban (Optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason: str = "No reason provided"):
        if user.id == ctx.author.id:
            return await ctx.send("❌ You cannot ban yourself.")
        
        try:
            await ctx.guild.fetch_ban(user)
            return await ctx.send(f"❌ **{user.name}** is already banned.")
        except discord.NotFound:
            pass

        # Pass Guild ID to get the correct case number
        case_id = await self.get_next_case(ctx.guild.id)
        
        dm_status = ""
        try:
            await user.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
            dm_status = "(user notified with a direct message)"
        except:
            dm_status = "(user could not be notified)"

        try:
            await ctx.guild.ban(user, reason=f"Case #{case_id} | {reason}")
            # Save using Guild ID
            self.save_case(ctx.guild.id, case_id, "Ban", user, ctx.author, reason)
            
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
        # Pass Guild ID to get the correct case number
        case_id = await self.get_next_case(ctx.guild.id)
        
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
            # Save using Guild ID
            self.save_case(ctx.guild.id, case_id, "Unban", target_user, ctx.author, reason)
            await ctx.send(f"✅ **Unbanned {target_user.name}** (Case #{case_id})")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban users.")

async def setup(bot):
    await bot.add_cog(Ban(bot))
