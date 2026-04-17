import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 📥 GET ACCESS LIST
    def get_access(self, guild_id):
        if guild_id is None:
            return []
        return self.bot.db.get(f"mpaccess.{guild_id}", [])

    # 💾 ADD ACCESS
    def add_access(self, guild_id, user_id):
        if guild_id is None:
            return
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(f"mpaccess.{guild_id}", users)

    # ❌ REMOVE ACCESS
    def remove_access(self, guild_id, user_id):
        if guild_id is None:
            return
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(f"mpaccess.{guild_id}", users)

    # 🔐 PERMISSION CHECK (DM SUPPORT ADDED)
    async def check_permissions(self, interaction_or_ctx):
        user = interaction_or_ctx.user if isinstance(interaction_or_ctx, discord.Interaction) else interaction_or_ctx.author
        guild = interaction_or_ctx.guild

        # ✅ BOT OWNER
        if await self.bot.is_owner(user):
            return True

        # ✅ DM → allow only owner
        if guild is None:
            return await self.bot.is_owner(user)

        # ✅ SERVER OWNER
        if user.id == guild.owner_id:
            return True

        # ✅ DB ACCESS
        users = self.get_access(guild.id)
        if user.id in users:
            return True

        return False

    def is_running(self, channel_id):
        return self.active.get(channel_id, False)

    # =========================
    # 🚀 MASSPING (HYBRID)
    # =========================
    @commands.hybrid_command(name="massping", description="Spam ping a user")
    @app_commands.describe(member="User to ping", amount="Number of pings")
    async def massping(self, ctx, member: discord.User, amount: int):

        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied")

        if amount <= 0:
            return await ctx.reply("Invalid amount")

        channel_id = ctx.channel.id

        if self.is_running(channel_id):
            return await ctx.reply("⚠️ Already running here")

        self.active[channel_id] = True
        await ctx.reply(f"⚡ Starting mass ping x{amount}")

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break

            await ctx.send(member.mention)
            sent += 1

            if sent % 5 == 0:
                await asyncio.sleep(0.5)

        self.active[channel_id] = False
        await ctx.send("✅ Done")

    # =========================
    # 👻 GHOSTPING
    # =========================
    @commands.hybrid_command(name="ghostping", description="Ghost ping user")
    async def ghostping(self, ctx, member: discord.User, amount: int):

        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied")

        if amount <= 0:
            return

        channel_id = ctx.channel.id
        self.active[channel_id] = True

        for _ in range(amount):
            if not self.active.get(channel_id):
                break

            msg = await ctx.send(member.mention)
            await asyncio.sleep(0.3)

            try:
                await msg.delete()
            except:
                pass

        self.active[channel_id] = False

    # =========================
    # ⚡ FAST PING
    # =========================
    @commands.hybrid_command(name="mpfast", description="Fast multi ping")
    async def mpfast(self, ctx, member: discord.User, amount: int):

        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied")

        if amount > 80:
            amount = 80

        msg = " ".join([member.mention for _ in range(amount)])
        await ctx.send(msg)

    # =========================
    # 🛑 STOP
    # =========================
    @commands.hybrid_command(name="mpstop", description="Stop mass ping")
    async def mpstop(self, ctx):

        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied")

        channel_id = ctx.channel.id

        if self.is_running(channel_id):
            self.active[channel_id] = False
            await ctx.reply("🛑 Stopped")
        else:
            await ctx.reply("Nothing running")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
