import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 📢 HYBRID: SAY COMMAND
    @commands.hybrid_command(name="say", description="Execute a system text message broadcast via the application engine.")
    @app_commands.describe(message="The explicit text array to broadcast.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def say(self, ctx: commands.Context, *, message: str):
        # Safely attempt to purge the initialization string if executed via prefix sequence inside a guild
        if ctx.interaction is None and ctx.message:
            try:
                await ctx.message.delete()
            except Exception:
                pass

        await ctx.send(message)

    # 📩 HYBRID: DM COMMAND
    @commands.hybrid_command(name="dm", description="Transmit an isolated direct message protocol to a specified user endpoint.")
    @app_commands.describe(user="The target recipient user snowflake parameter.", message="The isolated message payload string.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def dm(self, ctx: commands.Context, user: discord.User, *, message: str):
        # Dynamic extraction of fallback emojis from the core bot registry
        v = getattr(self.bot, 'emojis_dict', {}).get("verified", "✅")
        f_red = getattr(self.bot, 'emojis_dict', {}).get("fire_red_pastel", "❌")
        dot = getattr(self.bot, 'emojis_dict', {}).get("spider_red_dot", "⚠️")

        await ctx.defer(ephemeral=True)

        try:
            await user.send(message)
            await ctx.send(f"{v} **Transmission Complete:** Message successfully routed to `{user.name}`.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send(f"{f_red} **Delivery Protocol Failure:** Target system endpoints for `{user.name}` are restricted or private DMs are disabled.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"{dot} **Internal Operation Fault:** Asynchronous routing exception detected: `{str(e)}`", ephemeral=True)

    # ❗ STRUCTURAL UTILITY ERROR MANAGER
    @say.error
    @dm.error
    async def utility_error(self, ctx: commands.Context, error: Exception):
        dot = getattr(self.bot, 'emojis_dict', {}).get("spider_red_dot", "⚠️")
        
        if isinstance(error, commands.MissingRequiredArgument):
            f_purple = getattr(self.bot, 'emojis_dict', {}).get("fire_purple", "⚠️")
            await ctx.send(f"{f_purple} **Argument Configuration Error:** The requested module execution requires additional parameters.", ephemeral=True)
        else:
            await ctx.send(f"{dot} **Execution Exception Triggered:** `{str(error)}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utility(bot))
    
