import discord
from discord.ext import commands
import asyncio
import random
import datetime

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = [] # IDs save karne ke liye taaki dubara end na ho

    def convert(self, time):
        pos = ["s", "m", "h", "d"]
        time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time[-1]
        if unit not in pos:
            return -1
        try:
            val = int(time[:-1])
        except:
            return -2
        return val * time_dict[unit]

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, time: str, winners: int, *, prize: str):
        seconds = self.convert(time)
        if seconds == -1:
            return await ctx.send("❌ Time unit galat hai (s/m/h/d use karein)")
        elif seconds == -2:
            return await ctx.send("❌ Time integer hona chahiye")

        # Photo jaisa Embed Layout
        ends_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        embed = discord.Embed(
            title=f"🎁 {prize}",
            description=f"React with 🎉 to enter!\nEnds in: <t:{int(ends_at.timestamp())}:R>\nHosted by: {ctx.author.mention}",
            color=discord.Color.blue(),
            timestamp=ends_at
        )
        embed.set_footer(text=f"Winners: {winners} | Ends at")
        
        g_msg = await ctx.send("🎊 **GIVEAWAY STARTED** 🎊", embed=embed)
        await g_msg.add_reaction("🎉")
        
        self.active_giveaways.append(g_msg.id)

        await asyncio.sleep(seconds)

        # Automatic end agar manually end nahi kiya gaya
        if g_msg.id in self.active_giveaways:
            await self.end_giveaway(g_msg.id, winners, prize, ctx.channel)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def gend(self, ctx, msg_id: int):
        if msg_id not in self.active_giveaways:
            return await ctx.send("❌ Ye giveaway pehle hi end ho chuka hai ya ID galat hai.")
        
        # Giveaway details fetch karna message se
        try:
            msg = await ctx.channel.fetch_message(msg_id)
            prize = msg.embeds[0].title.replace("🎁 ", "")
            winners_str = msg.embeds[0].footer.text.split("|")[0].replace("Winners: ", "")
            winners = int(winners_str)
            
            await self.end_giveaway(msg_id, winners, prize, ctx.channel)
            await ctx.send(f"✅ Giveaway (ID: {msg_id}) manually end kar diya gaya.")
        except:
            await ctx.send("❌ Message nahi mila. Kya aap sahi channel mein hain?")

    async def end_giveaway(self, msg_id, winners, prize, channel):
        if msg_id not in self.active_giveaways:
            return
        
        self.active_giveaways.remove(msg_id)
        msg = await channel.fetch_message(msg_id)
        
        users = [user async for user in msg.reactions[0].users() if not user.bot]
        
        if len(users) == 0:
            return await channel.send(f"❌ Giveaway for **{prize}** ended, but no one reacted.")

        winning_announcement = []
        for _ in range(min(winners, len(users))):
            winner = random.choice(users)
            winning_announcement.append(winner.mention)
            users.remove(winner)

        # End Embed
        end_embed = msg.embeds[0]
        end_embed.description = f"Giveaway Ended!\nWinner(s): {', '.join(winning_announcement)}"
        end_embed.color = discord.Color.red()
        await msg.edit(content="🎊 **GIVEAWAY ENDED** 🎊", embed=end_embed)
        
        await channel.send(f"Congratulations {', '.join(winning_announcement)}! You won the **{prize}**! 🎁")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
      
