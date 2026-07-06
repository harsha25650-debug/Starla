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
        self.active = {} # Channel ID -> Boolean

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
            return await ctx.send(f"{E_CROSS} **Execution Aborted:** Destructive takeover simulation protocols are strictly restricted to guild server infrastructures.")

        if self.is_active(ctx.channel.id):
            return await ctx.send(f"{E_DOT} **Operation Conflict:** An active script runtime simulation is already executing within this node context.")

        self.active[ctx.channel.id] = True
        msg = await ctx.send(f"{E_DOT} **CRITICAL SYSTEM ALERT:** Initializing Full Server Takeover and Destruction Payload...")

        steps = [
            f"{E_NOM} Extracting localized server data mapping directories...",
            f"📡 Syncing bot assets into central server memory units...",
            f"💣 Caching original channels, banners, and server configuration states...",
            f"{E_SWORD} Bypassing guild authorization nodes... Complete.",
            f"⚡ Deploying automated network payload layout..."
        ]

        for step in steps:
            if not self.is_active(ctx.channel.id):
                return await ctx.send(f"{E_CROSS} **Operational Interrupt:** Takeover script aborted by administrative intervention.")
            await asyncio.sleep(2)
            await msg.edit(content=step)

        # Cache original infrastructure data structures
        original_guild_name = ctx.guild.name
        original_channels = {}
        original_icon = None
        original_banner = None
        
        # Save original icon and banner assets
        if ctx.guild.icon:
            try: original_icon = await ctx.guild.icon.read()
            except Exception: pass
        if ctx.guild.banner:
            try: original_banner = await ctx.guild.banner.read()
            except Exception: pass

        # Download bot avatar bytes for corporate branding injection
        bot_avatar_bytes = None
        if self.bot.user.avatar:
            try: bot_avatar_bytes = await self.bot.user.avatar.read()
            except Exception: pass

        # --- ☣️ STAGE 1: COMPREHENSIVE INFRASTRUCTURE ALTERATION ---
        await msg.edit(content=f"{E_NOM} **[STAGE 1]** Injecting brand identity properties into server root config...")
        
        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                # Forces server identity change using bot branding properties and customized name
                await ctx.guild.edit(
                    name="Aura of Harsh",
                    icon=bot_avatar_bytes,
                    banner=bot_avatar_bytes, 
                    reason="Destructive simulation execution."
                )
        except Exception:
            pass

        # Global channel override looping protocol
        if ctx.guild.me.guild_permissions.manage_channels:
            for channel in ctx.guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    original_channels[channel] = channel.name
                    try:
                        await channel.edit(name="☣️-nuked-by-starla", reason="Takeover payload simulation engaged.")
                    except Exception:
                        pass

        # Simulated progress loops
        for i in range(0, 101, 25):
            if not self.is_active(ctx.channel.id):
                break
            await asyncio.sleep(1.5)
            await msg.edit(content=f"{E_NOM} **[ALERT]** Overriding guild matrix data components... `{i}%` overwritten.")

        await asyncio.sleep(2)
        await msg.edit(content=f"☠️ **CRITICAL TAKEOVER DISASTER:** Full server infrastructure successfully seized and transformed via Starla Core Takeover Framework. {E_ROSE}")

        # The shock pause window before dynamic auto-restoration resets configurations
        await asyncio.sleep(6)
        await ctx.send(f"{E_SWORD} **System Restoration:** Network simulation timeout reached. Initializing dynamic backup configuration rollback parameters...")

        # --- 🔄 STAGE 2: BACKUP DATA RESTORATION PROTOCOL ---
        # 1. Revert server text and voice channel strings safely
        if ctx.guild.me.guild_permissions.manage_channels:
            for channel, old_name in original_channels.items():
                try:
                    await channel.edit(name=old_name, reason="Takeover simulation cleanup.")
                except Exception:
                    pass

        # 2. Revert server name, icon and banner configurations
        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                await ctx.guild.edit(
                    name=original_guild_name,
                    icon=original_icon,
                    banner=original_banner,
                    reason="Takeover simulation configurations completely restored."
                )
        except Exception:
            pass

        self.active[ctx.channel.id] = False
        await ctx.send(f"{E_GREENTICK} **Recovery Complete:** All modified channel arrays, server name, logos, and assets successfully synced back to default status profiles.")

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
            return await ctx.send(f"{E_DOT} **Operational Boundary Exceeded:** Maximum configuration threshold limited to 50 messages.")

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
            f"{E_CROSS} {member.mention} **System Exception:** Kernel architecture access compromise detected.",
            f"☠️ {member.mention} **Database Core Alert:** User credential tokens exposed globally.",
            f"📡 {member.mention} **Network Diagnostic Alert:** Foreign endpoint interception tracing active.",
            f"🔓 {member.mention} **Access Control Fault:** Local authentication keys leaked to public trackers.",
            f"🚶 {member.mention} **Execution Trace Warning:** Disconnecting terminal session... too late. {E_BUTTERFLY}"
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
            await ctx.send(f"{E_VERIFIED} **Identity Parameter Overridden:** Successfully changed nickname layout configuration for {member.mention}")
        except Exception:
            await ctx.send(f"{E_CROSS} **Execution Aborted:** Missing authorization architecture credentials to alter metadata constraints.")

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
            await ctx.send(f"{E_CROSS} **Execution Exception Aborted:** All simulation runtimes have been forcefully neutralized.")
        else:
            await ctx.send(f"{E_DOT} **Audit Diagnostic:** No operational active simulation engines detected running within this zone.")

async def setup(bot):
    await bot.add_cog(Troll(bot))
