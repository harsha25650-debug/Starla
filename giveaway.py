import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import random
import re
import aiosqlite

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = None
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    async def cog_load(self):
        # Database initialize karna
        self.db = await aiosqlite.connect("giveaways.db")
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                end_time TIMESTAMP,
                prize TEXT,
                winners INTEGER,
                active INTEGER
            )
        """)
        await self.db.commit()

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        if not self.db:
            return
        
        now = datetime.datetime.utcnow()
        async with self.db.execute(
            "SELECT message_id, channel_id, prize, winners FROM giveaways WHERE active = 1 AND end_time <= ?", 
            (now,)
        ) as cursor:
            async for row in cursor:
                await self.end_giveaway(row[0], row[1], row[2], row[3])

    async def end_giveaway(self, msg_id, channel_id, prize, winners_count):
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
        
        try:
            msg = await channel.fetch_message(msg_id)
            reaction = discord.utils.get(msg.reactions, emoji="🎉")
            
            if not reaction:
                users = []
            else:
                users = [user async for user in reaction.users() if not user.bot]

            if len(users) < winners_count:
                winners = users
            else:
                winners = random.sample(users, winners_count)

            if winners:
                w_mentions = ", ".join([w.mention for w in winners])
                embed = msg.embeds[0]
                embed.color = discord.Color.red()
                embed.description = f"**Giveaway Ended!**\n\nWinners: {w_mentions}\nHosted by: {msg.author.mention}"
                embed.set_footer(text="Ended at")
                embed.timestamp = datetime.datetime.utcnow()
                await msg.edit(embed=embed)
                await channel.send(f"Congratulations {w_mentions}! You won **{prize}**!\n{msg.jump_url}")
            else:
                embed = msg.embeds[0]
                embed.color = discord.Color.default()
                embed.description = "**Giveaway Ended!**\n\nNo winners could be determined (not enough participants)."
                await msg.edit(embed=embed)
                await channel.send(f"Giveaway for **{prize}** ended, but no one participated.")

        except Exception as e:
            print(f"Error ending giveaway: {e}")

        await self.db.execute("UPDATE giveaways SET active = 0 WHERE message_id = ?", (msg_id,))
        await self.db.commit()

    def parse_time(self, time_str):
        pos = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        match = re.match(r"^(\d+)([smhd])$", time_str.lower())
        if match:
            return int(match.group(1)) * pos[match.group(2)]
        return None

    @commands.command(name="gstart")
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, time: str, winners: int, *, prize: str):
        seconds = self.parse_time(time)
        if not seconds:
            return await ctx.send("Sahi format use karein! Example: `!gstart 15d 2 Nitro Boost` (s, m, h, d)")

        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        
        embed = discord.Embed(
            title=f"🎉 {prize}",
            description=f"React with 🎉 to enter!\nEnds: <t:{int(end_time.timestamp())}:R> (<t:{int(end_time.timestamp())}:f>)\nWinners: **{winners}**\nHosted by: {ctx.author.mention}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Ends at")
        embed.timestamp = end_time
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        await self.db.execute(
            "INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?)",
            (msg.id, ctx.channel.id, end_time, prize, winners, 1)
        )
        await self.db.commit()

    @commands.command(name="gend")
    @commands.has_permissions(manage_messages=True)
    async def gend(self, ctx, message_id: int = None):
        if message_id is None:
            async with self.db.execute(
                "SELECT message_id, channel_id, prize, winners FROM giveaways WHERE active = 1 AND channel_id = ? ORDER BY end_time DESC LIMIT 1", 
                (ctx.channel.id,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            async with self.db.execute(
                "SELECT message_id, channel_id, prize, winners FROM giveaways WHERE message_id = ? AND active = 1", 
                (message_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if row:
            await self.end_giveaway(row[0], row[1], row[2], row[3])
            await ctx.send("Giveaway manually end kar diya gaya hai.", delete_after=5)
            await ctx.message.delete()
        else:
            await ctx.send("Koi active giveaway nahi mila!", delete_after=5)

# Cog ko setup karne ke liye function
async def setup(bot):
    await bot.add_cog(Giveaway(bot))
