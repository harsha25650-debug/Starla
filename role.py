import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import datetime

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_green = "<:starlaDotGreen:1525756444782104597>"
        self.dot_red = "<:starlaDotRed:1525756464692596886>"
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.ico_mod = "<:starla_ico_mod:1525757006823161897>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 PERMISSION CHECK (OWNER BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            return ctx.author.guild_permissions.manage_roles
        return commands.check(predicate)

    # 🖼️ HELPER: Extract Image URL or Emoji
    async def get_image_or_emoji(self, ctx, argument: str = None):
        if ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                return "url", replied_msg.attachments[0].url
            elif replied_msg.content.startswith("http"):
                return "url", replied_msg.content.strip()

        if ctx.message.attachments:
            return "url", ctx.message.attachments[0].url

        if argument:
            argument = argument.strip()
            if argument.startswith("http"):
                return "url", argument
            else:
                return "emoji", argument

        return None, None

    # ⬇️ HELPER: Cloudflare Bypass Downloader
    async def download_image(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        if "image" in resp.headers.get("Content-Type", ""):
                            return await resp.read()
            except Exception:
                return None
        return None

    # 🔁 ROLE TOGGLE (HYBRID)
    @commands.hybrid_command(name="role", description="Toggle a role on or off for a specific server member")
    @app_commands.describe(member="Target user to modify", role="The role to toggle")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, role: discord.Role):

        # 🚨 ROLE POSITION CHECKS (Hierarchy Guards)
        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** The role {role.mention} is higher than my highest integration role.")

        if ctx.author.id != ctx.guild.owner_id and role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot manage a role that is equal to or higher than your top role.")

        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** Target user has authority higher or equal to your rank.")

        try:
            embed = discord.Embed(color=0x2b2d31)
            embed.set_footer(text=f"Action taken by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

            # 🔁 TOGGLE EXECUTION
            if role in member.roles:
                await member.remove_roles(role, reason=f"NovaX Role Toggle | Removed by {ctx.author}")
                embed.description = f"{self.dot_red} **Role Removed Successfully**\n\n{self.arrow} **User:** {member.mention}\n{self.arrow} **Role:** {role.mention}"
            else:
                await member.add_roles(role, reason=f"NovaX Role Toggle | Granted by {ctx.author}")
                embed.description = f"{self.dot_green} **Role Granted Successfully**\n\n{self.arrow} **User:** {member.mention}\n{self.arrow} **Role:** {role.mention}"

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} **Forbidden:** I don't have enough role power permissions to update this profile block.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Execution Error:** `{e}`")

    # 🎭 ROLE ICON (HYBRID)
    @commands.hybrid_command(name="roleicon", description="Modify display expression icon for a target role")
    @app_commands.describe(role="Target role to update", input_data="Emoji or direct image asset URL (Optional if replying)")
    @has_perm_or_owner()
    @commands.bot_has_permissions(manage_roles=True)
    async def roleicon(self, ctx, role: discord.Role, *, input_data: str = None):
        await ctx.typing()

        if role >= ctx.guild.me.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** This role is placed out of my permission reach boundary.")

        if ctx.author.id != ctx.guild.owner_id and role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot edit roles higher or equal to your own ranking.")

        data_type, source = await self.get_image_or_emoji(ctx, input_data)

        if not data_type:
            return await ctx.send(f"{self.cross} **Missing Parameter:** Attach a file, reply to an image asset, provide a URL, or drop a custom emoji.")

        try:
            # --- IF INPUT IS A URL LINK / ATTACHMENT ---
            if data_type == "url":
                image_bytes = await self.download_image(source)
                if image_bytes:
                    await role.edit(display_icon=image_bytes, reason=f"Icon modified by {ctx.author}")
                else:
                    return await ctx.send(f"{self.cross} **Download Error:** Could not stream image bytes. Check your link structure.")

            # --- IF INPUT IS A UNICODE OR SERVER CUSTOM EMOJI ---
            elif data_type == "emoji":
                if len(source) <= 4:  # Unicode Standard Emoji
                    await role.edit(display_icon=source.encode("utf-8"), reason=f"Icon modified by {ctx.author}")

                elif source.startswith("<:") or source.startswith("<a:"):  # Custom Guild Emoji
                    emoji_id = int(source.split(":")[2][:-1])
                    guild_emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

                    if guild_emoji is None:
                        return await ctx.send(f"{self.cross} **Scope Error:** Custom emoji must belong to *this* server to be saved as an icon slot.")

                    await role.edit(display_icon=await guild_emoji.read(), reason=f"Icon modified by {ctx.author}")
                else:
                    return await ctx.send(f"{self.cross} **Validation Error:** Invalid character set parsed for icon parameter.")

            # SUCCESS OUTPUT
            embed = discord.Embed(
                description=f"{self.dot_blue} **Display expression updated successfully for role {role.mention}.**",
                color=0x2b2d31
            )
            embed.set_footer(text=f"Updated by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} **Permission Error:** Check if this guild has reached the minimum Nitro Boost level requirement for icons.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Process Failure:** `{e}`")

    # ❗ CLEAN ACTION ERROR HANDLER
    @role.error
    @roleicon.error
    async def role_cog_errors(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** `Manage Roles` authorization clearance validation failed.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} **System Failure:** I am missing `Manage Roles` client clearance permissions.")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Role(bot))
            
