import discord
from discord.ext import commands
import datetime

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member.bot:
            return await ctx.send("❌ You cannot warn a bot.")

        guild_id = ctx.guild.id
        user_id = str(member.id)

        # 🔢 WARN COUNT
        warns = self.bot.db.get(f"warns.{guild_id}.{user_id}", 0) + 1
        self.bot.db.set(f"warns.{guild_id}.{user_id}", warns)

        # 📌 CASE ID
        case_id = self.get_next_case(guild_id)

        # 💾 SAVE CASE
        self.save_case(guild_id, case_id, "Warn", member, ctx.author, f"{reason} (Warn #{warns})")

        # 📢 EMBED RESPONSE
        embed = discord.Embed(
            title="⚠️ User Warned",
            description=f"{member.mention} has been warned",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Warnings", value=f"{warns}/3", inline=True)
        embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

        # 📩 DM
        try:
            await member.send(
                f"⚠️ You were warned in **{ctx.guild.name}**\n"
                f"Reason: {reason}\n"
                f"Warnings: {warns}/3\n"
                f"Case: #{case_id}"
            )
        except:
            pass

        # 👢 AUTO KICK (3 WARNS)
        if warns >= 3:
            try:
                await member.kick(reason="Exceeded 3 warnings")

                kick_case = self.get_next_case(guild_id)
                self.save_case(guild_id, kick_case, "Auto Kick", member, ctx.author, "Exceeded 3 warnings")

                self.bot.db.set(f"warns.{guild_id}.{user_id}", 0)

                await ctx.send(f"👢 {member.mention} was kicked for reaching 3 warnings.")

            except:
                await ctx.send("❌ Failed to auto-kick. Check permissions.")

    # 🔻 UNWARN
    @commands.hybrid_command(name="unwarn", description="Remove a warning")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, member: discord.Member):

        guild_id = ctx.guild.id
        user_id = str(member.id)

        warns = self.bot.db.get(f"warns.{guild_id}.{user_id}", 0)

        if warns <= 0:
            return await ctx.send(f"❌ {member.mention} has no warnings.")

        warns -= 1
        self.bot.db.set(f"warns.{guild_id}.{user_id}", warns)

        embed = discord.Embed(
            title="✅ Warning Removed",
            description=f"Removed 1 warning from {member.mention}",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Warns", value=f"{warns}/3")
        embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    # ❗ ERROR HANDLER
    @warn.error
    @unwarn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Manage Messages permission.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Warn(bot))
