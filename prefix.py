import discord
from discord.ext import commands
from discord import app_commands

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 💾 SAVE PREFIX
    def set_prefix(self, guild_id, prefix):
        self.bot.db.set(f"prefix.{guild_id}", prefix)

    # 📥 GET PREFIX (optional use)
    def get_prefix(self, guild_id):
        return self.bot.db.get(f"prefix.{guild_id}", "!")

    # ⚙️ SET PREFIX COMMAND
    @commands.hybrid_command(name="setprefix", description="Change bot prefix")
    @app_commands.describe(new_prefix="New prefix")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, new_prefix: str):

        if len(new_prefix) > 5:
            return await ctx.send("❌ Prefix cannot be longer than 5 characters.")

        self.set_prefix(ctx.guild.id, new_prefix)

        embed = discord.Embed(
            title="⚙️ Prefix Updated",
            description=f"New prefix is `{new_prefix}`",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Changed by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Prefix(bot))
