import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random

# --- 🎭 CUSTOM EMOJIS CONTEXT ---
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
E_CROSS = "<a:spider_cross:1494181311525687347>"

class Troll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}       # Channel ID -> Boolean
        self.backups = {}      # Guild ID -> Dictionary holding original assets data

    def is_active(self, channel_id):
        return self.active.get(channel_id, False)

    # ==================================
    # ☣️ HYBRID: MAXIMUM DESTRUCTIVE FAKE NUKE
    # ==================================
    @commands.hybrid_command(name="nuke", description="Owner Only: Launches full structural control takeover simulation protocol.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def nuke(self, ctx: commands.Context):
        await ctx.defer()

        if not ctx.guild:
            return await ctx.send(f"{E_CROSS} **Execution Aborted:** System isolation fault. Operational contexts are restricted to active guild structures.")

        if self.is_active(ctx.channel.id):
            return await ctx.send(f"{E_DOT} **Process Violation:** A core corruption routine is already executing within this sector.")

        self.active[ctx.channel.id] = True
        msg = await ctx.send(f"```ansi\n\u001b[1;31m⚠️ [CRITICAL ALERT]: EXPLOIT PAYLOAD DETECTED\u001b[0m\n```\n{E_DOT} **SYSTEM COMPROMISE IN PROGRESS:** Seizing administrative infrastructure channels...")

        steps = [
            f"{E_NOM} ```ansi\n\u001b[0;31m[+] Intercepting system tables... root permissions compromised.\u001b[0m\n```",
            f"📡 ```ansi\n\u001b[0;31m[+] Injecting malicious override daemons into Discord API nodes...\u001b[0m\n```",
            f"💣 ```ansi\n\u001b[0;31m[+] Purging fallback channels... Backup architecture encrypted.\u001b[0m\n```",
            f"{E_SWORD} ```ansi\n\u001b[1;31m[!] EXPLOIT ATTACHED: Master administrative token extracted.\u001b[0m\n```",
            f"⚡ ```ansi\n\u001b[0;35m[*] Executing mass liquidation parameters across all sectors...\u001b[0m\n```"
        ]

        for step in steps:
            if not self.is_active(ctx.channel.id):
                return await ctx.send(f"{E_CROSS} **System Warning:** Forced process interrupt. Sequence aborted by external administrator signature.")
            await asyncio.sleep(1.5)
            await msg.edit(content=step)

        # Cache original infrastructure data structures
        original_guild_name = ctx.guild.name
        original_channels = {}
        original_nicknames = {}
        original_icon = None
        original_banner = None
        
        if ctx.guild.icon:
            try: original_icon = await ctx.guild.icon.read()
            except Exception: pass
        if ctx.guild.banner:
            try: original_banner = await ctx.guild.banner.read()
            except Exception: pass

        bot_avatar_bytes = None
        if self.bot.user.avatar:
            try: bot_avatar_bytes = await self.bot.user.avatar.read()
            except Exception: pass

        # --- ☣️ STAGE 1: IDENTITY OVERRIDE ---
        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                await ctx.guild.edit(
                    name="Aura of Harsh",
                    icon=bot_avatar_bytes,
                    banner=bot_avatar_bytes, 
                    reason="System override routine execution."
                )
        except Exception:
            pass

        # --- ☣️ STAGE 2: CHANNEL LIQUIDATION ---
        if ctx.guild.me.guild_permissions.manage_channels:
            for channel in ctx.guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    original_channels[channel] = channel.name
                    try:
                        await channel.edit(name="☣️-nuked-by-starla", reason="Takeover routine active.")
                    except Exception:
                        pass

        # --- ☣️ STAGE 3: ACCOUNT DATA CORRUPTION (NICKNAMES) ---
        await ctx.send(f"{E_DOT} ```ansi\n\u001b[1;33m[~] CORRUPTING ACTIVE IDENTITIES... WIPING METADATA REGISTRIES.\u001b[0m\n```")
        for member in ctx.guild.members:
            if not member.bot and member.status != discord.Status.offline:
                if ctx.guild.me.top_role > member.top_role and member.id != ctx.guild.owner_id:
                    original_nicknames[member.id] = member.nick
                    try:
                        await member.edit(nick="OP Harsh ✌🏻", reason="System metadata liquidation.")
                    except Exception:
                        pass

        # Simulated encryption loops
        for i in range(0, 101, 25):
            if not self.is_active(ctx.channel.id):
                break
            await asyncio.sleep(1.5)
            await msg.edit(content=f"```ansi\n\u001b[1;31m🔥 ENCRYPTING GUILD DIRECTORIES: {i}% COMPLETION\u001b[0m\n```\n{E_NOM} *Wiping storage files... System connection destabilizing.*")

        # Save backups to cache
        self.backups[ctx.guild.id] = {
            "name": original_guild_name,
            "channels": original_channels,
            "nicknames": original_nicknames,
            "icon": original_icon,
            "banner": original_banner
        }

        self.active[ctx.channel.id] = False
        p = ctx.prefix if ctx.prefix else "!"
        await msg.edit(content=f"```ansi\n\u001b[1;41m💀 TOTAL INFRASTRUCTURE COLLAPSE: SUCCESSFUL WIPE 💀\u001b[0m\n```\n**SYSTEM STATUS:** Hostile Takeover Absolute. Guild modified to **Aura of Harsh**. User records overwriten to **OP Harsh ✌🏻**. {E_ROSE}\n\n⚠️ *Your database states are frozen. Recovery protocol locked. Access required via: `{p}rnrecovery`*")

    # ==================================
    # 🔄 HYBRID: MANUAL RECOVERY SYSTEM
    # ==================================
    @commands.hybrid_command(name="rnrecovery", description="Owner Only: Reverts all modified simulation configurations back to default profiles.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def rnrecovery(self, ctx: commands.Context):
        await ctx.defer()

        if not ctx.guild:
            return await ctx.send(f"{E_CROSS} Error: State restoration commands are restricted to target servers.")

        guild_backup = self.backups.get(ctx.guild.id)
        if not guild_backup:
            return await ctx.send(f"{E_DOT} **Restoration Refused:** No cached state backup located for this sector footprint.")

        status_msg = await ctx.send(f"{E_SWORD} **DECRYPTION SEQUENCE RUNNING:** Booting system safe state registries...")

        # 1. Restore nicknames
        for member_id, old_nick in guild_backup["nicknames"].items():
            member = ctx.guild.get_member(member_id)
            if member:
                try: await member.edit(nick=old_nick, reason="Emergency rollback.")
                except Exception: pass

        # 2. Restore channel names
        if ctx.guild.me.guild_permissions.manage_channels:
            for channel, old_name in guild_backup["channels"].items():
                try: await channel.edit(name=old_name, reason="Emergency rollback.")
                except Exception: pass

        # 3. Restore guild metadata
        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                await ctx.guild.edit(
                    name=guild_backup["name"],
                    icon=guild_backup["icon"],
                    banner=guild_backup["banner"],
                    reason="Emergency rollback."
                )
        except Exception:
            pass

        del self.backups[ctx.guild.id]
        await status_msg.edit(content=f"{E_GREENTICK} **System Normalized:** Core backup files injected. All structural metadata, channel registries, and user identifiers successfully decrypted and fully restored.")

    # ==================================
    # 📡 HYBRID: CONTROLLED SYSTEM FLOOD
    # ==================================
    @commands.hybrid_command(name="trollspam", description="Owner Only: Dispatches high-volume sequential terminal text flood loops.")
    @app_commands.describe(message="Target string payload to flood.", amount="Loop limits configuration (max 50)")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def trollspam(self, ctx: commands.Context, message: str, amount: int):
        await ctx.defer()

        if amount > 50:
            return await ctx.send(f"{E_DOT} **Boundary Block:** Pipeline execution thresholds limited to 50 iterations.")

        self.active[ctx.channel.id] = True

        if ctx.interaction is None and ctx.message:
            try: await ctx.message.delete()
            except Exception: pass

        for _ in range(amount):
            if not self.is_active(ctx.channel.id):
                break
            await ctx.send(message)
            await asyncio.sleep(0.4)

        self.active[ctx.channel.id] = False

    # ==================================
    # 🎭 HYBRID: SYSTEM LOG MATRIX FRAUD
    # ==================================
    @commands.hybrid_command(name="troll", description="Owner Only: Emits a simulated high-alert security warning targeting a user node.")
    @app_commands.describe(member="Target client member signature")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def troll(self, ctx: commands.Context, member: discord.User):
        await ctx.defer()
        
        messages = [
            f"{E_CROSS} {member.mention} ```ansi\n\u001b[1;31m[FATAL EXCEPTION]: Kernel level exploit attached to your system thread.\u001b[0m\n```",
            f"☠️ {member.mention} ```ansi\n\u001b[1;31m[DATA LEAK]: User tokens and unencrypted passwords pushed to open tracking relays.\u001b[0m\n```",
            f"📡 {member.mention} ```ansi\n\u001b[1;33m[WARNING]: Remote monitoring active. Tracing location signature assets...\u001b[0m\n```",
            f"🔓 {member.mention} ```ansi\n\u001b[1;31m[ACCESS REVOKED]: Cryptographic credentials dumped into dark web repositories.\u001b[0m\n```",
            f"🏃 {member.mention} ```ansi\n\u001b[1;35m[TERMINAL DETACHMENT]: Tracking connection loops finalized. You cannot run.\u001b[0m\n``` {E_BUTTERFLY}"
        ]
        await ctx.send(random.choice(messages))

    # ==================================
    # 🏷️ HYBRID: METADATA ALTERATION
    # ==================================
    @commands.hybrid_command(name="trollnick", description="Owner Only: Changes target nickname identity parameters inside a guild.")
    @app_commands.describe(member="Target guild member signature", name="New structural string metadata to apply")
    @app_commands.allowed_contexts(guilds=True)
    @app_commands.allowed_installs(guilds=True)
    @commands.is_owner()
    async def trollnick(self, ctx: commands.Context, member: discord.Member, name: str):
        await ctx.defer()

        try:
            await member.edit(nick=name, reason="Administrative metadata override.")
            await ctx.send(f"{E_VERIFIED} **Identity Compromised:** Successfully injected foreign string footprint onto user nickname metadata {member.mention}")
        except Exception:
            await ctx.send(f"{E_CROSS} **Execution Aborted:** Deficient system permissions to override user identity trees.")

    # ==================================
    # 🛑 HYBRID: GLOBAL FLOOD ABORT
    # ==================================
    @commands.hybrid_command(name="trollstop", description="Owner Only: Dispatches a forced termination interrupt to kill all local running cogs.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def trollstop(self, ctx: commands.Context):
        await ctx.defer()

        if self.is_active(ctx.channel.id):
            self.active[ctx.channel.id] = False
            await ctx.send(f"{E_CROSS} **Emergency Wipe Active:** All malicious system loop instances have been forcefully killed.")
        else:
            await ctx.send(f"{E_DOT} **Internal Check:** Diagnostic logs confirm no active exploit loop cogs are running inside this node.")

async def setup(bot):
    await bot.add_cog(Troll(bot))
            
