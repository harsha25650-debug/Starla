import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class Mute(commands.Cog):
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

    @commands.hybrid_command(name="mute", description="Mute a member in the server")
    @app_commands.describe(member="Member to mute", duration="Duration (e.g. 1h)", reason="Reason for the mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = "Indefinite", *, reason: str = "No reason provided"):
        case_id = await self.get_next_case()
        
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await member.add_roles(muted_role)
        self.save_case(case_id, "Mute", member, ctx.author, f"{reason} | Duration: {duration}")
        
        try:
            await member.send(f"🔇 You were muted in **{ctx.guild.name}**\n**Duration:** {duration}\n**Reason:** {reason}\n**Case:** #{case_id}")
        except: pass

        await ctx.send(f"✅ **Muted {member.name}** for **{duration}** (Case #{case_id}) (user notified with a direct message)")

async def setup(bot):
    await bot.add_cog(Mute(bot))
        
