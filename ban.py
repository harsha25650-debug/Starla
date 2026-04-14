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


    # 🔨 BAN COMMAND
    @commands.hybrid_command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban (Optional)")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
        try:
            await member.send(f"🚫 You were banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except:
            pass

        await member.ban(reason=f"Case #{case_id} | {reason}")
        
        self.save_case(case_id, "Ban", member, ctx.author, reason)
        
        await ctx.send(f"✅ **Banned {member.name}** (Case #{case_id}) (user notified with a direct message)")


    # 🔓 UNBAN COMMAND
    @commands.hybrid_command(name="unban", description="Unban a user from the server")
    @app_commands.describe(user="User to unban (ID or name#tag)", reason="Reason for unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: str, *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()

        banned_users = [entry async for entry in ctx.guild.bans()]

        target_user = None

        for ban_entry in banned_users:
            if user == str(ban_entry.user) or user == str(ban_entry.user.id):
                target_user = ban_entry.user
                break

        if target_user is None:
            return await ctx.send("❌ User not found in ban list.")

        # Unban
        await ctx.guild.unban(target_user, reason=f"Case #{case_id} | {reason}")

        # Try DM
        try:
            await target_user.send(f"🥀 You were unbanned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}")
        except:
            pass

        # Save Case
        self.save_case(case_id, "Unban", target_user, ctx.author, reason)

        # Response
        await ctx.send(f"✅ **Unbanned {target_user.name}** (Case #{case_id})")


async def setup(bot):
    await bot.add_cog(Ban(bot))
