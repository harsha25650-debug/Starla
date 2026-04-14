import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Professional Banner URL
BANNER_URL = "https://cdn.discordapp.com/attachments/1432767818075738242/1493536131403481118/1775935922918.png?ex=69df536a&is=69de01ea&hm=143e2e9e62a23474072913dc3ee3a94d30d4b845a910ea5e7add13a707400681&"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix
        options = [
            discord.SelectOption(label="Moderation", description="Safety and protection commands", emoji="🔨"),
            discord.SelectOption(label="Utility", description="General usage and information", emoji="⚙️"),
            discord.SelectOption(label="Management", description="Server settings and role control", emoji="🛡️"),
            discord.SelectOption(label="Home", description="Return to the main overview", emoji="🏠"),
        ]
        super().__init__(placeholder="Select a category to filter...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x2b2d31)
        embed.set_image(url=BANNER_URL)
        p = self.prefix

        if self.values[0] == "Moderation":
            embed.title = "🔨 Moderation Module"
            embed.description = (
                f"```\n"
                f"{p}ban    : Ban a member permanently\n"
                f"{p}unban  : Remove a ban via User ID\n"
                f"{p}kick   : Kick a member from the server\n"
                f"{p}mute   : Timeout a member temporarily\n"
                f"{p}unmute : Remove timeout from a member\n"
                f"{p}clear  : Delete a large amount of messages\n"
                f"```"
            )
        elif self.values[0] == "Utility":
            embed.title = "⚙️ Utility Module"
            embed.description = (
                f"```\n"
                f"{p}afk    : Set an away status\n"
                f"{p}say    : Broadcast via the bot\n"
                f"{p}dm     : Message a user privately\n"
                f"{p}ping   : Check bot connectivity\n"
                f"{p}help   : View this help panel\n"
                f"```"
            )
        elif self.values[0] == "Management":
            embed.title = "🛡️ Management Module"
            embed.description = (
                f"```\n"
                f"{p}setprefix : Update server prefix\n"
                f"{p}role add   : Assign role to a member\n"
                f"{p}role rem   : Strip role from a member\n"
                f"{p}case       : Lookup moderation records\n"
                f"```"
            )
        else:
            # Home logic
            await interaction.response.edit_message(embed=self.view.main_embed, view=self.view)
            return

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed)

class HelpView(discord.ui.View):
    def __init__(self, bot, guild_prefix, main_embed):
        super().__init__(timeout=180)
        self.main_embed = main_embed
        self.add_item(HelpDropdown(bot, guild_prefix))

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Browse available bot commands")
    async def help(self, ctx):
        # Fetch server-specific prefix
        guild_prefix = "!"
        prefix_file = "./data/prefixes.json"
        if os.path.exists(prefix_file):
            try:
                with open(prefix_file, "r") as f:
                    prefixes = json.load(f)
                guild_prefix = prefixes.get(str(ctx.guild.id), "!")
            except:
                pass

        p = guild_prefix

        # Main Overview Embed
        embed = discord.Embed(
            title="✨ NovaX | Bot Command Center",
            description="Welcome to **NovaX**. Below is a summary of all commands. Use the menu for detailed category views.",
            color=0x2b2d31
        )
        embed.set_image(url=BANNER_URL)
        
        # Dashboard display
        embed.add_field(name="🔨 Moderation", value="`ban`, `kick`, `mute`, `clear`", inline=True)
        embed.add_field(name="⚙️ Utility", value="`afk`, `say`, `dm`, `ping`", inline=True)
        embed.add_field(name="🛡️ Management", value="`role`, `prefix`, `case`", inline=True)
        
        embed.add_field(
            name="ℹ️ Usage Guide", 
            value=f"
