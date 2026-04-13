import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member == ctx.author:
            return await ctx.send("You cannot kick yourself.")

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot kick this user due to role hierarchy.")

        try:
            await member.kick(reason=f"{reason} | By {ctx.author}")

            embed = discord.Embed(
                title="User Kicked",
                color=discord.Color.gold()
            )
            embed.add_field(name="User", value=str(member), inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user.")

async def setup(bot):
    await bot.add_cog(Kick(bot))
