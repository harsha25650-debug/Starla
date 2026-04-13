import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # 1. Missing Arguments Error (Adhoori Command)
        if isinstance(error, commands.MissingRequiredArgument):
            cmd = ctx.command.name
            param = error.param.name # Konsa argument missing hai (user, time etc)
            
            # Har command ke liye photo jaisa Usage define karna
            usage_dict = {
                "mute": "!mute <user> <time> [reason]",
                "ban": "!ban <user> [reason]",
                "kick": "!kick <user> [reason]",
                "warn": "!warn <user> [reason]",
                "clear": "!clear <amount>",
                "afk": "!afk [reason]"
            }

            usage = usage_dict.get(cmd, f"!{cmd} <arguments>")

            # Photo jaisa response formatting
            error_msg = (
                f"**Missing required argument: {param}**\n"
                f"Usage: `{usage}`"
            )
            await ctx.send(error_msg)

        # 2. Member Not Found (Galat user mention karne par)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"❌ **Could not find that user.** Please mention a valid member.")

        # 3. Bad Argument (Number ki jagah text daalne par)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ **Invalid argument provided.** Please check the command usage.")

        # 4. Missing Permissions (Moderator nahi hai)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"🚫 **You don't have permission to use `!{ctx.command.name}`!**")

        # 5. Command Not Found (Galat spelling)
        elif isinstance(error, commands.CommandNotFound):
            pass # Isse bot khali message par reply nahi dega

        else:
            # Baki errors console mein dikhenge
            print(f"Unhandled Error: {error}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
    
