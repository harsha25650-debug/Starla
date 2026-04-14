import discord
from discord.ext import commands
import os
import sys
import json

class Restart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.restart_file = "./data/restart_info.json"
        # Bot start hote hi check karega ki kya koi restart pending tha
        self.bot.loop.create_task(self.check_restart())

    async def check_restart(self):
        await self.bot.wait_until_ready()
        if os.path.exists(self.restart_file):
            try:
                with open(self.restart_file, "r") as f:
                    data = json.load(f)
                
                channel = self.bot.get_channel(data["channel_id"])
                if channel:
                    await channel.send("✅ **Bot restarted successfully!**")
                
                # Message bhejne ke baad file delete kar dein
                os.remove(self.restart_file)
            except Exception as e:
                print(f"Error sending restart message: {e}")

    @commands.command(name="restart")
    async def restart(self, ctx):
        # Owner Check
        owner_id = 1140926535935725711 

        if ctx.author.id != owner_id:
            return 

        await ctx.send("🔄 **Restarting bot...**")
        
        # Channel ID save karein taaki restart ke baad bot ko pata ho kahan message bhejna hai
        if not os.path.exists("./data"):
            os.makedirs("./data")
            
        with open(self.restart_file, "w") as f:
            json.dump({"channel_id": ctx.channel.id}, f)

        # Connections close karein aur restart karein
        await self.bot.close()
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot):
    await bot.add_cog(Restart(bot))
