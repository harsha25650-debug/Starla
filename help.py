import discord
from discord.ext import commands
from datetime import datetime

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        # Clean Blurple Color
        embed = discord.Embed(
            title="✨ NovaX Bot | Help Panel",
            description="Welcome to **NovaX**. Here are the commands you can use to manage and interact with the server.",
            color=0x7289da,
            timestamp=datetime.utcnow()
        )

        # 🔨 Moderation Category
        embed.add_field(
            name="🔨 Moderation",
            value=(
                "> `!ban <user> [reason]` - Ban a member\n"
                "> `!kick <user> [reason]` - Kick a member\n"
                "> `!mute <user> [time] [reason]` - Mute a member\n"
                "> `!unmute <user>` - Unmute a member\n"
                "> `!clear <amount>` - Delete bulk messages"
            ),
            inline=False
        )

        # 💤 AFK System
        embed.add_field(
            name="💤 AFK System",
            value=(
                "> `!afk [reason]` - Set your AFK status\n"
                "> *Note: AFK is removed when you chat.*"
            ),
            inline=False
        )

        # ⚙️ Utility & Info
        embed.add_field(
            name="⚙️ Utility",
            value=(
                "> `!help` - Show this panel\n"
                "> `!ping` - Check bot latency"
            ),
            inline=False
        )

        # CHANGE: Mountain hata kar Bot ka icon set kiya hai
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Footer with user info
        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
    
        
