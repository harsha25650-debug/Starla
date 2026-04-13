import discord
from discord.ext import commands
import random

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        # Zeppelin style Case ID generation
        case_id = random.randint(10000, 99999)

        # Checking if user is trying to ban themselves or the bot
        if member == ctx.author:
            return await ctx.send("❌ You cannot ban yourself!")
        if member == self.bot.user:
            return await ctx.send("❌ You cannot ban me!")

        # Notifying the user via DM before banning
        try:
            embed_dm = discord.Embed(
                description=f"🚫 You have been banned from **{ctx.guild.name}**\n**Reason:** {reason}\n**Case:** #{case_id}",
                color=discord.Color.red()
            )
            await member.send(embed=embed_dm)
        except:
            # If DM is closed, it will ignore and continue
            pass

        try:
            await member.ban(reason=f"Case #{case_id} | Reason: {reason}")
            
            # Zeppelin Style Clean Response
            await ctx.send(f"✅ **Banned {member.name}** (Case #{case_id})")
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have enough permissions to ban this user. Check my role position!")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_id: int):
        # Unban manually using User ID
        try:
            user = await self.bot.fetch_user(member_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ **Unbanned {user.name}**")
        except discord.NotFound:
            await ctx.send("❌ User not found in ban list.")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
    
