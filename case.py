import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class CaseSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Path for Railway Volume
        self.db_file = "/data/cases.json"

    @commands.hybrid_command(name="case", description="Retrieve full details of a specific moderation case")
    @app_commands.describe(case_number="The numeric ID of the case you want to view")
    async def case(self, ctx, case_number: int):
        # 1. Check if database exists
        if not os.path.exists(self.db_file):
            return await ctx.send("❌ **Database Error:** No cases have been recorded yet.", ephemeral=True)

        # 2. Load the data
        with open(self.db_file, "r") as f:
            data = json.load(f)
        
        case_id = str(case_number)

        # 3. Check if specific case exists
        if case_id not in data:
            return await ctx.send(f"❌ **Case Not Found:** Case #{case_id} does not exist in the database.", ephemeral=True)

        info = data[case_id]
        
        # 4. Professional Dark Embed (Zeppelin Style)
        embed = discord.Embed(
            title=f"Case #{case_id} | {info['action']}",
            color=0x2b2d31, # Dark Grey/Black theme
            timestamp=datetime.datetime.fromisoformat(info.get('timestamp', datetime.datetime.utcnow().isoformat()))
        )
        
        embed.add_field(
            name="👤 User", 
            value=f"**{info['target_name']}**\n(`{info['target_id']}`)", 
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Moderator", 
            value=f"{info['moderator']}", 
            inline=True
        )
        
        embed.add_field(
            name="📝 Reason", 
            value=f"```{info['reason']}```", 
            inline=False
        )
        
        embed.set_footer(text="NovaX Security Database")
        
        # Use ctx.send so it works for both Prefix and Slash
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CaseSystem(bot))
    
  
