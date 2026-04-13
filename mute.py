import discord
from discord.ext import commands
import asyncio

class TempMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def tempmute(self, ctx, member: discord.Member, time: int, *, reason="No reason provided"):

        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)

        await member.add_roles(muted_role, reason=reason)

        await ctx.send(f"{member.mention} muted for {time}s | Reason: {reason}")

        await asyncio.sleep(time)

        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} unmuted automatically")
            
async def setup(bot):
    await bot.add_cog(TempMute(bot))
