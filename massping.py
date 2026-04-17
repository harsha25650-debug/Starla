import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 📥 GET ACCESS LIST (Global Support)
    def get_access(self, guild_id):
        # Agar DM hai toh hum 'global' key use karenge
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

    # 🔐 PERMISSION CHECK (Fixed for DMs)
    async def check_permissions(self, interaction_or_ctx):
        user = interaction_or_ctx.user if isinstance(interaction_or_ctx, discord.Interaction) else interaction_or_ctx.author
        guild = interaction_or_ctx.guild

        # 1. Bot Owner ko hamesha access hai
        if await self.bot.is_owner(user):
            return True

        # 2. Server context mein check karein
        if guild:
            if user.id == guild.owner_id:
                return True
            if user.id in self.get_access(guild.id):
                return True
        
        # 3. Global/DM access check
        if user.id in self.get_access(None):
            return True

        return False

    # =========================
    # 🔑 ACCESS COMMANDS
    # =========================
    @commands.hybrid_command(name="mpaccess", description="Give massping access to a user")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpaccess(self, ctx, member: discord.User):
        # Sirf Bot Owner hi access de sakta hai
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("❌ Sirf bot owner hi access de sakta hai.")

        guild_id = ctx.guild.id if ctx.guild else None
        self.add_access(guild_id, member.id)
        
        loc = f"server **{ctx.guild.name}**" if ctx.guild else "DMs (Global)"
        await ctx.reply(f"✅ {member.mention} ko {loc} mein access de diya gaya hai.")

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
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("❌ Aapke paas is command ka access nahi hai.")
        
        # ... baaki code same rahega ...
        if amount <= 0: return await ctx.reply("Invalid amount")
        channel_id = ctx.channel.id
        if self.active.get(channel_id): return await ctx.reply("⚠️ Already running")
        
        self.active[channel_id] = True
        await ctx.reply(f"⚡ Starting mass ping x{amount}")
        for _ in range(amount):
            if not self.active.get(channel_id): break
            await ctx.send(member.mention)
            await asyncio.sleep(0.5)
        self.active[channel_id] = False
        await ctx.send("✅ Done")

    # (Ghostping aur mpstop mein bhi check_permissions updated wala use hoga)
