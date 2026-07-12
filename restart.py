import discord
from discord.ext import commands
import os
import sys
import json

class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.restart_file = "./data/restart_info.json"
        
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.dot_green = "<:starlaDotGreen:1525756444782104597>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.cross = "<:starlacross:1525756266604007464>"
        
        # Bot start hote hi pending restart check karega
        self.bot.loop.create_task(self.check_restart())

    async def check_restart(self):
        await self.bot.wait_until_ready()
        if os.path.exists(self.restart_file):
            try:
                with open(self.restart_file, "r") as f:
                    data = json.load(f)
                
                channel = self.bot.get_channel(data["channel_id"])
                if channel:
                    # 📢 RESTART SUCCESS EMBED
                    embed = discord.Embed(
                        description=f"{self.dot_green} **Bot has been restarted successfully!**",
                        color=0x2b2d31
                    )
                    await channel.send(embed=embed)
                
                # Message bhejne ke baad data file clear clean kar dein
                os.remove(self.restart_file)
            except Exception as e:
                print(f"Error sending restart message: {e}")

    @commands.command(name="restart", description="Restarts the bot instance (Owner Only)")
    async def restart(self, ctx):
        # 🔐 DYNAMIC OWNER CHECK
        # Agar aap hi execution kar rahe ho ya bot owner ID matched hai
        is_owner = await self.bot.is_owner(ctx.author)
        if not is_owner and ctx.author.id != 1140926535935725711:
            return # Silent ignore for non-owners

        # 📢 RESTART INITIALIZED EMBED
        embed = discord.Embed(
            description=f"{self.dot_black} **Restarting the bot instance...**\n{self.arrow} *Please wait while the connection re-establishes.*",
            color=0x2b2d31
        )
        await ctx.send(embed=embed)
        
        # Channel ID save karein taaki restart ke baad bot ko target pata ho
        if not os.path.exists("./data"):
            os.makedirs("./data")
            
        with open(self.restart_file, "w") as f:
            json.dump({"channel_id": ctx.channel.id}, f)

        # Connections safely close karein aur process reload karein
        await self.bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot):
    await bot.add_cog(Restart(bot))
    
