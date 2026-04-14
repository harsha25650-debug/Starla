import discord
from discord.ext import commands
from discord import app_commands
import json

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Moderation", description="Ban, Kick, Mute, Clear, etc.", emoji="🔨"),
            discord.SelectOption(label="Utility", description="AFK, Say, DM, Ping, etc.", emoji="⚙️"),
            discord.SelectOption(label="Management", description="Role, Prefix, Case, etc.", emoji="🛡️"),
        ]
        super().__init__(placeholder="Select a category to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Fetch current prefix for display
        guild_prefix = "!"
        try:
            with open("./data/prefixes.json", "r") as f:
                prefixes = json.load(f)
            guild_prefix = prefixes.get(str(interaction.guild_id), "!")
        except: pass

        embed = discord.Embed(color=0x2b2d31)
        # Banner image repeated in every category for consistency
        embed.set_image(url="https://cdn.discordapp.com/attachments/1432767818075738242/1493536131403481118/1775935922918.png?ex=69df536a&is=69de01ea&hm=143e2e9e62a23474072913dc3ee3a94d30d4b845a910ea5e7add13a707400681&")
        
        if self.values[0] == "Moderation":
            embed.title = "🔨 Moderation Commands"
            embed.description = (
                f"`{guild_prefix}ban <user> [reason]` - Permanent server ban\n"
                f"`{guild_prefix}unban <id>` - Remove ban from user ID\n"
                f"`{guild_prefix}kick <user> [reason]` - Kick member from server\n"
                f"`{guild_prefix}mute <user> [time] [reason]` - Timeout member\n"
                f"`{guild_prefix}unmute <user>` - Remove member timeout\n"
                f"`{guild_prefix}clear <amount>` - Bulk delete messages"
            )
        
        elif self.values[0] == "Utility":
            embed.title = "⚙️ Utility Commands"
            embed.description = (
                f"`{guild_prefix}afk [reason]` - Set your AFK status\n"
                f"`{guild_prefix}say <channel> <message>` - Send message via bot\n"
                f"`{guild_prefix}dm <user> <message>` - Send DM to user via bot\n"
                f"`{guild_prefix}ping` - Check bot latency and heartbeat\n"
                f"`{guild_prefix}help` - Show this help panel"
            )

        elif self.values[0] == "Management":
            embed.title = "🛡️ Management Commands"
            embed.description = (
                f"`{guild_prefix}setprefix <prefix>` - Change bot prefix for server\n"
                f"`{guild_prefix}role add <user> <role>` - Add role to user\n"
                f"`{guild_prefix}role remove <user> <role>` - Remove role from user\n"
                f"`{guild_prefix}case <number>` - Retrieve moderation case details"
            )

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="NovaX Professional Help Panel")
    async def help(self, ctx):
        embed = discord.Embed(
            title="✨ NovaX | Information Panel",
            description="Welcome to **NovaX**. Use the select menu below to navigate through different command categories.",
            color=0x2b2d31
        )
        # Adding your requested banner image
        embed.set_image(url="https://cdn.discordapp.com/attachments/1432767818075738242/1493536131403481118/1775935922918.png?ex=69df536a&is=69de01ea&hm=143e2e9e62a23474072913dc3ee3a94d30d4b845a910ea5e7add13a707400681&")
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"NovaX Security • Developed for {ctx.guild.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed, view=HelpView(self.bot))

async def setup(bot):
    await bot.add_cog(Help(bot))
