import discord
from discord.ext import commands
import difflib # Ye library milti-julti commands dhoondne ke liye hai

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # 1. Agar command dhoondne mein galti ho (CommandNotFound)
        if isinstance(error, commands.CommandNotFound):
            # User ne jo galat command likhi hai use nikalna
            cmd_invoked = ctx.invoked_with
            # Bot ki saari available commands ki list
            all_commands = [cmd.name for cmd in self.bot.commands]
            
            # Difflib se milti-julti commands dhoondna (Advanced Logic)
            matches = difflib.get_close_matches(cmd_invoked, all_commands, n=1, cutoff=0.6)

            if matches:
                suggested_cmd = matches[0]
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"Did you mean `!{suggested_cmd}`?\nPlease type the full command correctly.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed, delete_after=10)
            else:
                # Agar koi milti-julti command na mile
                await ctx.send(f"❌ Unknown command. Type `!help` for a list of commands.", delete_after=5)

        # 2. Agar user ke paas Permission na ho
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"🚫 You don't have permission to use this command!", delete_after=5)

        # 3. Agar koi argument miss ho (e.g. !ban likha par user mention nahi kiya)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Missing arguments! Please check how to use the command.", delete_after=5)

        # Baki errors ke liye console mein print karega
        else:
            print(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
  
