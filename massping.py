import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re

# --- 🎭 CUSTOM EMOJIS (Aapke provided IDs ke sath) ---
E_NOM = "<a:bs_nom:1443239762197745790>"
E_BUTTERFLY = "<a:lyf_butterfly_black:1515672700415246346>"
E_DOT = "<a:spider_red_dot:1494179666133516411>"
E_SUPREME = "<:trick_supreme:1433737084363083869>"
E_GUAVA = "<a:Guava:1514950622586077354>"
E_HEART = "<a:HEART:1438571571915522208>"
E_HEART3 = "<a:Heart3:1434556967556350004>"
E_MOD = "<:Moderator:1433718499791994892>"
E_SWORD = "<:bd_sword:1495476833720729836>"
E_VERIFIED = "<a:verified:1434044320830459935>"
E_ROSE = "<:bd_rose:1510988383332204735>"
E_GREENTICK = "<a:greentick:1494180392440303777>"

class MassPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}         # Single-massping track karne ke liye (Channel ID -> Boolean)
        self.active_tasks = {}   # Multi-loop track karne ke liye ((channel_id, target_id) -> asyncio.Task)

    # =========================
    # 🕒 TIME PARSER FUNCTION
    # =========================
    def parse_time(self, time_str: str) -> int:
        match = re.match(r"(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)", time_str.lower())
        if not match:
            raise ValueError("Format galat hai bestie! Sahi format: `1m`, `5min`, `1h`, `1hour` etc.")
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ["s", "sec", "second", "seconds"]:
            return value
        elif unit in ["m", "min", "minute", "minutes"]:
            return value * 60
        elif unit in ["h", "hour", "hours"]:
            return value * 3600
        else:
            raise ValueError("Invalid unit!")

    # =========================
    # 🔑 ACCESS SYSTEM
    # =========================
    def get_global_access(self):
        if hasattr(self.bot, 'db') and self.bot.db:
            return self.bot.db.get("mpaccess.global", [])
        return []

    def add_global_access(self, user_id):
        users = self.get_global_access()
        if user_id not in users:
            users.append(user_id)
            if hasattr(self.bot, 'db') and self.bot.db:
                self.bot.db.set("mpaccess.global", users)

    def remove_global_access(self, user_id):
        users = self.get_global_access()
        if user_id in users:
            users.remove(user_id)
            if hasattr(self.bot, 'db') and self.bot.db:
                self.bot.db.set("mpaccess.global", users)

    async def check_permissions(self, ctx):
        user = ctx.author if hasattr(ctx, "author") else ctx.user
        if await self.bot.is_owner(user):
            return True
        return user.id in self.get_global_access()

    # =========================
    # 🔑 ACCESS COMMANDS
    # =========================
    @commands.hybrid_command(name="mpaccess", description="Give a user permissions to use massping.")
    @app_commands.describe(member="The user who will get permissions")
    async def mpaccess(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Only owner allowed.")
        self.add_global_access(member.id)
        await ctx.reply(f"{E_GREENTICK} {member.name} given access.")

    @commands.hybrid_command(name="mpremove", description="Remove access from a user.")
    @app_commands.describe(member="The user whose access you want to remove")
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied.")
        self.remove_global_access(member.id)
        await ctx.reply(f"{E_DOT} Removed access from {member.name}.")

    # =========================
    # 🚀 MASSPING (FAST SINGLE)
    # =========================
    @commands.hybrid_command(name="massping", description="Fast sequential pings in a channel.")
    @app_commands.describe(member="Who to ping", amount="How many times (max 200)")
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Access denied.")

        amount = min(amount, 200)
        channel_id = ctx.channel.id
        
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ Already running here.")

        self.active[channel_id] = True
        await ctx.reply(f"{E_DOT} Starting fast ping...")

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                await ctx.send(member.mention)
                sent += 1
                await asyncio.sleep(0.8) # ⚡ fastest safe delay
            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

        self.active[channel_id] = False
        await ctx.send(f"{E_GREENTICK} Mass ping completed.")

    # =========================
    # 👻 GHOSTPING (SILENT)
    # =========================
    @commands.hybrid_command(name="ghostping", description="Silently ping a user by deleting pings immediately.")
    @app_commands.describe(member="Target to ghostping", amount="How many times (max 100)")
    async def ghostping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            if ctx.message:
                try:
                    await ctx.message.delete()
                except:
                    pass
            return

        amount = min(amount, 100)
        channel_id = ctx.channel.id
        self.active[channel_id] = True

        # Slash interactions must get an ephemeral acknowledgement response, prefix messages are deleted.
        if ctx.interaction:
            await ctx.interaction.response.send_message(f"👻 Ghostping started for {member.name}!", ephemeral=True)
        elif ctx.message:
            try:
                await ctx.message.delete()
            except:
                pass

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                msg = await ctx.send(member.mention)
                sent += 1

                await asyncio.sleep(0.4)
                await msg.delete()
                await asyncio.sleep(0.9)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

        self.active[channel_id] = False

    # =========================
    # ⚡ FAST BURST
    # =========================
    @commands.hybrid_command(name="mpfast", description="Send a massive single message containing multiple mentions.")
    @app_commands.describe(member="The target user", amount="Mentions count (max 80)")
    async def mpfast(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Access denied.", ephemeral=True)

        amount = min(amount, 80)
        msg = " ".join([member.mention] * amount)
        await ctx.send(msg)

    # =========================
    # 🛑 STOP SINGLE MASSPING
    # =========================
    @commands.hybrid_command(name="mpstop", description="Stops sequential masspings/ghostpings in the channel.")
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Access denied.", ephemeral=True)
            
        self.active[ctx.channel.id] = False
        await ctx.reply(f"{E_GREENTICK} Stopped sequential pings.")

    # ==================================
    # 🎀 SUPERPINGS (LOOP TIME SCHEDULER)
    # ==================================
    async def ping_loop(self, ctx, member: discord.User, interval: int, amount: int):
        try:
            while True:
                for _ in range(amount):
                    await ctx.send(f"{member.mention} {E_HEART3} wake up cutie!")
                    await asyncio.sleep(0.6) # Anti-rate-limit delay
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    @commands.hybrid_command(name="superpings", description="Repeatedly pings a target member after specific intervals.")
    @app_commands.describe(
        member="Target to superping",
        time_input="How often to ping (e.g., 5s, 1m, 1h, 10h)",
        amount="Number of pings per cycle (max 50)"
    )
    async def superpings(self, ctx, member: discord.User, time_input: str, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Access denied.")

        try:
            seconds = self.parse_time(time_input)
        except ValueError as e:
            return await ctx.reply(f"{E_NOM} **Error:** {str(e)}")

        # Security checks to keep Bot Account safe
        if seconds < 10:
            return await ctx.reply(f"{E_NOM} **Security Check:** Interval minimum 10 seconds hona chahiye bestie!")
        if amount > 50:
            return await ctx.reply(f"{E_NOM} **Security Check:** Ek cycle mein max 50 pings hi ho sakte hain!")

        channel_id = ctx.channel.id
        task_key = (channel_id, member.id)

        # Purana active loop cancel karega agar exist karega toh
        if task_key in self.active_tasks:
            self.active_tasks[task_key].cancel()

        # Naya loop define karega
        task = asyncio.create_task(self.ping_loop(ctx, member, seconds, amount))
        self.active_tasks[task_key] = task

        embed = discord.Embed(
            title=f"{E_VERIFIED} Starla SuperPing Launched!",
            description=f"Maine loop pinging start kar di hai, bestie! {E_ROSE}",
            color=0xffb6c1
        )
        embed.add_field(name="🎯 Target", value=member.mention, inline=True)
        embed.add_field(name="🕒 Interval", value=f"`{time_input}` ({seconds}s)", inline=True)
        embed.add_field(name="⚡ Pings Per Cycle", value=f"`{amount}`", inline=True)
        
        # Determine prefix for instructions dynamic context
        p = ctx.prefix if ctx.prefix else "!"
        embed.set_footer(text=f"Stop karne ke liye: {p}stopsuperpings {member.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    # ==================================
    # 🛑 STOP SUPERPINGS (TARGET SPECIFIC)
    # ==================================
    @commands.hybrid_command(name="stopsuperpings", description="Stop active loop superpings.")
    @app_commands.describe(member="The user whose superping loop you want to stop (leave empty for all)")
    async def stopsuperpings(self, ctx, member: discord.User = None):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Access denied.")

        channel_id = ctx.channel.id

        # Case 1: Specific Target specified
        if member:
            task_key = (channel_id, member.id)
            if task_key in self.active_tasks:
                self.active_tasks[task_key].cancel()
                del self.active_tasks[task_key]

                embed = discord.Embed(
                    title=f"🛑 Target Stopped!",
                    description=f"Maine {member.mention} ke liye chal rahe active loops ko rok diya hai! {E_BUTTERFLY}",
                    color=0xffb6c1
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} Mujhe is channel mein {member.mention} ke liye koi active loop nahi mila, cutie!")

        # Case 2: Target not specified, stop all loops in this channel
        else:
            keys_to_remove = [key for key in self.active_tasks.keys() if key[0] == channel_id]
            if keys_to_remove:
                for key in keys_to_remove:
                    self.active_tasks[key].cancel()
                    del self.active_tasks[key]

                embed = discord.Embed(
                    title=f"🛑 All Targets Stopped!",
                    description=f"Maine is channel ke **saare active loops** ko turant rok diya hai! {E_BUTTERFLY}",
                    color=0xffb6c1
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} Is channel mein koi bhi active superpings loop nahi chal raha hai, bestie!")


async def setup(bot):
    await bot.add_cog(MassPing(bot))
