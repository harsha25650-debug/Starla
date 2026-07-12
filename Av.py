import discord
from discord.ext import commands
from discord import app_commands
import datetime

class AvatarView(discord.ui.View):
    def __init__(self, user: discord.User, asset_type: str = "avatar"):
        super().__init__(timeout=120)
        self.user = user
        self.asset_type = asset_type

        # Generate Direct Asset Download Links
        asset = user.banner if asset_type == "banner" else user.display_avatar
        
        if asset:
            png_url = asset.replace(format="png", size=1024).url
            jpg_url = asset.replace(format="jpg", size=1024).url
            webp_url = asset.replace(format="webp", size=1024).url
            
            self.add_item(discord.ui.Button(label="PNG", url=png_url, style=discord.ButtonStyle.link))
            self.add_item(discord.ui.Button(label="JPG", url=jpg_url, style=discord.ButtonStyle.link))
            self.add_item(discord.ui.Button(label="WEBP", url=webp_url, style=discord.ButtonStyle.link))
            
            if asset.is_animated():
                gif_url = asset.replace(format="gif", size=1024).url
                self.add_item(discord.ui.Button(label="GIF", url=gif_url, style=discord.ButtonStyle.link))


class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.dot_pink = "<:topggDotPink:1525756454345375764>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🖼️ AVATAR COMMAND
    @commands.hybrid_command(name="av", aliases=["avatar", "pfp"], description="Display high-resolution profile avatar of a user")
    @app_commands.describe(user="The user whose avatar you want to view")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def avatar(self, ctx, user: discord.User = None):
        user = user or ctx.author

        # Fetch full user object to ensure display_avatar & custom assets are loaded
        try:
            user = await self.bot.fetch_user(user.id)
        except Exception:
            pass

        avatar_url = user.display_avatar.replace(size=1024).url

        embed = discord.Embed(
            title=f"{self.ico_info} {user.name}'s Avatar",
            color=0x2b2d31
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        view = AvatarView(user, asset_type="avatar")
        
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)

    # 🚩 BANNER COMMAND
    @commands.hybrid_command(name="banner", description="Display high-resolution profile banner of a user")
    @app_commands.describe(user="The user whose banner you want to view")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def banner(self, ctx, user: discord.User = None):
        user = user or ctx.author

        # Fetch full user profile to retrieve banner asset
        try:
            user = await self.bot.fetch_user(user.id)
        except Exception as e:
            return await ctx.send(f"{self.cross} **Error:** Failed to fetch user profile data. `{e}`")

        if not user.banner:
            embed = discord.Embed(
                description=f"{self.cross} **{user.mention} does not have a profile banner set.**",
                color=0x2b2d31
            )
            if ctx.interaction:
                return await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
            return await ctx.send(embed=embed)

        banner_url = user.banner.replace(size=1024).url

        embed = discord.Embed(
            title=f"{self.ico_info} {user.name}'s Banner",
            color=0x2b2d31
        )
        embed.set_image(url=banner_url)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

        view = AvatarView(user, asset_type="banner")

        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)

    # ❗ ERROR HANDLER
    @avatar.error
    @banner.error
    async def avatar_banner_errors(self, ctx, error):
        if isinstance(error, commands.UserNotFound) or isinstance(error, commands.BadArgument):
            await ctx.send(f"{self.cross} **User Not Found:** Please specify a valid user tag or ID.")
        else:
            await ctx.send(f"{self.cross} **Execution Error:** `{error}`")

async def setup(bot):
    await bot.add_cog(Avatar(bot))
      
