import discord
from discord.ext import commands
from discord import app_commands
import datetime

class CaseSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        self.cross = "<:starlacross:1525756266604007464>"
        
        # Action Dots Map (Dynamic display ke liye)
        self.dots = {
            "ban": "<:starlaDotRed:1525756464692596886>",
            "unban": "<:starlaDotGreen:1525756444782104597>",
            "kick": "<:starlaDotOrange:1525756452487168121>",
            "mute": "<:starlaDotYellow:1525756269934411958>",
            "unmute": "<:starlaDotBlue:1525756437224099862>",
            "clear": "<:topggDotPink:1525756454345375764>",
            "purge": "<:topggDotPink:1525756454345375764>"
        }

    @commands.hybrid_command(name="case", description="Retrieve a moderation case info from the database")
    @app_commands.describe(case_id="Case ID number (e.g. 1 or #1)")
    async def case(self, ctx, *, case_id: str):

        # 🧹 CLEAN INPUT
        clean_id = case_id.replace("#", "").strip()
        guild_id = str(ctx.guild.id)

        # 📥 FETCH FROM DATABASE
        case_data = self.bot.db.get(f"cases.{guild_id}.cases.{clean_id}")

        if not case_data:
            return await ctx.send(f"{self.cross} **Error:** Case `#{clean_id}` not found in the database.")

        # ⏱ TIME PARSE
        try:
            timestamp = datetime.datetime.fromisoformat(
                case_data["timestamp"].replace("Z", "+00:00")
            )
        except:
            timestamp = discord.utils.utcnow()

        # 🎨 DYNAMIC DOT DETECTION
        action = case_data['action'].lower()
        dot_indicator = self.dots.get(action, "<:starlaDotBlack:1525756435089063948>") # Default black dot agar koi unknown action ho

        # 🖼 SLEEK EMBED DESIGN
        embed = discord.Embed(
            title=f"{self.ico_info} Case Details | #{clean_id}",
            color=0x2b2d31, # Starla Standard Dark Color
            timestamp=timestamp
        )

        # Main Info Area
        embed.description = (
            f"{dot_indicator} **Action:** {case_data['action'].upper()}\n\n"
            f"{self.arrow} **Target User:** {case_data['target_name']} (`{case_data['target_id']}`)\n"
            f"{self.arrow} **Moderator:** {case_data['moderator']}\n\n"
            f"**Reason:**\n```{case_data['reason']}```"
        )

        embed.set_footer(text=f"Server: {ctx.guild.name} • Case Loged")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CaseSystem(bot))
        
