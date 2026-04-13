import discord
from discord.ext import commands
import json

class Case(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_file = "cases.json"

    @commands.command()
    async def case(self, ctx, case_num: str):
        # Hash (#) symbol handle karne ke liye
        num = case_num.replace("#", "")
        
        try:
            with open(self.db_file, "r") as f:
                data = json.load(f)
            
            if num in data:
                case_info = data[num]
                embed = discord.Embed(
                    title=f"Case #{num} Information",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Action", value=case_info["action"], inline=True)
                embed.add_field(name="Target", value=case_info["target"], inline=True)
                embed.add_field(name="Moderator", value=case_info["moderator"], inline=True)
                embed.add_field(name="Reason", value=case_info["reason"], inline=False)
                embed.set_footer(text="NovaX Security Database")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Case #{num} database mein nahi mila.")
        except FileNotFoundError:
            await ctx.send("❌ Abhi tak koi cases record nahi huye hain.")

async def setup(bot):
    await bot.add_cog(Case(bot))
  
