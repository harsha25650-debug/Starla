import discord
from discord.ext import commands
from discord import app_commands
import json

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.guild_prefix = guild_prefix
        options = [
            discord.SelectOption(label="Moderation", description="Ban, Kick, Mute, Clear", emoji="🔨"),
            discord.SelectOption(label="Utility", description="AFK, Say, DM, Ping", emoji="⚙️"),
            discord.SelectOption(label="Management", description="Role, Prefix, Case", emoji="🛡️"),
            discord.SelectOption(label="All Commands", description="Show everything again", emoji="✨"),
        ]
        super().__init__(placeholder="Filter by category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x2b2d31)
        banner_url = "https://cdn.discordapp.com/attachments/1432767818075738242/1493536131403481118/1775935922918.png"
        embed.set_image(url=banner_url)
        
        p = self.guild_prefix

        if self.values[0] == "Moderation":
            embed.title = "🔨 Moderation Commands"
            embed.description = f"`{p}ban`, `{p}unban`, `{p}kick`, `{p}mute`, `{p}unmute`, `{p}clear`"
        
        elif self.values[0] == "Utility":
            embed.title = "⚙️ Utility Commands"
            embed.description = f"`{p}afk`, `{p}say`, `{p}dm`, `{p}ping`, `{p}help`"

        elif self.values[0] == "Management":
            embed.title = "🛡️ Management Commands"
            embed.description = f"`{p}setprefix`, `{p}role add`, `{p}role remove`, `{p}case`"
            
        elif self.values[0] == "All Commands":
            embed.title = "✨ NovaX | All Commands"
            embed.add_field(name="🔨 Moderation", value=f"`{p}ban`, `{p}kick`, `{p}mute`, `{p}clear`...", inline=False)
            embed.add_field(name="⚙️ Utility", value=f"`{p}afk`, `{p}say`, `{p}dm`, `{p}ping`", inline=False)
            embed.add_field(name="🛡️ Management", value=f"`{p}role`, `{p}setprefix`, `{p}case`", inline=False)

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot, guild_prefix):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot, guild_prefix))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="NovaX Help Panel")
    async def help(self, ctx):
        # Fetch Prefix
        guild_prefix = "!"
        try:
            with open("./data/prefixes.json", "r") as f:
                prefixes = json.load(f)
            guild_prefix = prefixes.get(str(ctx.guild.id), "!")
        except: pass

        p = guild_prefix
        banner_url = "https://cdn.discordapp.com/attachments/1432767818075738242/1493536131403481118/1775935922918.png"

        # Main Embed (Showing all features initially)
        embed = discord.Embed(
            title="✨ NovaX Bot | Help Panel",
            description=f"Welcome to **NovaX**. Here are all the commands you can use.",
            color=0x2b2d31
        )
        embed.set_image(url=banner_url)
        
        embed.add_field(
            name="🔨 Moderation", 
            value=f"`{p}ban`, `{p}kick`, `{p}mute`, `{p}unmute`, `{p}clear`", 
            inline=False
        )
        embed.add_field(
            name="💤 AFK System", 
            value=f"`{p}afk [reason]`", 
            inline=False
        )
        embed.add_field(
            name="⚙️ Utility", 
            value=f"`{p}say`, `{p}dm`, `{p}ping`, `{p}help`", 
            inline=False
        )
        embed.add_field(
            name="🛡️ Management", 
            value=f"`{p}setprefix`, `{p}role`, `{p}case`", 
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"NovaX Security • Use menu to filter", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed, view=HelpView(self.bot, p))

async def setup(bot):
    await bot.add_cog(Help(bot))
