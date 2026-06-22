import discord
from discord.ext import commands
from discord import app_commands
import json
import os

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
# Agar bot ka custom banner set nahi hai, toh ye cute animation banner display hoga!
# Aap is link ko kisi bhi image/gif link se badal sakte hain.
DEFAULT_BANNER_URL = "https://i.imgur.com/k9b8fU6.gif"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix

        options = [
            discord.SelectOption(label="Moderation", description="Safety & protection commands", emoji=E_SWORD),
            discord.SelectOption(label="Utility", description="General usage & info", emoji=E_SUPREME),
            discord.SelectOption(label="Management", description="Server settings & role control", emoji=E_MOD),
            discord.SelectOption(label="Home", description="Return to main page", emoji="🏠"),
        ]

        super().__init__(
            placeholder="Choose a category, cutie... 💞",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0xffb6c1)
        p = self.prefix

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # Banner Fetch Logic
        banner_url = DEFAULT_BANNER_URL
        try:
            bot_user = await self.bot.fetch_user(self.bot.user.id)
            if bot_user.banner:
                banner_url = bot_user.banner.url
        except Exception:
            pass
        embed.set_image(url=banner_url)

        if self.values[0] == "Moderation":
            embed.title = f"{E_SWORD} Starla Moderation System"
            embed.description = (
                f"{E_DOT} *Keep your server clean and safe!* {E_NOM}\n"
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
            embed.title = f"{E_SUPREME} Starla Utility Perks"
            embed.description = (
                f"{E_BUTTERFLY} *Handy commands for everyday fun!* {E_GUAVA}\n"
                f"```\n"
                f"{p}afk    : Set AFK status\n"
                f"{p}say    : Bot message\n"
                f"{p}dm     : DM a user\n"
                f"{p}ping   : Check latency\n"
                f"{p}help   : Open help panel\n"
                f"```"
            )

        elif self.values[0] == "Management":
            embed.title = f"{E_MOD} Starla Management Dashboard"
            embed.description = (
                f"{E_VERIFIED} *Configure and tune up your server rules!* {E_HEART}\n"
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
            text=f"Requested by {interaction.user} {E_HEART3}",
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

    @commands.hybrid_command(name="help", description="Browse Starla's cute commands!")
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
            title=f"{E_VERIFIED} Starla {E_HEART3} Command Center",
            description=f"Hey bestie! {E_BUTTERFLY} Use the dropdown menu below to check out all my features. I'm here to make your server amazing! {E_ROSE}",
            color=0xffb6c1
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        # Banner Fetch Logic
        banner_url = DEFAULT_BANNER_URL
        try:
            bot_user = await self.bot.fetch_user(self.bot.user.id)
            if bot_user.banner:
                banner_url = bot_user.banner.url
        except Exception:
            pass
        embed.set_image(url=banner_url)

        embed.add_field(name=f"{E_SWORD} Moderation", value="`ban`, `kick`, `mute`, `clear`", inline=True)
        embed.add_field(name=f"{E_SUPREME} Utility", value="`afk`, `say`, `dm`, `ping`", inline=True)
        embed.add_field(name=f"{E_MOD} Management", value="`role`, `setprefix`, `case`", inline=True)

        embed.add_field(
            name=f"{E_NOM} Quick Guide",
            value=f"Type `{p}help` or select an entry from the cute dropdown below! {E_GUAVA}",
            inline=False
        )

        embed.set_footer(text=f"Starla Cute System • Built with {E_HEART}")

        view = HelpView(self.bot, p, embed)

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))
