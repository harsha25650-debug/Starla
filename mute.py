
import discord
from discord.ext import commands

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        
        if member == ctx.author:
            return await ctx.send("You cannot mute yourself.")

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        # Create role if not exists
        if not muted_role:
            muted_role = await ctx.guild.create_role(
                name="Muted",
                reason="Mute system setup"
            )

            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role,
                    send_messages=False,
                    speak=False,
                    add_reactions=False
                )

        if muted_role in member.roles:
            return await ctx.send("This user is already muted.")

        await member.add_roles(muted_role, reason=reason)

        embed = discord.Embed(
            title="User Muted",
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Mute(bot))
