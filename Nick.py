import discord
from discord.ext import commands

class Nickname(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="nick", aliases=["nickname", "changenick"])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, new_nick: str = None):
        """
        Change or reset a member's nickname.
        Usage: 
        !nick @user New Nickname (To change)
        !nick @user (To reset to original name)
        """
        # 1. Role Hierarchy Check: Ensure bot's highest role is above the target member
        if ctx.guild.me.top_role <= member.top_role:
            embed = discord.Embed(
                description=f"❌ Cannot change the nickname of {member.mention} because their role is higher than or equal to mine.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        # 2. Server Owner Protection Check
        if member == ctx.guild.owner:
            embed = discord.Embed(
                description="❌ I do not have permission to change the server owner's nickname.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        try:
            # If no nickname is specified, reset it to their original name
            if new_nick is None:
                await member.edit(nick=None)
                embed = discord.Embed(
                    description=f"✅ {member.mention}'s nickname has been reset to default.",
                    color=discord.Color.green()
                )
            else:
                # Discord enforces a strict maximum limit of 32 characters for nicknames
                if len(new_nick) > 32:
                    embed = discord.Embed(
                        description="❌ Nicknames cannot exceed 32 characters in length.",
                        color=discord.Color.red()
                    )
                    return await ctx.send(embed=embed)
                
                await member.edit(nick=new_nick)
                embed = discord.Embed(
                    description=f"✅ Changed nickname for {member.mention} to **{new_nick}**.",
                    color=discord.Color.green()
                )
            
            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(
                description="❌ Missing permissions to update this user's nickname.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                description=f"❌ An error occurred: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Clean local error handler for missing arguments or permissions
    @nick.error
    async def nick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                description="❌ You need the `Manage Nicknames` permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                description="❌ NovaX requires the `Manage Nicknames` permission to execute this.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        elif isinstance(error, commands.MissingRequiredArgument):
            prefix = ctx.prefix
            embed = discord.Embed(
                title="Command Usage Guide",
                description=f"Correct Format:\n`{prefix}nick @user <New Name>`\n\n*Leave `<New Name>` empty to clear the nickname.*",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

# Loader setup function for the main script
async def setup(bot):
    await bot.add_cog(Nickname(bot))

