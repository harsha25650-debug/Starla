import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("Role hierarchy prevents this action.")

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="User Kicked",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=member, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Kick(bot))
