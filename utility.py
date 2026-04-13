import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # !say command - Bot wahi bolega jo aap likhoge
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, message):
        await ctx.message.delete() # Aapka command delete kar dega
        await ctx.send(message)    # Normal text bhejega

    # !dm command - Kisi ko bhi normal message bhejega
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def dm(self, ctx, member: discord.Member, *, message):
        try:
            await member.send(message) # Sirf normal message jayega
            await ctx.send(f"✅ Message sent to {member.name}", delete_after=3)
        except discord.Forbidden:
            await ctx.send(f"❌ Could not DM {member.name}. DMs are closed.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
