import discord
from discord.ext import commands
import asyncio
import random

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason="No reason provided"):
        # Zeppelin-style Case ID
        case_id = random.randint(10000, 99999)
        
        # Muted role setup
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted", reason="Required for Mute Command")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False, add_reactions=False)

        # Mute check
        if muted_role in member.roles:
            return await ctx.send(f"❌ **{member.name}** is already muted.")

        await member.add_roles(muted_role, reason=reason)

        # Time logic (e.g., 10s, 5m, 1h)
        time_display = duration if duration else "Indefinite"
        
        # Zeppelin Style Response
        await ctx.send(f"✅ **Muted {member.name}** for **{time_display}** (Case #{case_id})")

        # User ko DM notify karna
        try:
            embed_dm = discord.Embed(
                description=f"🔇 You have been muted in **{ctx.guild.name}**\n**Duration:** {time_display}\n**Reason:** {reason}\n**Case:** #{case_id}",
                color=discord.Color.red()
            )
            await member.send(embed=embed_dm)
        except:
            pass

        # Temporary Mute Logic
        if duration:
            time_unit = duration[-1]
            time_val = int(duration[:-1])

            if time_unit == "s":
                seconds = time_val
            elif time_unit == "m":
                seconds = time_val * 60
            elif time_unit == "h":
                seconds = time_val * 3600
            elif time_unit == "d":
                seconds = time_val * 86400
            else:
                return # Invalid format

            await asyncio.sleep(seconds)

            # Check if still muted, then unmute
            if muted_role in member.roles:
                await member.remove_roles(muted_role)
                await ctx.send(f"🔊 **{member.name}** has been automatically unmuted (Case #{case_id} expired).")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"🔊 **Unmuted {member.name}**")
        else:
            await ctx.send(f"❌ **{member.name}** is not muted.")

async def setup(bot):
    await bot.add_cog(Mute(bot))
        
