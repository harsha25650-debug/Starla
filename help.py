import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# --- 🎭 CUSTOM EMOJIS ---
E_NOM = "<:bs_nom:1494179666133516411>"
E_BUTTERFLY = "<:lyf_butterfly_black:1494179666133516411>"
E_DOT = "<a:spider_red_dot:1494179666133516411>"
E_SUPREME = "<:trick_supreme:1494179666133516411>"
E_GUAVA = "<:Guava:1494179666133516411>"
E_HEART = "<:HEART:1494179666133516411>"
E_HEART3 = "<:Heart3:1494179666133516411>"
E_MOD = "<:Moderator:1494179666133516411>"
E_SWORD = "<:bd_sword:1494179666133516411>"
E_VERIFIED = "<:verified:1494179666133516411>"
E_ROSE = "<:bd_rose:1494179666133516411>"

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot, guild_prefix):
        self.bot = bot
        self.prefix = guild_prefix

        options = [
            discord.SelectOption(label="Moderation", description="Safety & protection commands", emoji="⚔️"),
            discord.SelectOption(label="Utility", description="General usage & info", emoji="⚙️"),
            discord.SelectOption(label="Management", description="Server settings & role control", emoji="🛡️"),
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
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)

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
                f"
```\n"
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
                f"
```\n"
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
        if self.bot.user.banner:
            embed.set_image(url=self.bot.user.banner.url)

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
    
