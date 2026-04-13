import discord
from discord.ext import commands
from utils.warnings import add_warning, get_warnings

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):

        add_warning(member.id, reason)
        total = len(get_warnings(member.id))

        embed = discord.Embed(
            title="User Warned",
            color=discord.Color.yellow()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=str(total), inline=False)

        await ctx.send(embed=embed)

        # Auto punishment system
        if total >= 3:
            await member.ban(reason="3 warnings reached (auto punishment)")
            await ctx.send(f"{member.mention} auto banned (3 warnings reached)")

async def setup(bot):
    await bot.add_cog(Warn(bot))
