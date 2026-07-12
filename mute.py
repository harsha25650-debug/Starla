import discord
from discord.ext import commands
from discord import app_commands
import datetime
import re
import asyncio

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_yellow = "<:starlaDotYellow:1525756269934411958>"
        self.ico_chat = "<:starla_ico_chat:1525757016461545615>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 FIXED PERMISSION CHECK (Owner & High Staff Bypass)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            perms = ctx.author.guild_permissions
            return perms.administrator or perms.manage_roles or perms.moderate_members
        return commands.check(predicate)

    # ⏱ IMPROVED TIME CONVERTER
    def convert_time(self, time_str):
        if not time_str:
            return None
        time_str = time_str.lower().strip()
        patterns = {
            r"^(\d+)\s*(s|sec|second|seconds)$": 1,
            r"^(\d+)\s*(m|min|minute|minutes)$": 60,
            r"^(\d+)\s*(h|hr|hour|hours)$": 3600,
            r"^(\d+)\s*(d|day|days)$": 86400  # Fixed: 1 day = 86400 seconds
        }
        for pattern, multiplier in patterns.items():
            match = re.match(pattern, time_str)
            if match:
                return int(match.group(1)) * multiplier
        return None

    # 📌 CASE ID SYSTEM
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
    @commands.hybrid_command(name="mute", description="Mute or Timeout a member from the server")
    @app_commands.describe(member="Member to mute", duration="e.g. 10m, 5h, 1d", reason="Reason for the mute")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True, moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):

        # 🚨 HIERARCHY CHECKS
        if member.id == ctx.author.id:
            return await ctx.send(f"{self.cross} **Error:** You cannot mute yourself.")

        if member.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} **Error:** You cannot mute the Server Owner.")

        # Executor vs Target Hierarchy check
        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot mute someone with a higher or equal role.")

        # Bot vs Target Hierarchy check
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user to mute them.")

        case_id = self.get_next_case(ctx.guild.id)
        display_duration = f"{duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None
        
        action_used = "Mute"
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        # 🔁 Modern Discord Timeout Try (Max 28 days limit check)
        if seconds and seconds <= 2419200:
            try:
                until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
                await member.timeout(until, reason=f"Case #{case_id} | {reason}")
                action_used = "Timeout"
            except:
                action_used = "Mute Role"
        else:
            action_used = "Mute Role"

        # 🔇 Role Mute Fallback
        if action_used == "Mute Role":
            if not muted_role:
                try:
                    muted_role = await ctx.guild.create_role(name="Muted", reason="Automatic Mute Setup")
                    for channel in ctx.guild.channels:
                        await channel.set_permissions(muted_role, send_messages=False, speak=False)
                except discord.Forbidden:
                    return await ctx.send(f"{self.cross} **Error:** I don't have permission to create the 'Muted' role.")

            await member.add_roles(muted_role, reason=f"Case #{case_id} | {reason}")

        # 💾 SAVE TO DATABASE
        self.save_case(ctx.guild.id, case_id, action_used, member, ctx.author, f"{reason} (Duration: {display_duration})")

        # 📩 DM NOTIFICATION
        try:
            dm_embed = discord.Embed(
                title=f"{self.ico_chat} Muted in {ctx.guild.name}",
                description=f"{self.arrow} **Type:** {action_used}\n{self.arrow} **Duration:** {display_duration}\n{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** #{case_id}",
                color=0xffcc00
            )
            await member.send(embed=dm_embed)
        except:
            pass

        # 📢 SUCCESS RESPONSE EMBED
        embed = discord.Embed(
            description=f"{self.dot_yellow} **{member.mention} has been successfully muted**",
            color=0x2b2d31
        )
        embed.add_field(
            name=f"{self.ico_info} Details", 
            value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n"
                  f"{self.arrow} **Type:** `{action_used}`\n"
                  f"{self.arrow} **Duration:** `{display_duration}`\n"
                  f"{self.arrow} **Case ID:** `#{case_id}`", 
            inline=True
        )
        embed.add_field(name="Reason", value=f"```{reason}```", inline=False)
        embed.set_footer(text=f"Action by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await ctx.send(embed=embed)

        # ⏳ AUTO UNMUTE FOR OLD-SCHOOL ROLE MUTE
        if seconds and action_used == "Mute Role":
            await asyncio.sleep(seconds)
            # Fetch latest data to verify role presence
            try:
                if muted_role in member.roles:
                    await member.remove_roles(muted_role, reason="Mute duration automatically expired.")
            except:
                pass

    # ❗ CLEAN ERROR HANDLER
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.cross} **Usage Error:** Please mention a valid user. `!mute <@user> [duration] [reason]`")
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You don't have permissions (`Moderate Members` / `Manage Roles`) to run this command.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I need `Manage Roles` and `Moderate Members` permissions to execute this.")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Mute(bot))
    
