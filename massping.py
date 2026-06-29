import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re

# --- 🎭 CUSTOM EMOJIS ---
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
        self.active = {}         # Tracks fast sequential masspings (Channel ID -> Boolean)
        self.active_tasks = {}   # Tracks multi-target loops ((channel_id, target_id) -> asyncio.Task)

    # =========================
    # 🕒 TIME PARSER FUNCTION
    # =========================
    def parse_time(self, time_str: str) -> int:
        match = re.match(r"(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)", time_str.lower())
        if not match:
            raise ValueError("Invalid time format. Use something like `1m`, `5min`, `1h`, `1hour`.")
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ["s", "sec", "second", "seconds"]:
            return value
        elif unit in ["m", "min", "minute", "minutes"]:
            return value * 60
        elif unit in ["h", "hour", "hours"]:
            return value * 3600
        else:
            raise ValueError("Invalid unit detected.")

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
    @commands.hybrid_command(name="mpaccess", description="Grants a user authorization to run massping operations.")
    @app_commands.describe(member="The user to authorize")
    async def mpaccess(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Authorized personnel only.")
        self.add_global_access(member.id)
        await ctx.reply(f"{E_GREENTICK} Authorization granted to {member.name}.")

    @commands.hybrid_command(name="mpremove", description="Revokes massping authorization from a user.")
    @app_commands.describe(member="The user to deauthorize")
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Authorization failed.")
        self.remove_global_access(member.id)
        await ctx.reply(f"{E_DOT} Authorization revoked for {member.name}.")

    # =========================
    # 🚀 MASSPING (FAST SINGLE)
    # =========================
    @commands.hybrid_command(name="massping", description="Launches high-velocity sequential pings on a target.")
    @app_commands.describe(member="Target to bombard", amount="Total ping count (max 200)")
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access denied.")

        amount = min(amount, 200)
        channel_id = ctx.channel.id
        
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ An active operation is already running in this channel.")

        self.active[channel_id] = True
        await ctx.reply(f"{E_DOT} Initiating target saturation...")

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                await ctx.send(member.mention)
                sent += 1
                await asyncio.sleep(0.8)  # Optimal delay to prevent API bottleneck
            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

        self.active[channel_id] = False
        await ctx.send(f"{E_GREENTICK} Target saturation completed successfully.")

    # =========================
    # 👻 GHOSTPING (SILENT TROLL)
    # =========================
    @commands.hybrid_command(name="ghostping", description="Quietly spams notifications and deletes the traces.")
    @app_commands.describe(member="Target to ghostping", amount="Spam cycle count (max 100)")
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

        if ctx.interaction:
            await ctx.interaction.response.send_message(f"👻 Ghost protocol initiated on {member.name}.", ephemeral=True)
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
    @commands.hybrid_command(name="mpfast", description="Dispatches a massive block of mentions in a single transmission.")
    @app_commands.describe(member="The target user", amount="Mentions payload (max 80)")
    async def mpfast(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access denied.", ephemeral=True)

        amount = min(amount, 80)
        msg = " ".join([member.mention] * amount)
        await ctx.send(msg)

    # =========================
    # 🛑 STOP SINGLE MASSPING
    # =========================
    @commands.hybrid_command(name="mpstop", description="Kills active sequential massping/ghostping operations in the channel.")
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access denied.", ephemeral=True)
            
        self.active[ctx.channel.id] = False
        await ctx.reply(f"{E_GREENTICK} Sequential ping sequence aborted.")

    # ==================================
    # 🎀 SUPERPINGS (LOOP TIME SCHEDULER)
    # ==================================
    async def ping_loop(self, ctx, member: discord.User, interval: int, amount: int):
        try:
            while True:
                for _ in range(amount):
                    await ctx.send(f"{member.mention} {E_SWORD} Wake up. Cry about it.")
                    await asyncio.sleep(0.6)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    @commands.hybrid_command(name="superpings", description="Locks onto a target and executes scheduled loop ping sequences.")
    @app_commands.describe(
        member="Designated target",
        time_input="Interval frequency (e.g., 5s, 1m, 1h, 10h)",
        amount="Ping payload per loop (max 50)"
    )
    async def superpings(self, ctx, member: discord.User, time_input: str, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access denied.")

        try:
            seconds = self.parse_time(time_input)
        except ValueError as e:
            return await ctx.reply(f"{E_NOM} **Configuration Error:** {str(e)}")

        # Security checks to avoid platform limits
        if seconds < 10:
            return await ctx.reply(f"{E_NOM} **Security Protocol:** Minimum loop interval is capped at 10 seconds.")
        if amount > 50:
            return await ctx.reply(f"{E_NOM} **Security Protocol:** Maximum loop payload is capped at 50.")

        channel_id = ctx.channel.id
        task_key = (channel_id, member.id)

        # Cancel any active operations for this specific target in the channel
        if task_key in self.active_tasks:
            self.active_tasks[task_key].cancel()

        # Initialize the looping schedule
        task = asyncio.create_task(self.ping_loop(ctx, member, seconds, amount))
        self.active_tasks[task_key] = task

        embed = discord.Embed(
            title=f"{E_VERIFIED} Target Locked - Loop Initialized",
            description=f"Continuous bombardment schedule active for the designated target. {E_ROSE}",
            color=0xffb6c1
        )
        embed.add_field(name="🎯 Designated Target", value=member.mention, inline=True)
        embed.add_field(name="🕒 Interval Frequency", value=f"`{time_input}` ({seconds}s)", inline=True)
        embed.add_field(name="⚡ Loop Payload", value=f"`{amount}` pings", inline=True)
        
        p = ctx.prefix if ctx.prefix else "!"
        embed.set_footer(text=f"Abort command: {p}stopsuperpings {member.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    # ==================================
    # 🛑 STOP SUPERPINGS (TARGET SPECIFIC)
    # ==================================
    @commands.hybrid_command(name="stopsuperpings", description="Aborts active loop pinging operations.")
    @app_commands.describe(member="The specific target to release (leave empty to clear the channel)")
    async def stopsuperpings(self, ctx, member: discord.User = None):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access denied.")

        channel_id = ctx.channel.id

        # Case 1: Specific Target Terminated
        if member:
            task_key = (channel_id, member.id)
            if task_key in self.active_tasks:
                self.active_tasks[task_key].cancel()
                del self.active_tasks[task_key]

                embed = discord.Embed(
                    title=f"🛑 Operation Terminated",
                    description=f"Ping sequence aborted for {member.mention}. Target released. {E_BUTTERFLY}",
                    color=0xffb6c1
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} No active loop sequence found for {member.mention} in this sector.")

        # Case 2: Broad Termination
        else:
            keys_to_remove = [key for key in self.active_tasks.keys() if key[0] == channel_id]
            if keys_to_remove:
                for key in keys_to_remove:
                    self.active_tasks[key].cancel()
                    del self.active_tasks[key]

                embed = discord.Embed(
                    title=f"🛑 Total Cessation",
                    description=f"All active loop sequences in this channel have been forcefully terminated. {E_BUTTERFLY}",
                    color=0xffb6c1
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} No active loop sequences detected in this channel.")


async def setup(bot):
    await bot.add_cog(MassPing(bot))
