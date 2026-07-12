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
            discord.SelectOption(label="Moderation", description="Security and member punishment utilities.", emoji=self.ico_mod),
            discord.SelectOption(label="Utility & Management", description="Core guild config & developer tools.", emoji=self.ico_info),
            discord.SelectOption(label="Fun & Saturation", description="Massping and chat extraction functions.", emoji=self.ico_chat),
            discord.SelectOption(label="Main Index", description="Return to home dashboard.", emoji="🏠"),
        ]

        super().__init__(
            placeholder="Select a module category to review parameters...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        # View se components dynamic extract karenge
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

        if self.values[0] == "Moderation":
            embed.title = f"<:starla_ico_mod:1525757006823161897> Security Operations Center"
            embed.description = (
                f"{dot_red} **Enforcing server protection policies and protocols.**\n\n"
                f"```ansi\n"
                f"\u001b[0;31m{p}ban\u001b[0m       : {p}ban <@user> [reason]\n"
                f"\u001b[0;31m{p}unban\u001b[0m     : {p}unban <user_id> [reason]\n"
                f"\u001b[0;31m{p}kick\u001b[0m      : {p}kick <@user> [reason]\n"
                f"\u001b[0;31m{p}mute\u001b[0m      : {p}mute <@user> [duration] [reason]\n"
                f"\u001b[0;31m{p}clear\u001b[0m     : {p}clear <amount> [@user]\n"
                f"\u001b[0;31m{p}snipe\u001b[0m     : View recently deleted chat blocks\n"
                f"```\n"
                f"{arrow} *Mute durations can be parsed in intervals like `10m`, `2h`, `1d`.*"
            )

        elif self.values[0] == "Utility & Management":
            embed.title = f"{ico_info} Management & Diagnostics Core"
            embed.description = (
                f"{dot_blue} **Structural configuration modules for staff members.**\n\n"
                f"```ansi\n"
                f"\u001b[0;34m{p}role\u001b[0m      : {p}role <@user> <@role> (Toggles Role)\n"
                f"\u001b[0;34m{p}roleicon\u001b[0m  : {p}roleicon <@role> [emoji/link/reply]\n"
                f"\u001b[0;34m{p}nick\u001b[0m      : {p}nick <@user> [New Name] (Leave empty to reset)\n"
                f"\u001b[0;34m{p}case\u001b[0m      : {p}case <case_id> (Audits DB logs)\n"
                f"\u001b[0;34m{p}restart\u001b[0m   : Safely reloads bot process (Owner Only)\n"
                f"```"
            )

        elif self.values[0] == "Fun & Saturation":
            embed.title = f"<:starla_ico_chat:1525757016461545615> Network Saturation & Fun Pack"
            embed.description = (
                f"{dot_pink} **High-velocity cluster utilities and media actions.**\n\n"
                f"```ansi\n"
                f"\u001b[0;35m{p}steal\u001b[0m       : {p}steal :emoji: [Or reply to messages]\n"
                f"\u001b[0;35m{p}spam\u001b[0m        : {p}spam <message> <amount>\n"
                f"\u001b[0;35m{p}spstop\u001b[0m      : Terminates channel active spam loops\n"
                f"\u001b[0;35m{p}massping\u001b[0m    : Mentions target in sequence (Max 200)\n"
                f"\u001b[0;35m{p}ghostping\u001b[0m   : Quietly pings user and purges logs\n"
                f"\u001b[0;35m{p}superpings\u001b[0m  : Scheduled loop mentions (e.g. 10m 50)\n"
                f"```\n"
                f"{arrow} *Access rights for spam/ping tools managed by `{p}spaccess` & `{p}mpaccess`.*"
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
        
        # Share Starla parameters down to selection components
        self.dot_red = "<:starlaDotRed:1525756464692596886>"
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.dot_pink = "<:topggDotPink:1525756444782104597>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        
        self.add_item(HelpDropdown(bot, guild_prefix))


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ MAIN STORAGE STRINGS
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.yes = "<:starla_opt_yes:1525757001664299102>"

    @commands.hybrid_command(name="help", description="Access the NovaX system command directory grid matrix.")
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

        # Main Home Dashboard Setup
        embed = discord.Embed(
            title=f"{self.yes} NovaX Control Terminal Dashboard",
            description=f"Welcome to the automated control hub. Use the selection drop-down matrix mapped below to review explicit operation parameters.",
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

        # Categorized Grid Fields matching actual module filenames
        embed.add_field(name="🛡️ Security Ops", value="`ban`, `unban`, `kick`, `mute`, `clear`, `snipe`", inline=True)
        embed.add_field(name=f"{self.ico_info} Management Core", value="`role`, `roleicon`, `nick`, `case`, `restart`", inline=True)
        embed.add_field(name="⚡ Saturation Systems", value="`steal`, `spam`, `massping`, `ghostping`, `superpings`", inline=False)

        embed.add_field(
            name="💡 Operational Guideline",
            value=f"{self.arrow} Open the drop-down box down below to display advanced argument formats for each distinct category.",
            inline=False
        )

        embed.set_footer(text="NovaX Automation Security Engine • Status: Operational", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        view = HelpView(self.bot, p, embed)

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
            
