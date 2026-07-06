import discord
import os
import json
from discord.ext import commands

# --- 🎭 CUSTOM EMOJIS ---
E_NOM = "<a:bs_nom:1443239762197745790>"
E_BUTTERFLY = "<a:lyf_butterfly_black:1515672700415246346>"
E_DOT = "<a:spider_red_dot:1494179666133516411>"
E_SUPREME = "<:trick_supreme:1433737084363083869>"
E_GUAVA = "<a:Guava:1514950622586077354>"
E_HEART = "<a:HEART:1438571571915522208>"
E_HEART3 = "<a:Heart3:1434556967556350004>"
E_MOD = "<:Moderator:1433718499791994892>"
E_SWORD = "<:bd_sword:1495476833720729836>"
E_VERIFIED = "<a:verified:1434044320830459935>"
E_ROSE = "<:bd_rose:1510988383332204735>"

# --- 🖼️ DEFAULT BANNER URL ---
DEFAULT_BANNER_URL = "https://i.imgur.com/k9b8fU6.gif"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix

        options = [
            discord.SelectOption(label="Moderation", description="Security and guild protection utilities.", emoji=E_SWORD),
            discord.SelectOption(label="Utility", description="General framework service parameters.", emoji=E_SUPREME),
            discord.SelectOption(label="Management", description="Core guild configuration protocols.", emoji=E_MOD),
            discord.SelectOption(label="Main Index", description="Return to home dashboard.", emoji="🏠"),
        ]

        super().__init__(
            placeholder="Select a module category to review parameters...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.from_rgb(47, 49, 54))
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
            embed.title = f"{E_SWORD} System Security Operations Center"
            embed.description = (
                f"{E_DOT} *Enforcing network protection parameters and guild policies.* {E_NOM}\n"
                f"```ansi\n"
                f"\u001b[0;31m{p}ban\u001b[0m    : Restrict user access permanently\n"
                f"\u001b[0;31m{p}unban\u001b[0m  : Revoke standard guild ban via User ID\n"
                f"\u001b[0;31m{p}kick\u001b[0m   : Remove user from active guild node\n"
                f"\u001b[0;31m{p}mute\u001b[0m   : Apply global communication timeout\n"
                f"\u001b[0;31m{p}unmute\u001b[0m : Clear communication timeout status\n"
                f"\u001b[0;31m{p}clear\u001b[0m  : Purge targeted messages from text channel\n"
                f"```"
            )

        elif self.values[0] == "Utility":
            embed.title = f"{E_SUPREME} Framework General Utility Interface"
            embed.description = (
                f"{E_BUTTERFLY} *Standard diagnostic protocols and general features.* {E_GUAVA}\n"
                f"```ansi\n"
                f"\u001b[0;34m{p}afk\u001b[0m    : Toggle status to away from keyboard\n"
                f"\u001b[0;34m{p}say\u001b[0m    : Execute system text message broadcast\n"
                f"\u001b[0;34m{p}dm\u001b[0m     : Transmit private direct message to target\n"
                f"\u001b[0;34m{p}ping\u001b[0m   : Analyze gateway response latency parameters\n"
                f"\u001b[0;34m{p}help\u001b[0m   : Display framework navigation directory\n"
                f"```"
            )

        elif self.values[0] == "Management":
            embed.title = f"{E_MOD} Structural Management Dashboard"
            embed.description = (
                f"{E_VERIFIED} *Configure guild rules, administrative tags, and logs.* {E_HEART}\n"
                f"```ansi\n"
                f"\u001b[0;35m{p}setprefix\u001b[0m : Reconfigure structural command prefix\n"
                f"\u001b[0;35m{p}role add\u001b[0m   : Assign targeted structural role configuration\n"
                f"\u001b[0;35m{p}role rem\u001b[0m   : Strip targeted structural role configuration\n"
                f"\u001b[0;35m{p}case\u001b[0m       : Audit specified action incident records\n"
                f"```"
            )

        else:
            await interaction.response.edit_message(embed=self.view.main_embed, view=self.view)
            return

        embed.set_footer(
            text=f"Queried by: {interaction.user} {E_HEART3}",
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

    @commands.hybrid_command(name="help", description="Access the configuration matrix directory.")
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
            title=f"{E_VERIFIED} Starla Operational Command Matrix",
            description=f"Welcome to the automated control hub. {E_BUTTERFLY} Utilize the selection drop-down parameters mapped below to view detailed operation arguments. {E_ROSE}",
            color=discord.Color.from_rgb(47, 49, 54)
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

        embed.add_field(name=f"{E_SWORD} Security Operations", value="`ban`, `kick`, `mute`, `clear`", inline=True)
        embed.add_field(name=f"{E_SUPREME} General Utilities", value="`afk`, `say`, `dm`, `ping`", inline=True)
        embed.add_field(name=f"{E_MOD} Structural Admin", value="`role`, `setprefix`, `case`", inline=True)

        embed.add_field(
            name=f"{E_NOM} Operational Execution Guide",
            value=f"Trigger explicit system calls via `{p}help` or initialize drop-down tracking down below. {E_GUAVA}",
            inline=False
        )

        embed.set_footer(text=f"Starla Secure Framework Core Operations • Status: Operational {E_HEART}")

        view = HelpView(self.bot, p, embed)

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
        
