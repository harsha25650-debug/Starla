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

    # Cog load hote hi database connect karega
    async def cog_load(self):
        self.db = await aiosqlite.connect("./data/giveaways.db") # Data folder use karna Railway ke liye best hai
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

    # 🔄 AUTO CHECK (Har 10 second mein check karega)
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
                await self.end_giveaway(*row)

    # 🎉 END GIVEAWAY FUNCTION
    async def end_giveaway(self, msg_id, channel_id, prize, winners_count):
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
        
        try:
            msg = await channel.fetch_message(msg_id)
            reaction = discord.utils.get(msg.reactions, emoji="🎉")

            users = []
            if reaction:
                users = [u async for u in reaction.users() if not u.bot]

            winners = random.sample(users, min(len(users), winners_count)) if users else []

            embed = msg.embeds[0]

            if winners:
                w_mentions = ", ".join([w.mention for w in winners])
                embed.color = discord.Color.red()
                embed.description = f"**Giveaway Ended!**\n\nWinners: {w_mentions}\nHosted by: {embed.fields[0].value if embed.fields else 'Unknown'}"
                await msg.edit(embed=embed)

                await channel.send(f"🎉 Congrats {w_mentions}! You won **{prize}**!\n{msg.jump_url}")
            else:
                embed.color = discord.Color.default()
                embed.description = "**Giveaway Ended!**\n\nNo valid participants."
                await msg.edit(embed=embed)
                await channel.send(f"⚠️ No one won the giveaway for **{prize}**.")

        except Exception as e:
            print(f"Error ending giveaway: {e}")

        await self.db.execute("UPDATE giveaways SET active = 0 WHERE message_id = ?", (msg_id,))
        await self.db.commit()

    # ⏱ TIME PARSER
    def parse_time(self, time_str):
        time_str = time_str.lower().strip()
        patterns = {
            r"(\d+)\s*(s|sec|secs|second|seconds)": 1,
            r"(\d+)\s*(m|min|mins|minute|minutes)": 60,
            r"(\d+)\s*(h|hr|hrs|hour|hours)": 3600,
            r"(\d+)\s*(d|day|days)": 86400
        }
        for pattern, multiplier in patterns.items():
            match = re.search(pattern, time_str)
            if match:
                return int(match.group(1)) * multiplier
        return None

    # 🚀 START COMMAND
    @commands.command(name="gstart")
    @commands.has_permissions(manage_messages=True)
    async def gstart(self, ctx, time: str, winners: int, *, prize: str):
        seconds = self.parse_time(time)
        if not seconds:
            return await ctx.send("❌ Invalid time format! Use `10m`, `1h`, etc.")

        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)

        embed = discord.Embed(
            title=f"🎉 Giveaway: {prize}",
            description=(
                f"React with 🎉 to enter!\n"
                f"Ends: <t:{int(end_time.timestamp())}:R>\n"
                f"Winners: **{winners}**"
            ),
            color=discord.Color.blue()
        )
        embed.add_field(name="Hosted by", value=ctx.author.mention)
        embed.set_footer(text=f"Ends at")
        embed.timestamp = end_time

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")

        await self.db.execute(
            "INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?)",
            (msg.id, ctx.channel.id, end_time, prize, winners, 1)
        )
        await self.db.commit()

    # 🛑 END COMMAND
    @commands.command(name="gend")
    @commands.has_permissions(manage_messages=True)
    async def gend(self, ctx, message_id: int = None):
        if message_id is None:
            async with self.db.execute(
                "SELECT message_id, channel_id, prize, winners FROM giveaways WHERE active = 1 AND channel_id = ? ORDER BY message_id DESC LIMIT 1",
                (ctx.channel.id,)
            ) as cursor:
                row = await cursor.fetchone()
        else:
            async with self.db.execute(
                "SELECT message_id, channel_id, prize, winners FROM giveaways WHERE message_id = ? AND active = 1",
                (message_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if not row:
            return await ctx.send("❌ No active giveaway found.")

        await self.end_giveaway(*row)
        await ctx.send("✅ Giveaway ended early.")

# 🔥 YE FUNCTION ZAROORI HAI (Iske bina bot error deta hai)
async def setup(bot):
    await bot.add_cog(Giveaway(bot))
