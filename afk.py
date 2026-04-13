import discord
from discord.ext import commands

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    @commands.command()
    async def afk(self, ctx, *, reason="I'm AFK"):
        self.afk_users[ctx.author.id] = reason
        await ctx.send(f"✅ {ctx.author.mention}, you are now AFK: **{reason}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. If an AFK user sends a message, remove AFK
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            await message.channel.send(f"Welcome back {message.author.mention}! Your AFK has been removed.", delete_after=5)

        # 2. If someone mentions an AFK user
        for mention in message.mentions:
            if mention.id in self.afk_users:
                reason = self.afk_users[mention.id]
                await message.reply(f"⚠️ **{mention.name}** is currently AFK: {reason}")

async def setup(bot):
    await bot.add_cog(AFK(bot))
  
