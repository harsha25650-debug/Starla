import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}

    def get_global_access(self):
        return self.bot.db.get("mpaccess.global", [])

    def add_global_access(self, user_id):
        users = self.get_global_access()
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set("mpaccess.global", users)

    def remove_global_access(self, user_id):
        users = self.get_global_access()
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set("mpaccess.global", users)

    async def check_permissions(self, interaction_or_ctx):
        user = interaction_or_ctx.user if isinstance(interaction_or_ctx, discord.Interaction) else interaction_or_ctx.author
        if await self.bot.is_owner(user):
            return True
        return user.id in self.get_global_access()

    # =========================
    # 🔑 ACCESS MANAGEMENT
    # =========================
    
    @commands.hybrid_command(name="mpaccess", description="Grant global massping access to a user")
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
    # 🚀 RE-OPTIMIZED COMMANDS
    # =========================

    @commands.hybrid_command(name="massping", description="Repeatedly ping a user")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Access denied.")
        
        channel_id = ctx.channel.id
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ Process already running in this channel.")

        self.active[channel_id] = True
        await ctx.reply(f"⚡ Starting mass ping: **{amount}** times.")
        
        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break
                
            try:
                await ctx.send(member.mention)
                sent += 1
                
                # 🛡️ SMART JITTER DELAY (Crucial for DMs)
                if sent % 4 == 0:
                    # Har 4 messages ke baad lamba random break (3 to 5 seconds)
                    await asyncio.sleep(random.uniform(3.5, 5.2))
                else:
                    # Normal delay (thoda fast but safe)
                    await asyncio.sleep(random.uniform(0.9, 1.4))
                    
            except discord.HTTPException as e:
                if e.status == 429: # Rate Limited
                    retry_after = e.retry_after if hasattr(e, 'retry_after') else 10
                    await asyncio.sleep(retry_after + 2)
                else:
                    break
            except Exception:
                break

        self.active[channel_id] = False
        await ctx.send("<a:greentick:1494180392440303777> Mass ping completed.")

    @commands.hybrid_command(name="ghostping", description="Ping and delete instantly")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ghostping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply("<a:spider_cross:1494181311525687347> Access denied.")
        
        channel_id = ctx.channel.id
        self.active[channel_id] = True
        await ctx.reply(f"👻 Ghost pinging: **{amount}** times.", ephemeral=True)

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id): break
            try:
                msg = await ctx.send(member.mention)
                sent += 1
                await asyncio.sleep(0.4)
                await msg.delete()
                
                if sent % 3 == 0: 
                    await asyncio.sleep(random.uniform(2.5, 4.0))
                else:
                    await asyncio.sleep(0.8)
            except:
                pass
            
        self.active[channel_id] = False

    @commands.hybrid_command(name="mpfast", description="Send 80 pings in one message")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpfast(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx): return
        amount = min(amount, 80)
        pings = " ".join([member.mention for _ in range(amount)])
        await ctx.send(pings)

    @commands.hybrid_command(name="mpstop", description="Stop pings")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def mpstop(self, ctx):
        self.active[ctx.channel.id] = False
        await ctx.reply("<a:greentick:1494180392440303777> Stopped.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
