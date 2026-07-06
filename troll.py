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
    # ☣️ HYBRID: DESTRUCTIVE FAKE NUKE PROTOCOL
    # ==================================
    @commands.hybrid_command(name="nuke", description="Owner Only: Initializes the localized destructive framework payload simulation.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def nuke(self, ctx: commands.Context):
        await ctx.defer()

        if self.is_active(ctx.channel.id):
            return await ctx.send(f"{E_DOT} **Operation Conflict:** An active script runtime simulation is already executing within this node context.")

        self.active[ctx.channel.id] = True
        msg = await ctx.send(f"{E_DOT} **CRITICAL SYSTEM ALERT:** Initializing Localized Server Nuke Protocol Structure...")

        steps = [
            f"{E_NOM} Injecting high-velocity kernel payload scripts...",
            f"📡 Connecting to discord gateway routing clusters...",
            f"🛡️ Corrupting guild verification nodes and safety checks...",
            f"{E_SWORD} Overriding permission maps for text channels...",
            f"⚡ Deploying automated structural cleanup sequence..."
        ]

        for step in steps:
            if not self.is_active(ctx.channel.id):
                return await ctx.send(f"{E_CROSS} **Operational Interrupt:** Nuke deployment aborted by administrator command.")
            await asyncio.sleep(2)
            await msg.edit(content=step)

        # Cache original channel names before simulation alteration triggers
        original_names = {}
        if ctx.guild and ctx.guild.me.guild_permissions.manage_channels:
            channels_to_alter = ctx.guild.text_channels[:5] # Limits to top 5 channels to avoid api throttling flags
            for channel in channels_to_alter:
                original_names[channel] = channel.name
                try:
                    await channel.edit(name="☣️-nuked-by-starla", reason="Simulation sequence triggered.")
                except Exception:
                    pass

        # Simulated progress loops
        for i in range(0, 101, 20):
            if not self.is_active(ctx.channel.id):
                # Critical emergency rollback sequence
                for channel, old_name in original_names.items():
                    try: await channel.edit(name=old_name)
                    except Exception: pass
                return await ctx.send(f"{E_CROSS} **Operational Emergency Rollback:** Structure sequence terminated.")
            await asyncio.sleep(1.5)
            await msg.edit(content=f"{E_NOM} **[ALERT]** Purging infrastructure channel records... `{i}%` completely wiped.")

        await asyncio.sleep(2)
        await msg.edit(content=f"☠️ **CRITICAL DISASTER:** Server Infrastructure Wiped Successfully via Starla Core Execution Engine. {E_ROSE}")

        # Grace period for terminal simulation shock before auto-restoration
        await asyncio.sleep(4)
        await ctx.send(f"{E_SWORD} **System Diagnostics:** Initiating backup channel mapping auto-restoration sequence...")

        # Flawlessly restore original state settings
        for channel, old_name in original_names.items():
            try:
                await channel.edit(name=old_name, reason="Simulation restoration complete.")
            except Exception:
                pass

        self.active[ctx.channel.id] = False
        await ctx.send(f"{E_GREENTICK} **Core Recovery Successful:** All modified guild nodes successfully restored to default architecture parameters. *Simulation Complete.*")

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
            
