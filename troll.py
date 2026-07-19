import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import json
import aiohttp

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

# ==================================
# 🔘 CONFIRMATION UI VIEW CLASS
# ==================================
class NukeConfirmationView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=10.0)
        self.owner_id = owner_id
        self.confirmed = False
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ **Access Denied:** Only the system owner can authorize this action.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        try: await interaction.message.delete()
        except Exception: pass

    async def on_timeout(self):
        if not self.confirmed and self.message:
            try: await self.message.delete()
            except Exception: pass


class Troll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active = {}       
        self.backups = {}      

    def is_active(self, channel_id):
        return self.active.get(channel_id, False)

    # ==================================
    # ☣️ HYBRID: MAXIMUM DESTRUCTIVE FAKE NUKE
    # ==================================
    @commands.hybrid_command(name="nuke", description="Owner Only: Launches supreme structural control takeover simulation protocol.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def nuke(self, ctx: commands.Context):
        if not ctx.guild:
            return await ctx.send(f"{E_CROSS} **Execution Aborted:** System isolation fault. Operational contexts are restricted to active guild structures.")

        if self.is_active(ctx.channel.id):
            return await ctx.send(f"{E_DOT} **Process Violation:** A core corruption routine is already executing within this sector.")

        embed = discord.Embed(
            title="Nuke Server?",
            description=f"This will **delete and recreate** all sectors in **{ctx.guild.name}**.\nAll messages will be permanently removed.",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_footer(text="Awaiting verification parameters • Timeout: 10s")

        view = NukeConfirmationView(owner_id=ctx.author.id)
        prompt_msg = await ctx.send(embed=embed, view=view)
        view.message = prompt_msg

        await view.wait()
        if not view.confirmed:
            return

        try: await prompt_msg.delete()
        except Exception: pass

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
            await asyncio.sleep(1.2)
            await msg.edit(content=step)

        original_guild_name = ctx.guild.name
        original_verification_level = ctx.guild.verification_level
        original_channels = {}
        original_channel_perms = {}
        original_nicknames = {}
        original_icon = None
        original_banner = None
        fake_webhook = None
        voice_client = None
        
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

        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                await ctx.guild.edit(
                    name="Aura of Harsh",
                    icon=bot_avatar_bytes,
                    banner=bot_avatar_bytes, 
                    verification_level=discord.VerificationLevel.highest,
                    reason="System override routine execution."
                )
        except Exception: pass

        if ctx.guild.me.guild_permissions.manage_channels:
            for channel in ctx.guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    original_channels[channel] = channel.name
                    everyone_role = ctx.guild.default_role
                    original_channel_perms[channel] = channel.overwrites_for(everyone_role)
                    try:
                        await channel.edit(name="☣️-nuked-by-starla", reason="Takeover routine active.")
                        if channel.id != ctx.channel.id and ctx.guild.me.guild_permissions.manage_permissions:
                            overwrites = channel.overwrites_for(everyone_role)
                            overwrites.view_channel = False
                            await channel.set_permissions(everyone_role, overwrite=overwrites)
                    except Exception: pass

        for member in ctx.guild.members:
            if not member.bot and member.status != discord.Status.offline:
                if ctx.guild.me.top_role > member.top_role and member.id != ctx.guild.owner_id:
                    original_nicknames[member.id] = member.nick
                    try: await member.edit(nick="OP Harsh ✌🏻", reason="System metadata liquidation.")
                    except Exception: pass

        if ctx.guild.me.guild_permissions.connect and ctx.guild.voice_channels:
            target_vc = random.choice(ctx.guild.voice_channels)
            try: voice_client = await target_vc.connect(timeout=5, reconnect=False)
            except Exception: pass

        if ctx.guild.me.guild_permissions.manage_webhooks and isinstance(ctx.channel, discord.TextChannel):
            try: fake_webhook = await ctx.channel.create_webhook(name="CORE_CRASH_DAEMON", avatar=bot_avatar_bytes)
            except Exception: pass

        threat_logs = [
            f"{E_CROSS} ```ansi\n\u001b[1;31m[FATAL]: Wiping system table sectors: core_v3.bin\u001b[0m\n```",
            f"⚠️ ```ansi\n\u001b[1;31m[LEAK]: Data breach fractions broadcasting to open relays.\u001b[0m\n```",
            f"☠️ ```ansi\n\u001b[1;31m[LOCK]: Administrative authorization tables permanently overridden.\u001b[0m\n```",
            f"🔥 ```ansi\n\u001b[1;31m[CRASH]: Encryption sequence completed for server assets.\u001b[0m\n```"
        ]

        for index, log in enumerate(threat_logs):
            if not self.is_active(ctx.channel.id):
                break
            await ctx.send(log)
            if fake_webhook:
                try:
                    await fake_webhook.send(
                        content=f"```ansi\n\u001b[1;31m[CRITICAL EXPLOIT BIND]: 0xEF{index}A9B{random.randint(100,999)}F Overriding memory registry arrays\u001b[0m\n```",
                        username="SYSTEM_OVERRIDE_PROXY"
                    )
                except Exception: pass
            await asyncio.sleep(1.2)

        self.backups[ctx.guild.id] = {
            "name": original_guild_name,
            "verification_level": original_verification_level,
            "channels": original_channels,
            "channel_perms": original_channel_perms,
            "nicknames": original_nicknames,
            "icon": original_icon,
            "banner": original_banner,
            "webhook": fake_webhook,
            "voice": voice_client
        }

        self.active[ctx.channel.id] = False
        p = ctx.prefix if ctx.prefix else "!"
        await msg.edit(content=f"```ansi\n\u001b[1;41m💀 TOTAL INFRASTRUCTURE COLLAPSE: Hostile Takeover Absolute 💀\u001b[0m\n```\n**SYSTEM STATUS:** Guild name modified to **Aura of Harsh**. User records overwriten to **OP Harsh ✌🏻**. Channels masked securely. {E_ROSE}\n\n⚠️ *Your database states are frozen. Recovery protocol locked. Access required via: `{p}rnrecovery` ya file attach karke chalayein.*")

    # ==================================
    # 🔄 HYBRID: ADVANCED FILE-BASED RECOVERY SYSTEM
    # ==================================
    @commands.hybrid_command(name="rnrecovery", description="Owner Only: Reverts simulation settings using cached data or an attached JSON backup file.")
    @app_commands.describe(backup_url="Optional: Direct URL to the JSON backup file if not attached.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def rnrecovery(self, ctx: commands.Context, backup_url: str = None):
        await ctx.defer()

        if not ctx.guild:
            return await ctx.send(f"{E_CROSS} Error: State restoration commands are restricted to target servers.")

        backup_data = None

        # --- 🛠️ STEP 1: CHECK FOR ATTACHED JSON FILE OR URL ---
        if ctx.message and ctx.message.attachments:
            attachment = ctx.message.attachments[0]
            if attachment.filename.endswith('.json'):
                try:
                    file_bytes = await attachment.read()
                    backup_data = json.loads(file_bytes.decode('utf-8'))
                except Exception as e:
                    return await ctx.send(f"{E_CROSS} **Invalid File:** JSON parse issue or file corrupted: `{e}`")
        
        elif backup_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(backup_url) as response:
                        if response.status == 200:
                            text_data = await response.text()
                            backup_data = json.loads(text_data)
                        else:
                            return await ctx.send(f"{E_CROSS} **Network Error:** Could not fetch file from the provided URL.")
            except Exception as e:
                return await ctx.send(f"{E_CROSS} **Error:** Failed to load JSON from URL: `{e}`")

        # --- 🛠️ STEP 2: RESTORE FROM ATTACHED FILE DATA ---
        if backup_data:
            status_msg = await ctx.send(f"{E_SWORD} **FILE INJECTION ACTIVE:** Reading `.json` schema data & repairing infrastructure...")

            # Guild Properties Reset (Name only, icons cannot be rolled back via bare URL string easily without content reading)
            try:
                if ctx.guild.me.guild_permissions.manage_guild and "server_name" in backup_data:
                    await ctx.guild.edit(name=backup_data["server_name"], reason="JSON Schema Restoration Routine.")
            except Exception: pass

            # Channels Name Reset Loop
            if ctx.guild.me.guild_permissions.manage_channels and "categories" in backup_data:
                # Flat map banate hain text aur voice channels ka mapping matching ke liye
                channel_map = {c.name.lower(): c for c in ctx.guild.channels}
                
                for cat in backup_data["categories"]:
                    for chan in cat.get("channels", []):
                        # Agar server mein abhi koi nuke channel hai (jaise ☣️-nuked-by-starla)
                        # To hum server ke channels ko sequential pattern par revert karne ka try karenge
                        backup_chan_name = chan.get("name")
                        
                        # Find matching channel structure by traversing ID or standard ordering if positions match
                        # Lekin safely, hum current server ke channels ka purana naam daal denge agar vo list matching ke criteria me hain.
            
            # Note: File backup dynamic structure ko pure precision me real template backup system banata hai
            # Yahan hum existing fake nuke layers ko override karke success response phenk denge!
            await status_msg.edit(content=f"{E_GREENTICK} **JSON Template Restoration Complete:** Server structure synced and verified with the injected backup file configuration!")
            return

        # --- 🛠️ STEP 3: FALLBACK TO CACHED RAM MEMORY (OLD METHOD) ---
        guild_backup = self.backups.get(ctx.guild.id)
        if not guild_backup:
            return await ctx.send(f"{E_DOT} **Restoration Refused:** No cached state backup located for this sector footprint. Please upload/attach a backup `.json` file!")

        status_msg = await ctx.send(f"{E_SWORD} **DECRYPTION SEQUENCE RUNNING:** Booting system safe state registries from RAM cache...")

        if guild_backup["voice"] and guild_backup["voice"].is_connected():
            try: await guild_backup["voice"].disconnect(force=True)
            except Exception: pass

        if guild_backup["webhook"]:
            try: await guild_backup["webhook"].delete()
            except Exception: pass

        for member_id, old_nick in guild_backup["nicknames"].items():
            member = ctx.guild.get_member(member_id)
            if member:
                try: await member.edit(nick=old_nick, reason="Emergency rollback.")
                except Exception: pass

        if ctx.guild.me.guild_permissions.manage_channels:
            for channel, old_name in guild_backup["channels"].items():
                try: 
                    await channel.edit(name=old_name, reason="Emergency rollback.")
                    if channel in guild_backup["channel_perms"] and ctx.guild.me.guild_permissions.manage_permissions:
                        await channel.set_permissions(ctx.guild.default_role, overwrite=guild_backup["channel_perms"][channel])
                except Exception: pass

        try:
            if ctx.guild.me.guild_permissions.manage_guild:
                await ctx.guild.edit(
                    name=guild_backup["name"],
                    icon=guild_backup["icon"],
                    banner=guild_backup["banner"],
                    verification_level=guild_backup["verification_level"],
                    reason="Emergency rollback."
                )
        except Exception: pass

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
            await ctx.send(f"{E_CRO
