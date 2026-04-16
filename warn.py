import discord
from discord.ext import commands
import datetime

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Custom Emojis
        self.caution_icon = "<a:GF_Caution:1494212827865415730>"
        self.loading_icon = "<a:spider_red_dot:1494179666133516411>"
        self.success_icon = "<a:greentick:1494180392440303777>"
        self.cross_icon = "<a:spider_cross:1494181311525687347>"

    # 🔐 PERMISSION CHECK (Owner Bypass)
    def has_mod_perms():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            return ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)

    # 📌 GET NEXT CASE ID
    def get_next_case(self, guild_id):
        path = f"cases.{guild_id}.case_count"
        case_id = self.bot.db.get(path, 0) + 1
        self.bot.db.set(path, case_id)
        return case_id

    # 💾 SAVE CASE
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

    # ⚠️ WARN COMMAND
    @commands.hybrid_command(name="warn", description="Warn a user")
    @has_mod_perms()
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member.bot:
            return await ctx.send(f"{self.cross_icon} You cannot warn a bot.")
        
        if member.id == ctx.author.id:
            return await ctx.send(f"{self.cross_icon} You cannot warn yourself.")

        guild_id = ctx.guild.id
        user_id = str(member.id)

        # 🔢 WARN COUNT
        warns = self.bot.db.get(f"warns.{guild_id}.{user_id}", 0) + 1
        self.bot.db.set(f"warns.{guild_id}.{user_id}", warns)

        # 📌 CASE ID
        case_id = self.get_next_case(guild_id)

        # 💾 SAVE CASE
        self.save_case(guild_id, case_id, "Warn", member, ctx.author, f"{reason} (Warn #{warns})")

        # 📢 EMBED RESPONSE (Black Theme)
        embed = discord.Embed(
            description=f"{self.loading_icon} **{member.mention} has been warned**",
            color=0x000000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Warnings", value=f"`{warns}/3`", inline=True)
        embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

        # 📩 DM (With Caution Emoji)
        try:
            await member.send(
                f"{self.caution_icon} **You were warned in {ctx.guild.name}**\n"
                f"**Reason:** {reason}\n"
                f"**Total Warnings:** {warns}/3\n"
                f"**Case:** #{case_id}"
            )
        except:
            pass

        # 👢 AUTO KICK (3 WARNS)
        if warns >= 3:
            try:
                if member.top_role < ctx.guild.me.top_role:
                    await member.kick(reason="Exceeded 3 warnings")
                    kick_case = self.get_next_case(guild_id)
                    self.save_case(guild_id, kick_case, "Auto Kick", member, "System", "Reached 3 warnings")
                    self.bot.db.set(f"warns.{guild_id}.{user_id}", 0)
                    await ctx.send(f" **{member.mention} has been auto-kicked (3/3 warnings).**")
                else:
                    await ctx.send(f"{self.cross_icon} Cannot auto-kick {member.mention} due to role hierarchy.")
            except:
                await ctx.send(f"{self.cross_icon} Failed to auto-kick. Check my permissions.")

    # 🔻 UNWARN
    @commands.hybrid_command(name="unwarn", description="Remove a warning")
    @has_mod_perms()
    async def unwarn(self, ctx, member: discord.Member):
        guild_id = ctx.guild.id
        user_id = str(member.id)
        warns = self.bot.db.get(f"warns.{guild_id}.{user_id}", 0)

        if warns <= 0:
            return await ctx.send(embed=discord.Embed(description=f"{self.cross_icon} {member.mention} has no warnings.", color=0x000000))

        warns -= 1
        self.bot.db.set(f"warns.{guild_id}.{user_id}", warns)

        embed = discord.Embed(
            description=f"{self.success_icon} **Removed 1 warning from {member.mention}**",
            color=0x000000
        )
        embed.add_field(name="Current Warns", value=f"`{warns}/3`")
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ❗ ERROR HANDLER
    @warn.error
    @unwarn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.cross_icon} **Access denied | owner/premiumUser only command**", 
                color=0x000000
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.cross_icon} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Warn(bot))
    
