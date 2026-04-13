import discord
from discord.ext import commands
import asyncio
import json
import os

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "cases.json"
        
        # Database check: Agar file nahi hai toh bana do
        if not os.path.exists(self.db_file):
            with open(self.db_file, "w") as f:
                json.dump({"case_count": 0}, f)

    def get_next_case(self):
        # Case number ko +1 badhane ke liye function
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        new_case = data["case_count"] + 1
        
        with open(self.db_file, "w") as f:
            json.dump({"case_count": new_case}, f)
        
        return new_case

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: str = None, *, reason="No reason provided"):
        # Agla Case ID nikalna (#1, #2...)
        case_id = self.get_next_case()
        
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, speak=False, send_messages=False)

        await member.add_roles(muted_role)
        time_display = duration if duration else "Indefinite"
        
        # CLEAN SERVER RESPONSE (Photo jaisa)
        await ctx.send(f"✅ **Muted {member.name}** for **{time_display}** (Case #{case_id}) (user notified with a direct message)")

        # DM NOTIFICATION
        try:
            dm_embed = discord.Embed(
                description=f"🔇 You have been muted in **{ctx.guild.name}**\n**Duration:** {time_display}\n**Reason:** {reason}\n**Case:** #{case_id}",
                color=discord.Color.red()
            )
            await member.send(embed=dm_embed)
        except:
            pass

        # TEMP MUTE LOGIC
        if duration:
            unit = duration[-1].lower()
            try:
                time_val = int(duration[:-1])
                seconds = 0
                if unit == "s": seconds = time_val
                elif unit == "m": seconds = time_val * 60
                elif unit == "h": seconds = time_val * 3600
                elif unit == "d": seconds = time_val * 86400

                if seconds > 0:
                    await asyncio.sleep(seconds)
                    if muted_role in member.roles:
                        await member.remove_roles(muted_role)
                        await ctx.send(f"🔊 **{member.name}** unmuted (Case #{case_id} expired).")
            except:
                pass

async def setup(bot):
    await bot.add_cog(Mute(bot))
    
        
