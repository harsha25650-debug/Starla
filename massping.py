import discord
from discord.ext import commands
import asyncio
import random

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 📥 GET ACCESS LIST
    def get_access(self, guild_id):
        return self.bot.db.get(f"mpaccess.{guild_id}", [])

    # 💾 ADD ACCESS
    def add_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(f"mpaccess.{guild_id}", users)

    # ❌ REMOVE ACCESS
    def remove_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(f"mpaccess.{guild_id}", users)

    # 🔐 UPDATED ACCESS CHECK
    async def check_permissions(self, ctx):
        # 1. Check if Bot Owner
        if await self.bot.is_owner(ctx.author):
            return True
        
        # 2. Check if Server Owner
        if ctx.author.id == ctx.guild.owner_id:
            return True
            
        # 3. Check Database Access List
        users = self.get_access(ctx.guild.id)
        if ctx.author.id in users:
            return True
            
        return False

    def is_running(self, channel_id):
        return self.active.get(channel_id, False)

    # ✅ GIVE ACCESS
    @commands.command()
    @commands.is_owner()
    async def mpaccess(self, ctx, member: discord.Member):
        self.add_access(ctx.guild.id, member.id)
        await ctx.send(f"✅ MP access granted for {member.mention}")

    # ❌ REMOVE ACCESS
    @commands.command()
    @commands.is_owner()
    async def mpremove(self, ctx, member: discord.Member):
        self.remove_access(ctx.guild.id, member.id)
        await ctx.send(f"❌ MP access removed for {member.mention}")

    # 🚀 MASSPING
    @commands.command()
    async def massping(self, ctx, member: discord.Member, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.send("❌ Access denied | owner/premiumUser only command")

        if amount <= 0:
            return await ctx.send("Invalid amount.")

        if self.is_running(ctx.channel.id):
            return await ctx.send("⚠️ Already running in this channel.")

        self.active[ctx.channel.id] = True
        await ctx.send(f"⚡ Starting mass ping x{amount}")

        sent = 0
        while sent < amount:
            if not self.active.get(ctx.channel.id):
                return # Task stopped via mpstop

            batch = min(5, amount - sent)
            for _ in range(batch):
                if not self.active.get(ctx.channel.id): break
                await ctx.send(member.mention)
                sent += 1

            await asyncio.sleep(0.5)

        self.active[ctx.channel.id] = False
        await ctx.send("✅ Done.")

    # ⚡ FAST LOOP
    @commands.command()
    async def mploop(self, ctx, member: discord.Member, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.send("❌ Access denied | owner/premiumUser only command")

        if amount > 500: amount = 500
        if amount <= 0: return

        self.active[ctx.channel.id] = True
        await ctx.send(f"⚡ Fast loop ping x{amount}")

        for i in range(amount):
            if not self.active.get(ctx.channel.id):
                return await ctx.send("🛑 Stopped.")

            await ctx.send(member.mention)
            if i % 5 == 0:
                await asyncio.sleep(0.2)

        self.active[ctx.channel.id] = False
        await ctx.send("✅ Done.")

    # 🚀 FAST MESSAGE
    @commands.command()
    async def mpfast(self, ctx, member: discord.Member, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.send("❌ Access denied | owner/premiumUser only command")

        if amount > 87: amount = 87
        if amount <= 0: return

        self.active[ctx.channel.id] = True
        msg = " ".join([member.mention for _ in range(amount)])
        
        await ctx.send(msg)
        self.active[ctx.channel.id] = False

    # 👻 GHOSTPING
    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def ghostping(self, ctx, member: discord.Member, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.send("❌ Access denied | owner/premiumUser only command")

        if amount > 500: amount = 500
        if amount <= 0: return

        self.active[ctx.channel.id] = True

        try:
            await ctx.message.delete()
        except:
            pass

        for _ in range(amount):
            if not self.active.get(ctx.channel.id):
                break

            msg = await ctx.send(member.mention)
            await asyncio.sleep(0.2)
            try:
                await msg.delete()
            except:
                pass

        self.active[ctx.channel.id] = False

    # 🛑 STOP
    @commands.command()
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.send("❌ Access denied | owner/premiumUser only command")

        if self.is_running(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send("🛑 All ping tasks stopped for this channel.")
        else:
            await ctx.send("Nothing is running here.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
