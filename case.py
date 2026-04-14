import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

class CaseSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "./data/cases.json"

    @commands.hybrid_command(name="case", description="Retrieve details of a moderation case for this server")
    @app_commands.describe(case_id="The case ID (e.g. 1 or #1)")
    async def case(self, ctx, *, case_id: str):
        # 1. Input clean-up
        clean_id = case_id.replace("#", "").strip()
        guild_id = str(ctx.guild.id)

        if not os.path.exists(self.db_file):
            return await ctx.send("❌ No cases recorded yet.")

        with open(self.db_file, "r") as f:
            data = json.load(f)

        # 2. Check if this server has any data
        if guild_id not in data or clean_id not in data[guild_id]["cases"]:
            return await ctx.send(f"❌ Case #{clean_id} not found for this server.")

        info = data[guild_id]["cases"][clean_id]
        
        # 3. Embed Response
        embed = discord.Embed(
            title=f"Case #{clean_id} | {info['action']}",
            color=0x2b2d31,
            timestamp=datetime.datetime.fromisoformat(info['timestamp'].replace('Z', '+00:00'))
        )
        embed.add_field(name="👤 User", value=f"**{info['target_name']}**\n(`{info['target_id']}`)", inline=True)
        embed.add_field(name="🛡️ Moderator", value=f"{info['moderator']}", inline=True)
        embed.add_field(name="📝 Reason", value=f"```{info['reason']}```", inline=False)
        embed.set_footer(text=f"Server: {ctx.guild.name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CaseSystem(bot))
        
