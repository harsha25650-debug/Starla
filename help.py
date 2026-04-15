import discord
from discord.ext import commands
from discord import app_commands
import json
import os


class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix

        options = [
            discord.SelectOption(label="Moderation", description="Safety and protection commands", emoji="🔨"),
            discord.SelectOption(label="Utility", description="General usage and information", emoji="⚙️"),
            discord.SelectOption(label="Management", description="Server settings and role control", emoji="🛡️"),
            discord.SelectOption(label="Home", description="Return to main page", emoji="🏠"),
        ]

        super().__init__(
            placeholder="Select a category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x9b59b6)
        p = self.prefix

        # Bot icon
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Bot banner (AUTO)
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)

        if self.values[0] == "Moderation":
            embed.title = "🔨 Moderation Module"
            embed.description = (
                f"```\n"
                f"{p}ban    : Ban a member permanently\n"
                f"{p}unban  : Remove a ban via User ID\n"
                f"{p}kick   : Kick a member\n"
                f"{p}mute   : Timeout a member\n"
                f"{p}unmute : Remove timeout\n"
                f"{p}clear  : Delete messages\n"
                f"```"
            )

        elif self.values[0] == "Utility":
            embed.title = "⚙️ Utility Module"
            embed.description = (
                f"```\n"
                f"{p}afk    : Set AFK status\n"
                f"{p}say    : Bot message\n"
                f"{p}dm     : DM a user\n"
                f"{p}ping   : Check latency\n"
                f"{p}help   : Open help panel\n"
                f"```"
            )

        elif self.values[0] == "Management":
            embed.title = "🛡️ Management Module"
            embed.description = (
                f"```\n"
                f"{p}setprefix : Change prefix\n"
                f"{p}role add   : Give role\n"
                f"{p}role rem   : Remove role\n"
                f"{p}case       : Moderation logs\n"
                f"```"
            )

        else:
            await interaction.response.edit_message(embed=self.view.main_embed, view=self.view)
            return

        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, bot, guild_prefix, main_embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.main_embed = main_embed
        self.add_item(HelpDropdown(bot, guild_prefix))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Browse bot commands")
    async def help(self, ctx: commands.Context):
        guild_prefix = "!"
        prefix_file = "./data/prefixes.json"

        if ctx.guild and os.path.exists(prefix_file):
            try:
                with open(prefix_file, "r") as f:
                    prefixes = json.load(f)
                guild_prefix = prefixes.get(str(ctx.guild.id), "!")
            except:
                pass

        p = guild_prefix

        embed = discord.Embed(
            title="✨ NovaX | Command Center",
            description="Use the menu below to explore bot commands.",
            color=0x9b59b6
        )

        # Bot icon
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        # Bot banner (AUTO)
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)

        embed.add_field(name="🔨 Moderation", value="`ban`, `kick`, `mute`, `clear`", inline=True)
        embed.add_field(name="⚙️ Utility", value="`afk`, `say`, `dm`, `ping`", inline=True)
        embed.add_field(name="🛡️ Management", value="`role`, `setprefix`, `case`", inline=True)

        embed.add_field(
            name="ℹ️ Usage Guide",
            value=f"Use `{p}help` or `/help` and select a category from dropdown.",
            inline=False
        )

        embed.set_footer(text="NovaX Help System")

        view = HelpView(self.bot, p, embed)

        # Hybrid response (slash + prefix both)
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
