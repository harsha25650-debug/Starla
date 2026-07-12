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
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.ico_chat = "<:starla_ico_chat:1525757016461545615>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            perms = ctx.author.guild_permissions
            return perms.administrator or perms.manage_roles or perms.moderate_members
        return commands.check(predicate)

    # ⏱ TIME CONVERTER
    def convert_time(self, time_str):
        if not time_str:
            return None
        time_str = time_str.lower().strip()
        patterns = {
            r"^(\d+)\s*(s|sec|second|seconds)$": 1,
            r"^(\d+)\s*(m|min|minute|minutes)$": 60,
            r"^(\d+)\s*(h|hr|hour|hours)$": 3600,
            r"^(\d+)\s*(d|day|days)$": 86400
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

    # 🛠️ HELPER: MUTED ROLE CREATOR & PERMISSIONS OVERRIDE
    async def configure_muted_role(self, ctx):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            try:
                # Create role with zero permissions by default
                muted_role = await ctx.guild.create_role(
                    name="Muted", 
                    reason="Starla Automatic Mute Setup",
                    permissions=discord.Permissions.none()
                )
                # Override channels permissions
                for channel in ctx.guild.channels:
                    try:
                        if isinstance(channel, discord.TextChannel):
                            await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(muted_role, speak=False, connect=False)
                    except Exception:
                        continue
            except discord.Forbidden:
                return None
        return muted_role

    # 🔨 COMMAND: MANUAL MUTE ROLE SETUP
    @commands.hybrid_command(name="muterole", description="Manually creates and configures the 'Muted' role overrides.")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole(self, ctx):
        existing_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if existing_role:
            return await ctx.send(f"{self.cross} **Error:** A role named `Muted` already exists in this server.")
        
        status_msg = await ctx.send(f"{self.dot_blue} Initializing 'Muted' role matrix configuration...")
        role = await self.configure_muted_role(ctx)
        
        if role:
            await status_msg.edit(content=f"{self.yes} **Success:** `Muted` role created and all channel permissions overridden completely.")
        else:
            await status_msg.edit(content=f"{self.cross} **Failed:** Missing authorization power or role hierarchy restriction.")

    # 🔇 COMMAND: MUTE
    @commands.hybrid_command(name="mute", description="Mute a member via Muted role strategy")
    @app_commands.describe(member="Member to mute", duration="e.g. 10m, 5h, 1d (Optional)", reason="Reason for the mute")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):

        # 🚨 HIERARCHY CHECKS
        if member.id == ctx.author.id:
            return await ctx.send(f"{self.cross} **Error:** You cannot mute yourself.")

        if member.id == ctx.guild.owner_id:
            return await ctx.send(f"{self.cross} **Error:** You cannot mute the Server Owner.")

        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot mute someone with a higher or equal role.")

        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My role must be higher than this user.")

        # Fetch or auto-create the role
        muted_role = await self.configure_muted_role(ctx)
        if not muted_role:
            return await ctx.send(f"{self.cross} **Permissions Error:** I could not build or trace the `Muted` role structure.")

        if muted_role in member.roles:
            return await ctx.send(f"{self.cross} **Status Alert:** This user is already assigned to the `Muted` role matrix.")

        case_id = self.get_next_case(ctx.guild.id)
        display_duration = f"{duration}" if duration else "permanently"
        seconds = self.convert_time(duration) if duration else None

        # Add role
        await member.add_roles(muted_role, reason=f"Case #{case_id} | {reason}")
        self.save_case(ctx.guild.id, case_id, "Mute", member, ctx.author, f"{reason} (Duration: {display_duration})")

        # 📩 DM
        try:
            dm_embed = discord.Embed(
                title=f"{self.ico_chat} Muted in {ctx.guild.name}",
                description=f"{self.arrow} **Duration:** {display_duration}\n{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** #{case_id}",
                color=0xffcc00
            )
            await member.send(embed=dm_embed)
        except Exception:
            pass

        # 📢 SUCCESS EMBED
        embed = discord.Embed(
            description=f"{self.dot_yellow} **{member.mention} has been successfully assigned to the Muted grid**",
            color=0x2b2d31
        )
        embed.add_field(
            name=f"{self.ico_info} Details", 
            value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n"
                  f"{self.arrow} **Duration:** `{display_duration}`\n"
                  f"{self.arrow} **Case ID:** `#{case_id}`", 
            inline=True
        )
        embed.add_field(name="Reason", value=f"```{reason}```", inline=False)
        embed.set_footer(text=f"Action by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await ctx.send(embed=embed)

        # ⏳ AUTOMATIC DURATIONAL UNMUTE PIPELINE
        if seconds:
            await asyncio.sleep(seconds)
            try:
                # Fresh cache check to avoid unmuting if re-muted or manually removed
                if muted_role in member.roles:
                    await member.remove_roles(muted_role, reason="Mute temporal schedule expired.")
                    
                    # Optional: Silent trace/log for unmuted action
                    unmute_case = self.get_next_case(ctx.guild.id)
                    self.save_case(ctx.guild.id, unmute_case, "Auto-Unmute", member, ctx.guild.me, "Duration expired.")
            except Exception:
                pass

    # 🔊 COMMAND: UNMUTE
    @commands.hybrid_command(name="unmute", description="Strip the Muted role from a member")
    @app_commands.describe(member="Member to unmute", reason="Reason for the unmute")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        
        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** Target user's role hierarchy is above your clearance.")
            
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** My integration layer is below this user's top role.")

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            return await ctx.send(f"{self.cross} **Error:** Target member is not currently restricted by the Muted role.")

        case_id = self.get_next_case(ctx.guild.id)
        await member.remove_roles(muted_role, reason=f"Case #{case_id} | {reason}")
        self.save_case(ctx.guild.id, case_id, "Unmute", member, ctx.author, reason)

        # 📩 DM
        try:
            dm_embed = discord.Embed(
                title=f"{self.ico_chat} Unmuted in {ctx.guild.name}",
                description=f"{self.arrow} **Reason:** {reason}\n{self.arrow} **Case ID:** #{case_id}",
                color=0x00ff00
            )
            await member.send(embed=dm_embed)
        except Exception:
            pass

        # 📢 RESPONSE EMBED
        embed = discord.Embed(
            description=f"{self.dot_blue} **{member.mention} has been successfully unmuted**",
            color=0x2b2d31
        )
        embed.add_field(
            name=f"{self.ico_info} Details", 
            value=f"{self.arrow} **Moderator:** {ctx.author.mention}\n"
                  f"{self.arrow} **Case ID:** `#{case_id}`", 
            inline=True
        )
        embed.add_field(name="Reason", value=f"```{reason}```", inline=False)
        embed.set_footer(text=f"Action by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await ctx.send(embed=embed)

    # ❗ SYSTEM ERROR HANDLER
    @mute.error
    @unmute.error
    @muterole.error
    async def mute_cog_errors(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.cross} **Usage Error:** Target parameter missing. Use `!mute/!unmute <@user>`")
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** Missing `Manage Roles` or `Moderate Members` permissions token.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} **Permissions Fault:** Client requires `Manage Roles` access privilege.")
        else:
            await ctx.send(f"{self.cross} **Operational Exception:** `{error}`")

async def setup(bot):
    await bot.add_cog(Mute(bot))
        
