import discord
from discord.ext import commands

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):

        if member == ctx.author:
            return await ctx.send("You cannot ban yourself.")

        if member.top_role >= ctx.author.top_role:
            return await ctx.send("You cannot ban this user due to role hierarchy.")

        try:
            await member.ban(reason=f"{reason} | By {ctx.author}")

            embed = discord.Embed(
                title="User Banned",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=str(member), inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this user.")

async def setup(bot):
    await bot.add_cog(Ban(bot))
