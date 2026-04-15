import discord
from discord.ext import commands
from discord import app_commands
import datetime
import re
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 FIXED PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            # Bot Owner ya Server Owner ko allow karein
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            
            perms = ctx.author.guild_permissions
            # Admin, Manage Roles, ya Moderate Members check karein
            return perms.administrator or perms.manage_roles or perms.moderate_members
        return commands.check(predicate)

    # ⏱ TIME CONVERTER
    def convert_time(self, time_str):
        if not time_str:
            return None
        time_str = time_str.lower().strip()
        patterns = {
            r"(\d+)\s*(s|sec|second)": 1,
            r"(\d+)\s*(m|min|minute)": 60,
            r"(\d+)\s*(h|hr|hour)": 3600,
            r"(\d+)\s*(d|day)": 86400
        }
        for pattern, multiplier in patterns.items():
            match = re.match(pattern, time_str)
            if match:
                return int(match.group(1)) * multiplier
        return None

    def get_next_case(self, guild_id):
        path = f"cases.{guild_id}.case_count"
        case_id = self.bot.db.get(path, 0) + 1
        self.bot.db.set(path, case_id)
        return case_id

    def save_case(self, guild_id, case_id, action, target, moderator, reason):
        case_data = {
            "action": action,
            "target_id": target.id,
            "target_name": str(target),
            "moderator": str(moderator),
            "reason": reason,
            "timestamp": str(datetime.datetime.now(datetime.timezone.utc))
        }
        self.bot.db.set(f"cases.{guild_id}.cases.{case_id}", case_data)

    # 🔇 MUTE COMMAND
    @commands.hybrid_command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="e.g. 10m, 5h, 1d", reason="Reason")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True, moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        
        # 🚨 HIERARCHY CHECK
        if member.id == ctx.guild.owner_id:
            return await ctx.send("❌ Main server owner ko mute nahi kar sakta.")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ Hierarchy Error: Mera role is user se niche hai. Mere role ko upar karein.")

        case_id = self.get_next_case(ctx.guild.id)
        display_duration = f"for {duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        action_used = "Mute Role"

        # 🔁 Try timeout first (Modern Discord Mute)
        if seconds and seconds <= 2419200: # 28 days max for timeout
            try:
                until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
                await member.timeout(until, reason=reason)
                action_used = "Timeout"
            except Exception:
                action_used = "Mute Role"

        # 🔇 Role mute fallback
        if action_used == "Mute Role":
            if not muted_role:
                try:
                    muted_role = await ctx.guild.create_role(name="Muted", reason="Mute command setup")
                    for channel in ctx.guild.channels:
                        await channel.set_permissions(muted_role, send_messages=False, speak=False)
                except discord.Forbidden:
                    return await ctx.send("❌ Mere paas 'Manage Roles' permission nahi hai role banane ke liye.")

            await member.add_roles(muted_role, reason=reason)

        self.save_case(ctx.guild.id, case_id, action_used, member, ctx.author, f"{reason} | {display_duration}")

        # Send DM
        try:
            await member.send(f"🔇 You were {action_used.lower()} in **{ctx.guild.name}**\nDuration: {display_duration}\nReason: {reason}")
        except: pass

        embed = discord.Embed(title="🔇 Member Muted", color=discord.Color.orange())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Type", value=action_used, inline=True)
        embed.add_field(name="Duration", value=display_duration, inline=True)
        embed.set_footer(text=f"Case #{case_id} | Moderator: {ctx.author}")
        await ctx.send(embed=embed)

        # ⏳ AUTO UNMUTE
        if seconds and action_used == "Mute Role":
            await asyncio.sleep(seconds)
            if muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Mute duration expired")

    # ❗ ERROR HANDLER
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Sahi format use karein: `!mute <user> [time] [reason]`")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Aapke paas permissions nahi hain.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Mere paas permissions (Manage Roles/Moderate Members) nahi hain.")
        else:
            await ctx.send(f"⚠️ Error: {error}")

async def setup(bot):
    await bot.add_cog(Mute(bot))
