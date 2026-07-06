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
        self.active = {}         # Channel ID -> Boolean
        self.active_tasks = {}   # (channel_id, target_id) -> asyncio.Task

    # =========================
    # 🕒 TIME PARSER FUNCTION
    # =========================
    def parse_time(self, time_str: str) -> int:
        match = re.match(r"(\d+)\s*(s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)", time_str.lower())
        if not match:
            raise ValueError("Invalid time format configuration. Use specifications like: `1m`, `5min`, `1h`.")
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit in ["s", "sec", "second", "seconds"]:
            return value
        elif unit in ["m", "min", "minute", "minutes"]:
            return value * 60
        elif unit in ["h", "hour", "hours"]:
            return value * 3600
        else:
            raise ValueError("Invalid network operational unit detected.")

    # =========================
    # 🔑 ACCESS & FIREWALL REGISTRY
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

    def get_bypassed_users(self):
        if hasattr(self.bot, 'db') and self.bot.db:
            return self.bot.db.get("mpbypass.users", [])
        return []

    def add_bypass_user(self, user_id):
        users = self.get_bypassed_users()
        if user_id not in users:
            users.append(user_id)
            if hasattr(self.bot, 'db') and self.bot.db:
                self.bot.db.set("mpbypass.users", users)

    def remove_bypass_user(self, user_id):
        users = self.get_bypassed_users()
        if user_id in users:
            users.remove(user_id)
            if hasattr(self.bot, 'db') and self.bot.db:
                self.bot.db.set("mpbypass.users", users)

    async def check_permissions(self, ctx):
        user = ctx.author if hasattr(ctx, "author") else ctx.user
        if await self.bot.is_owner(user):
            return True
        return user.id in self.get_global_access()

    async def verify_target_safety(self, ctx, target: discord.User) -> bool:
        """Core Firewall: Ensures supreme developer security and checks whitelist exemptions."""
        if await self.bot.is_owner(target):
            crown = self.bot.emojis_dict.get("devil_crown", "👑")
            admin = self.bot.emojis_dict.get("air_admin", "🛡️")
            await ctx.reply(
                f"{ crown } **Security Override Fault:** Target parameter points to the root software architect (**Harsh**). "
                f"Defensive operational protocol triggered. Command execution permanently aborted. { admin }"
            )
            return False

        if target.id in self.get_bypassed_users():
            v = self.bot.emojis_dict.get("verified", "✅")
            await ctx.reply(f"{ v} **Firewall Exception:** Targeted user `{target.name}` is registered in the secure whitelist configuration matrix.")
            return False
            
        return True

    # =========================
    # 🔑 ACCESS AND FIREWALL CONTROL
    # =========================
    @commands.hybrid_command(name="mpaccess", description="Grants a user authorization to run massping operations.")
    @app_commands.describe(member="The user to authorize")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpaccess(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Root developer authorization failure.")
        self.add_global_access(member.id)
        await ctx.reply(f"{E_GREENTICK} Security privileges granted successfully to `{member.name}`.")

    @commands.hybrid_command(name="mpremove", description="Revokes massping authorization from a user.")
    @app_commands.describe(member="The user to deauthorize")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpremove(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Privilege modification failure.")
        self.remove_global_access(member.id)
        await ctx.reply(f"{E_DOT} Operational authorization revoked for `{member.name}`.")

    @commands.hybrid_command(name="mpbypass", description="Owner Only: Adds a targeted user payload into the firewall bypass matrix.")
    @app_commands.describe(member="The targeted user configuration to secure")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpbypass(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Restricted deployment sequence.")
        self.add_bypass_user(member.id)
        await ctx.reply(f"{E_GREENTICK} **Bypassed User Registered:** Target `{member.name}` successfully secured from operational targeting modules.")

    @commands.hybrid_command(name="mpunbypass", description="Owner Only: Removes a targeted user configuration from the firewall bypass matrix.")
    @app_commands.describe(member="The targeted user configuration to restore")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpunbypass(self, ctx, member: discord.User):
        if not await self.bot.is_owner(ctx.author):
            return await ctx.reply(f"{E_DOT} Access denied. Privileged argument context fault.")
        self.remove_bypass_user(member.id)
        await ctx.reply(f"{E_DOT} **Exemption Expired:** Target `{member.name}` removed from the secure whitelist database.")

    # =========================
    # 🚀 MASSPING (FAST SINGLE)
    # =========================
    @commands.hybrid_command(name="massping", description="Launches high-velocity sequential pings on a target.")
    @app_commands.describe(member="Target to bombard", amount="Total ping count (max 200)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def massping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized cluster action. Access denied.")
        if not await self.verify_target_safety(ctx, member):
            return

        amount = min(amount, 200)
        channel_id = ctx.channel.id
        
        if self.active.get(channel_id):
            return await ctx.reply("⚠️ A saturation sequence is currently active within this structural network channel.")

        self.active[channel_id] = True
        await ctx.reply(f"{E_DOT} Initializing targeted frequency saturation matrix...")

        sent = 0
        while sent < amount:
            if not self.active.get(channel_id):
                break

            try:
                await ctx.send(member.mention)
                sent += 1
                await asyncio.sleep(0.8)
            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except:
                break

        self.active[channel_id] = False
        await ctx.send(f"{E_GREENTICK} Target cluster saturation sequence executed completely.")

    # =========================
    # 👻 GHOSTPING (SILENT TROLL)
    # =========================
    @commands.hybrid_command(name="ghostping", description="Quietly spams notifications and deletes the traces.")
    @app_commands.describe(member="Target to ghostping", amount="Spam cycle count (max 100)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def ghostping(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            if ctx.message:
                try: await ctx.message.delete()
                except: pass
            return
        if not await self.verify_target_safety(ctx, member):
            return

        amount = min(amount, 100)
        channel_id = ctx.channel.id
        self.active[channel_id] = True

        if ctx.interaction:
            await ctx.interaction.response.send_message(f"👻 Asynchronous ghost tracking payload attached onto user `{member.name}`.", ephemeral=True)
        elif ctx.message:
            try: await ctx.message.delete()
            except: pass

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
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpfast(self, ctx, member: discord.User, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Access parameters denied.", ephemeral=True)
        if not await self.verify_target_safety(ctx, member):
            return

        amount = min(amount, 80)
        msg = " ".join([member.mention] * amount)
        await ctx.send(msg)

    # =========================
    # 🛑 STOP SINGLE MASSPING
    # =========================
    @commands.hybrid_command(name="mpstop", description="Kills active sequential massping/ghostping operations in the channel.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def mpstop(self, ctx):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized command caller signature.", ephemeral=True)
            
        self.active[ctx.channel.id] = False
        await ctx.reply(f"{E_GREENTICK} Sequential packet tracking sequences safely aborted within channel context.")

    # ==================================
    # 🎀 SUPERPINGS (LOOP TIME SCHEDULER)
    # ==================================
    async def ping_loop(self, ctx, member: discord.User, interval: int, amount: int):
        try:
            while True:
                for _ in range(amount):
                    await ctx.send(f"{member.mention} {E_SWORD} Target node localized. Operational sweep engaged.")
                    await asyncio.sleep(0.6)
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass

    @commands.hybrid_command(name="superpings", description="Locks onto a target and executes scheduled loop ping sequences.")
    @app_commands.describe(member="Designated target", time_input="Interval frequency (e.g., 5s, 1m, 1h)", amount="Ping payload per loop (max 200)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def superpings(self, ctx, member: discord.User, time_input: str, amount: int):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized network operational context.")
        if not await self.verify_target_safety(ctx, member):
            return

        try:
            seconds = self.parse_time(time_input)
        except ValueError as e:
            return await ctx.reply(f"{E_NOM} **Configuration Exception:** {str(e)}")

        if seconds < 10:
            return await ctx.reply(f"{E_NOM} **System Architecture Constraint:** Minimum loop frequency duration is set at 10 seconds.")
        if amount > 200:
            return await ctx.reply(f"{E_NOM} **System Architecture Constraint:** Maximum loop block limits capped at 200.")

        channel_id = ctx.channel.id
        task_key = (channel_id, member.id)

        if task_key in self.active_tasks:
            self.active_tasks[task_key].cancel()

        task = asyncio.create_task(self.ping_loop(ctx, member, seconds, amount))
        self.active_tasks[task_key] = task

        embed = discord.Embed(
            title=f"{E_VERIFIED} Automation Sequence Synchronized - Loop Active",
            description=f"Persistent diagnostic loop scheduling sequence successfully operational. {E_ROSE}",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.add_field(name="🎯 Structural Target", value=member.mention, inline=True)
        embed.add_field(name="🕒 Loop Frequency", value=f"`{time_input}` ({seconds}s)", inline=True)
        embed.add_field(name="⚡ Burst Payload Volume", value=f"`{amount}` transmissions", inline=True)
        
        p = ctx.prefix if ctx.prefix else "!"
        embed.set_footer(text=f"Abort operational sequence: {p}stopsuperpings {member.name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    # ==================================
    # 🛑 STOP SUPERPINGS (TARGET SPECIFIC)
    # ==================================
    @commands.hybrid_command(name="stopsuperpings", description="Aborts active loop pinging operations.")
    @app_commands.describe(member="The specific target to release (leave empty to clear the channel)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def stopsuperpings(self, ctx, member: discord.User = None):
        if not await self.check_permissions(ctx):
            return await ctx.reply(f"{E_DOT} Unauthorized. Operations access denied.")

        channel_id = ctx.channel.id

        if member:
            task_key = (channel_id, member.id)
            if task_key in self.active_tasks:
                self.active_tasks[task_key].cancel()
                del self.active_tasks[task_key]

                embed = discord.Embed(
                    title=f"🛑 Target Node Released",
                    description=f"Automated loops terminated for user target {member.mention}. Tracking off. {E_BUTTERFLY}",
                    color=discord.Color.from_rgb(47, 49, 54)
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} No operational tracking parameters detected for {member.mention} inside this specific node sector.")

        else:
            keys_to_remove = [key for key in self.active_tasks.keys() if key[0] == channel_id]
            if keys_to_remove:
                for key in keys_to_remove:
                    self.active_tasks[key].cancel()
                    del self.active_tasks[key]

                embed = discord.Embed(
                    title=f"🛑 Forced Channel Cleared",
                    description=f"All background cluster scheduling loop nodes in this channel have been explicitly terminated. {E_BUTTERFLY}",
                    color=discord.Color.from_rgb(47, 49, 54)
                )
                await ctx.send(embed=embed)
            else:
                await ctx.reply(f"{E_NOM} No background active tracking tasks found active in this channel zone.")

async def setup(bot):
    await bot.add_cog(MassPing(bot))
    
