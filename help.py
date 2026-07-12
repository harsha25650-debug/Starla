import discord
import os
import json
from discord.ext import commands
import datetime

# --- 🖼️ DEFAULT BANNER URL ---
DEFAULT_BANNER_URL = "https://i.imgur.com/k9b8fU6.gif"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix

        # ✨ STARLA THEMED ICONS MAPPING FOR OPTIONS
        self.ico_mod = "<:starla_ico_mod:1525757006823161897>"
        self.ico_chat = "<:starla_ico_chat:1525757016461545615>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"

        options = [
            discord.SelectOption(label="Moderation", description="Security and member moderation commands.", emoji=self.ico_mod),
            discord.SelectOption(label="Management & Utility", description="Server configuration and role tools.", emoji=self.ico_info),
            discord.SelectOption(label="Automation & Tools", description="Massping, steal, and spam utilities.", emoji=self.ico_chat),
            discord.SelectOption(label="Main Index", description="Return to home dashboard.", emoji="🏠"),
        ]

        super().__init__(
            placeholder="Choose a category to view commands and examples...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        dot_red = self.view.dot_red
        dot_blue = self.view.dot_blue
        dot_pink = self.view.dot_pink
        arrow = self.view.arrow
        ico_info = self.view.ico_info
        
        embed = discord.Embed(color=0x2b2d31)
        p = self.prefix

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        banner_url = DEFAULT_BANNER_URL
        try:
            bot_user = await self.bot.fetch_user(self.bot.user.id)
            if bot_user.banner:
                banner_url = bot_user.banner.url
        except Exception:
            pass
        embed.set_image(url=banner_url)

        # 1. MODERATION CATEGORY
        if self.values[0] == "Moderation":
            embed.title = f"<:starla_ico_mod:1525757006823161897> Security Operations Center"
            embed.description = (
                f"{dot_red} **Enforcing server protection and member punishment.**\n\n"
                f"```ansi\n"
                f"\u001b[0;31m{p}ban\u001b[0m       : {p}ban @User Spamming in chat\n"
                f"\u001b[0;31m{p}unban\u001b[0m     : {p}unban 1140926535935725711 Appeal accepted\n"
                f"\u001b[0;31m{p}kick\u001b[0m      : {p}kick @User Warning limit reached\n"
                f"\u001b[0;31m{p}mute\u001b[0m      : {p}mute @User 10m Bad language\n"
                f"\u001b[0;31m{p}unmute\u001b[0m    : {p}unmute @User Mute time cleared\n"
                f"\u001b[0;31m{p}clear\u001b[0m     : {p}clear 50  OR  {p}clear 20 @User\n"
                f"\u001b[0;31m{p}snipe\u001b[0m     : {p}snipe (Shows deleted messages)\n"
                f"```\n"
                f"{arrow} *Mute time formats: `10m`, `2h`, `1d`.*"
            )

        # 2. MANAGEMENT & UTILITY CATEGORY
        elif self.values[0] == "Management & Utility":
            embed.title = f"{ico_info} Server Management & Roles"
            embed.description = (
                f"{dot_blue} **Server configuration and role assignment tools.**\n\n"
                f"```ansi\n"
                f"\u001b[0;34m{p}role\u001b[0m      : {p}role @User @VIP (Toggles Role)\n"
                f"\u001b[0;34m{p}roleicon\u001b[0m  : {p}roleicon @VIP :star:  (Or reply to an image)\n"
                f"\u001b[0;34m{p}nick\u001b[0m      : {p}nick @User Starla Member  (Empty to reset)\n"
                f"\u001b[0;34m{p}case\u001b[0m      : {p}case #1  (Check mod log history)\n"
                f"```"
            )

        # 3. AUTOMATION & TOOLS CATEGORY (Non-Owner Only)
        elif self.values[0] == "Fun & Saturation":
            embed.title = f"<:starla_ico_chat:1525757016461545615> Automation & Saturation Tools"
            embed.description = (
                f"{dot_pink} **High-speed messaging and emoji stealing utilities.**\n\n"
                f"```ansi\n"
                f"\u001b[0;35m{p}steal\u001b[0m       : {p}steal :emoji1: :emoji2:  (Or reply to msg)\n"
                f"\u001b[0;35m{p}spam\u001b[0m        : {p}spam Hello World 10\n"
                f"\u001b[0;35m{p}spstop\u001b[0m      : {p}spstop (Stops running spam loop)\n"
                f"\u001b[0;35m{p}massping\u001b[0m    : {p}massping @User 50\n"
                f"\u001b[0;35m{p}ghostping\u001b[0m   : {p}ghostping @User 20\n"
                f"\u001b[0;35m{p}superpings\u001b[0m  : {p}superpings @User 10s 30\n"
                f"\u001b[0;35m{p}stopsuperpings\u001b[0m: {p}stopsuperpings @User\n"
                f"```"
            )

        else:
            await interaction.response.edit_message(embed=self.view.main_embed, view=self.view)
            return

        embed.set_footer(
            text=f"Queried by: {interaction.user.name}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, bot, guild_prefix, main_embed):
        super().__init__(timeout=180)
        self.bot = bot
        self.main_embed = main_embed
        
        self.dot_red = "<:starlaDotRed:1525756464692596886>"
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.dot_pink = "<:topggDotPink:1525756454345375764>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        
        self.add_item(HelpDropdown(bot, guild_prefix))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.yes = "<:starla_opt_yes:1525757001664299102>"

    @commands.hybrid_command(name="help", description="Access Starla's command directory and operational guidelines.")
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

        # MAIN DASHBOARD EMBED
        embed = discord.Embed(
            title=f"{self.yes} Starla Security & Control Terminal",
            description=(
                f"Welcome to **Starla** control hub! Use the drop-down menu below to check available commands, syntax, and live examples.\n\n"
                f"💎 **Starla Premium Privilege:**\n"
                f"{self.arrow} *Premium users get access to **No Prefix** execution! You can run commands directly without typing `{p}` (e.g., `ban @user` instead of `{p}ban @user`).*"
            ),
            color=0x2b2d31
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        banner_url = DEFAULT_BANNER_URL
        try:
            bot_user = await self.bot.fetch_user(self.bot.user.id)
            if bot_user.banner:
                banner_url = bot_user.banner.url
        except Exception:
            pass
        embed.set_image(url=banner_url)

        # CATEGORY GRID FIELDS WITH REAL USAGE
        embed.add_field(
            name="🛡️ Moderation", 
            value=f"`{p}ban`, `{p}unban`, `{p}kick`\n`{p}mute`, `{p}clear`, `{p}snipe`", 
            inline=True
        )
        embed.add_field(
            name=f"{self.ico_info} Management", 
            value=f"`{p}role`, `{p}roleicon`\n`{p}nick`, `{p}case`", 
            inline=True
        )
        embed.add_field(
            name="⚡ Automation & Tools", 
            value=f"`{p}steal`, `{p}spam`, `{p}spstop`\n`{p}massping`, `{p}ghostping`, `{p}superpings`", 
            inline=False
        )

        embed.set_footer(text="Starla Framework Core Operations • Premium No-Prefix System Active", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        view = HelpView(self.bot, p, embed)

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
        
