import discord
from discord.ext import commands
from discord import app_commands
import datetime

class CaseSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="case", description="Retrieve a moderation case")
    @app_commands.describe(case_id="Case ID (e.g. 1 or #1)")
    async def case(self, ctx, *, case_id: str):

        # 🧹 CLEAN INPUT
        clean_id = case_id.replace("#", "").strip()
        guild_id = str(ctx.guild.id)

        # 📥 FETCH FROM DATABASE
        case_data = self.bot.db.get(f"cases.{guild_id}.cases.{clean_id}")

        if not case_data:
            return await ctx.send(f"❌ Case #{clean_id} not found.")

        # ⏱ TIME PARSE
        try:
            timestamp = datetime.datetime.fromisoformat(
                case_data["timestamp"].replace("Z", "+00:00")
            )
        except:
            timestamp = discord.utils.utcnow()

        # 🎨 EMBED
        embed = discord.Embed(
            title=f"📁 Case #{clean_id} | {case_data['action']}",
            color=discord.Color.blurple(),
            timestamp=timestamp
        )

        embed.add_field(
            name="👤 User",
            value=f"**{case_data['target_name']}**\n(`{case_data['target_id']}`)",
            inline=True
        )

        embed.add_field(
            name="🛡️ Moderator",
            value=f"{case_data['moderator']}",
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=f"```{case_data['reason']}```",
            inline=False
        )

        embed.set_footer(text=f"Server: {ctx.guild.name}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CaseSystem(bot))
