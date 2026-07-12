import discord
from discord.ext import commands
import datetime

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_green = "<:starlaDotGreen:1525756444782104597>"
        self.dot_red = "<:starlaDotRed:1525756464692596886>"
        self.dot_blue = "<:starlaDotBlue:1525756437224099862>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 FIXED PERMISSION CHECK (OWNER BYPASS)
    def has_nick_perms():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            return ctx.author.guild_permissions.manage_nicknames
        return commands.check(predicate)

    @commands.command(name="nick", aliases=["nickname", "changenick"], description="Change or reset a member's nickname")
    @has_nick_perms()
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, new_nick: str = None):
        
        # 🚨 EXECUTOR HIERARCHY CHECK (Staff Security)
        if ctx.author.id != ctx.guild.owner_id and member.top_role >= ctx.author.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** You cannot manage someone with a higher or equal role.")

        # 🚨 BOT HIERARCHY CHECK
        if ctx.guild.me.top_role <= member.top_role:
            return await ctx.send(f"{self.cross} **Hierarchy Error:** This member's role is higher than or equal to my highest integration role.")

        # 🚨 SERVER OWNER PROTECTION CHECK
        if member == ctx.guild.owner:
            return await ctx.send(f"{self.cross} **Permission Error:** I do not have permission to modify the Server Owner's profile.")

        try:
            embed = discord.Embed(color=0x2b2d31)
            embed.set_footer(text=f"Action by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
            embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

            # 🔄 RESET NICKNAME (If new_nick is None)
            if new_nick is None:
                await member.edit(nick=None, reason=f"NovaX Nickname System | Reset by {ctx.author}")
                embed.description = f"{self.dot_blue} **Nickname Reset Successfully**\n\n{self.arrow} **User:** {member.mention}\n{self.arrow} **Status:** Reverted to default username."
            
            # 📝 UPDATE NICKNAME
            else:
                new_nick = new_nick.strip()
                if len(new_nick) > 32:
                    return await ctx.send(f"{self.cross} **Validation Error:** Nicknames cannot exceed 32 characters in length.")
                
                await member.edit(nick=new_nick, reason=f"NovaX Nickname System | Changed by {ctx.author}")
                embed.description = f"{self.dot_green} **Nickname Updated Successfully**\n\n{self.arrow} **User:** {member.mention}\n{self.arrow} **New Nickname:** `{new_nick}`"
            
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(f"{self.cross} **Forbidden:** Missing role or hierarchy power to update this user's nickname.")
        except Exception as e:
            await ctx.send(f"{self.cross} **Execution Error:** `{e}`")

    # ❗ CLEAN ACTION ERROR HANDLER
    @nick.error
    async def nick_error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You need `Manage Nicknames` authorization to use this command.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
            
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} **System Failure:** I am missing `Manage Nicknames` client clearance permissions.")
            
        elif isinstance(error, commands.MissingRequiredArgument):
            p = ctx.prefix
            embed = discord.Embed(
                title=f"{self.ico_info} Nickname Usage Guide",
                description=f"{self.arrow} **Change Nickname:** `{p}nick @user New Name`\n"
                            f"{self.arrow} **Reset Nickname:** `{p}nick @user`",
                color=0x2b2d31
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Nickname(bot))
        
