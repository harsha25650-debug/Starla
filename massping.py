import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 📥 GET ACCESS LIST (DM support added)
    def get_access(self, guild_id):
        # DMs ke liye alag key use karenge taaki data mix na ho
        key = f"mpaccess.{guild_id}" if guild_id else "mpaccess.global"
        return self.bot.db.get(key, [])

    # 💾 ADD ACCESS
    def add_access(self, guild_id, user_id):
        key = f"mpaccess.{guild_id}" if guild_id else "mpaccess.global"
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(key, users)

    # ❌ REMOVE ACCESS
    def remove_access(self, guild_id, user_id):
        key = f"mpaccess.{guild_id}" if guild_id else "mpaccess.global"
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(key, users)

    # 🔐 PERMISSION CHECK
    async def check_permissions(self, interaction_or_ctx):
        user = interaction_or_ctx.user if isinstance(interaction_or_ctx, discord.Interaction) else interaction_or_ctx.author
        guild = interaction_or_ctx.guild

        if await self.bot.is_owner(user):
            return True
        
        # Server context
        if guild:
            if user.id == guild.owner_id:
                return True
            if user.id in self.get_access(guild.id):
                return True
        
        # DM/Global context
        if user.id in self.get_access(None):
            return True

        return False

    # =========================
    # 🔑 ACCESS COMMANDS (Naya Section)
    # =========================
    
    @commands.hybrid_command(name="mpaccess", description="Give massping access to a user")
    @app_commands.describe(member="User to give access")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpaccess(self, ctx, member: discord.User):
        # Sirf aap (Owner) hi access de sakte hain
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("❌ Sirf Bot Owner hi access de sakta hai!")

        guild_id = ctx.guild.id if ctx.guild else None
        self.add_access(guild_id, member.id)
        
        target = "Server" if ctx.guild else "Global/DMs"
        await ctx.reply(f"✅ {member.mention} ko **{target}** mein access mil gaya hai.")

    @commands.hybrid_command(name="mpremove", description="Remove massping access")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("❌ Access denied.")

        guild_id = ctx.guild.id if ctx.guild else None
        self.remove_access(guild_id, member.id)
        await ctx.reply(f"❌ {member.mention} ka access hata diya gaya hai.")

    # =========================
    # 🚀 MASSPING COMMANDS
    # =========================

    @commands.hybrid_command(name="massping", description="Spam ping a user")
    @app_commands.describe(member="User to ping", amount="Number of pings")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied. Aapke paas permission nahi hai.")
        
        if amount <= 0:
            return await ctx.reply("Invalid amount")
        
        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ Already running here")

        self.active[channel_id] = True
        await ctx.reply(f"⚡ Starting mass ping x{amount}")
        
        for _ in range(amount):
            if not self.active.get(channel_id): break
            await ctx.send(member.mention)
            await asyncio.sleep(0.5)

        self.active[channel_id] = False
        await ctx.send("✅ Done")

    @commands.hybrid_command(name="mpstop", description="Stop mass ping")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Access denied")
        channel_id = ctx.channel.id
        self.active[channel_id] = False
        await ctx.reply("🛑 Stopped")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
