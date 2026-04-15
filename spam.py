import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spam = {}

    # 📥 GET ACCESS
    def get_access(self, guild_id):
        return self.bot.db.get(f"spaccess.{guild_id}", [])

    # 💾 ADD ACCESS
    def add_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    # ❌ REMOVE ACCESS
    def remove_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    # 🔐 CHECK ACCESS
    def has_access(self, ctx):
        users = self.get_access(ctx.guild.id)
        return ctx.author.id == ctx.bot.owner_id or ctx.author.id in users

    # ✅ GIVE ACCESS
    @commands.command(name="spaccess")
    @commands.is_owner()
    async def spaccess(self, ctx, member: discord.Member):
        self.add_access(ctx.guild.id, member.id)
        await ctx.send(f"✅ Spam access granted for {member.mention}")

    # ❌ REMOVE ACCESS
    @commands.command(name="spremove")
    @commands.is_owner()
    async def spremove(self, ctx, member: discord.Member):
        self.remove_access(ctx.guild.id, member.id)
        await ctx.send(f"❌ Spam access removed for {member.mention}")

    # 🚀 SPAM COMMAND
    @commands.command(name="spam")
    async def spam(self, ctx, *, args=None):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if not args:
            return await ctx.send("❌ Usage: !spam <message> <amount>")

        try:
            parts = args.rsplit(" ", 1)
            message = parts[0]
            amount = int(parts[1])
        except:
            return await ctx.send("❌ Invalid format. Example: !spam hello 10")

        if amount <= 0:
            return await ctx.send("❌ Amount must be greater than 0.")

        if amount > 500:
            return await ctx.send("⚠️ Max limit is 500.")

        self.active_spam[ctx.channel.id] = True

        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            if not self.active_spam.get(ctx.channel.id):
                break

            await ctx.send(message)
            await asyncio.sleep(0.3)

        self.active_spam.pop(ctx.channel.id, None)

    # 🛑 STOP
    @commands.command(name="spstop")
    async def spstop(self, ctx):

        if not self.has_access(ctx):
            return await ctx.send("❌ You don't have permission.")

        if self.active_spam.get(ctx.channel.id):
            self.active_spam[ctx.channel.id] = False
            await ctx.send("🛑 Spam stopped.")
        else:
            await ctx.send("⚠️ No active spam.")

        try:
            await ctx.message.delete()
        except:
            pass

    # ❗ ERROR HANDLER
    @spam.error
    @spstop.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("⛔ Owner only command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: !spam <message> <amount>")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid number.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Spam(bot))
