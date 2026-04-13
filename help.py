import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):

        embed = discord.Embed(
            title="✨ NovaX Help Panel",
            description="**Welcome to NovaX Bot!**\nUse the commands below:",
            color=discord.Color.purple()
        )

        # Bot PFP
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Top banner (optional - remove if not needed)
        embed.set_image(url="https://i.imgur.com/8Km9tLL.png")

        # Moderation commands
        embed.add_field(
            name="🔨 Moderation",
            value=(
                "`!ban <user> [reason]`\n"
                "`!kick <user> [reason]`\n"
                "`!mute <user> [reason]`\n"
                "`!warn <user> [reason]`"
            ),
            inline=False
        )

        # Extra info
        embed.add_field(
            name="⚙️ Utility",
            value="`!help` → Show this panel",
            inline=False
        )

        # Footer
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        # Timestamp (pro look)
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
