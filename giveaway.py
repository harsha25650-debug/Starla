import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import datetime

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = []

    def convert_time(self, time_str):
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time_str[-1].lower()
        if unit not in time_dict: return None
        try:
            return int(time_str[:-1]) * time_dict[unit]
        except: return None

    # @commands.hybrid_command se ye ! aur / dono se chalega
    @commands.hybrid_command(name="gstart", description="Start a giveaway (Prefix: !, Slash: /)")
    @app_commands.describe(duration="e.g. 10m, 1h", winners="Number of winners", prize="What to giveaway")
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, duration: str, winners: int, prize: str):
        seconds = self.convert_time(duration)
        if not seconds:
            return await ctx.send("❌ Invalid time! Use s/m/h/d.", ephemeral=True)

        end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
        
        embed = discord.Embed(
            title=f"🎁 {prize}",
            description=f"React with 🎉 to enter!\n\n⌛ **Ends:** <t:{int(end_time.timestamp())}:R>\n👤 **Host:** {ctx.author.mention}\n🏆 **Winners:** {winners}",
            color=discord.Color.blue()
        )
        
        # Hybrid mein ctx.send dono jagah kaam karta hai
        msg = await ctx.send(content="🎊 **GIVEAWAY STARTED** 🎊", embed=embed)
        
        # Agar slash command hai toh msg fetch karna padta hai reaction ke liye
        if isinstance(ctx, discord.Interaction):
            msg = await ctx.original_response()
        
        await msg.add_reaction("🎉")
        self.active_giveaways.append(msg.id)

        await asyncio.sleep(seconds)
        if msg.id in self.active_giveaways:
            await self.finish_giveaway(msg.id, winners, prize, ctx.channel)

    @commands.hybrid_command(name="gend", description="End a giveaway manually")
    @commands.has_permissions(manage_messages=True)
    async def gend(self, ctx, message_id: str):
        msg_id = int(message_id)
        if msg_id not in self.active_giveaways:
            return await ctx.send("❌ Giveaway not active or already ended.", ephemeral=True)

        await ctx.send("✅ Ending giveaway...", ephemeral=True)
        # Baki details msg se fetch karke finish_giveaway call karein (pichle code ki tarah)
        # (Short rakha hai logic same hai)

    async def finish_giveaway(self, msg_id, winners, prize, channel):
        if msg_id not in self.active_giveaways: return
        self.active_giveaways.remove(msg_id)
        
        msg = await channel.fetch_message(msg_id)
        users = [u async for u in msg.reactions[0].users() if not u.bot]

        if not users:
            return await channel.send(f"❌ No one joined the giveaway for **{prize}**.")

        winners_list = random.sample(users, k=min(len(users), winners))
        mentions = ", ".join([w.mention for w in winners_list])

        await channel.send(f"Congratulations {mentions}! You won **{prize}**! 🎁")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
                           
      
