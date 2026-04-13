import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("Role hierarchy prevents this action.")

        await member.ban(reason=reason)

        embed = discord.Embed(
            title="User Banned",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=str(member), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ban(bot))
