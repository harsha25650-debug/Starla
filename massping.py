import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    # 📥 GET GLOBAL ACCESS LIST
    def get_global_access(self):
        return self.bot.db.get("mpaccess.global", [])

    # 💾 ADD GLOBAL ACCESS
    def add_global_access(self, user_id):
        users = self.get_global_access()
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set("mpaccess.global", users)

    # ❌ REMOVE GLOBAL ACCESS
    def remove_global_access(self, user_id):
        users = self.get_global_access()
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set("mpaccess.global", users)

    # 🔐 PERMISSION CHECK
    async def check_permissions(self, interaction_or_ctx):
        user = interaction_or_ctx.user if isinstance(interaction_or_ctx, discord.Interaction) else interaction_or_ctx.author
        if await self.bot.is_owner(user):
            return True
        return user.id in self.get_global_access()

    # =========================
    # 🔑 ACCESS MANAGEMENT
    # =========================
    
    @commands.hybrid_command(name="mpaccess", description="Grant global massping access to a user")
    @app_commands.describe(member="User to authorize globally")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpaccess(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Only the bot owner can manage global access.")

        self.add_global_access(member.id)
        await ctx.reply(f"<a:greentick:1494180392440303777> **{member.name}** has been granted **Global Access**.")

    @commands.hybrid_command(name="mpremove", description="Revoke global massping access")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Access denied.")

        self.remove_global_access(member.id)
        await ctx.reply(f"<a:spider_cross:1494181311525687347> Global access revoked for **{member.name}**.")

    # =========================
    # 🚀 MASSPING COMMANDS
    # =========================

    @commands.hybrid_command(name="massping", description="Repeatedly ping a user")
    @app_commands.describe(member="User to ping", amount="Number of pings")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Access denied. Global permission required.")
        
        if amount <= 0:
            return await ctx.reply("<a:spider_cross:1494181311525687347> Please provide a valid amount.")
        
        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ A process is already running in this channel.")

        self.active[channel_id] = True
        await ctx.reply(f"⚡ Starting mass ping: **{amount}** times.")
        
        for _ in range(amount):
            if not self.active.get(channel_id):
                break
            await ctx.send(member.mention)
            await asyncio.sleep(0.6)

        self.active[channel_id] = False
        await ctx.send("<a:greentick:1494180392440303777> Mass ping completed.")

    @commands.hybrid_command(name="mpstop", description="Stop the current mass ping process")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Access denied.")
            
        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            self.active[channel_id] = False
            await ctx.reply("<a:greentick:1494180392440303777> Process stopped successfully.")
        else:
            await ctx.reply("<a:spider_cross:1494181311525687347> No process is currently running.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
