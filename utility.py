import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK (OWNER BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True

            return ctx.author.guild_permissions.manage_messages

        return commands.check(predicate)

    # 📢 SAY COMMAND (PREFIX + SLASH)
    @commands.hybrid_command(name="say", description="Make the bot say something")
    @app_commands.describe(message="Message to send")
    @has_perm_or_owner()
    async def say(self, ctx, *, message: str):

        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.send(message)

    # 📩 DM COMMAND (PREFIX + SLASH)
    @commands.hybrid_command(name="dm", description="Send a DM to a user")
    @app_commands.describe(member="User to DM", message="Message to send")
    @has_perm_or_owner()
    async def dm(self, ctx, member: discord.Member, *, message: str):

        try:
            await member.send(message)
            await ctx.send(f"✅ Message sent to {member.name}", delete_after=3)
        except discord.Forbidden:
            await ctx.send(f"❌ Could not DM {member.name}. DMs are closed.")

    # ❗ ERROR HANDLER
    @say.error
    @dm.error
    async def utility_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
