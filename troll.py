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

        prompt_msg = await ctx.reply(f"Lord… are we really about to bring this server down?", mention_author=True)

        def check(m):
            if m.author.id != ctx.author.id or m.channel.id != ctx.channel.id:
                return False
            text = m.content.lower()
            has_yes = any(word in text for word in ["yes", "yep", "yeah", "sure", "ok", "do it", "ya", "sweetheart"])
            has_no = any(word in text for word in ["no", "nope", "nah", "cancel", "stop"])
            return has_yes or has_no

        try:
            msg_reply = await self.bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            try:
                await prompt_msg.edit(content=prompt_msg.content + "\n\n*Timed out. Action cancelled.*")
            except Exception:
                pass
            return

        reply_text = msg_reply.content.lower()
        if any(word in reply_text for word in ["no", "nope", "nah", "cancel", "stop"]) and not any(word in reply_text for word in ["yes", "yep", "yeah", "sure", "ok", "sweetheart"]):
            await msg_reply.reply("the server owner got lucky this time", mention_author=False)
            return

        self.active[ctx.channel.id] = True
        
        # Replies directly to the user's message without mentioning/tagging them
        await msg_reply.reply("As your wish lord", mention_author=True)

        original_guild_name = ctx.guild.name
        original_verification_level = ctx.guild.verification_level
        original_channels = {}
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
                    name="🔪 power of Harsh ki starla",
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
                    try:
                        await channel.edit(name="💔-nuked-by-harsh", reason="Takeover routine active.")
                    except Exception: pass

        for member in ctx.guild.members:
            if not member.bot and member.status != discord.Status.offline:
                if ctx.guild.me.top_role > member.top_role and member.id != ctx.guild.owner_id:
                    original_nicknames[member.id] = member.nick
                    try: 
                        await member.edit(nick="Harsh's slave 🍪", reason="System metadata update.")
                    except Exception: pass

        if ctx.guild.me.guild_permissions.connect and ctx.guild.voice_channels:
            target_vc = random.choice(ctx.guild.voice_channels)
            try: voice_client = await target_vc.connect(timeout=5, reconnect=False)
            except Exception: pass

        if ctx.guild.me.guild_permissions.manage_webhooks and isinstance(ctx.channel, discord.TextChannel):
            try: fake_webhook = await ctx.channel.create_webhook(name="CORE_CRASH_DAEMON", avatar=bot_avatar_bytes)
            except Exception: pass

        self.backups[ctx.guild.id] = {
            "name": original_guild_name,
            "verification_level": original_verification_level,
            "channels": original_channels,
            "nicknames": original_nicknames,
            "icon": original_icon,
            "banner": original_banner,
            "webhook": fake_webhook,
            "voice": voice_client
        }

        self.active[ctx.channel.id] = False

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

        if backup_data:
            status_msg = await ctx.send(f"{E_SWORD} **FILE INJECTION ACTIVE:** Reading `.json` schema data & repairing infrastructure...")

            try:
                if ctx.guild.me.guild_permissions.manage_guild and "server_name" in backup_data:
                    await ctx.guild.edit(name=backup_data["server_name"], reason="JSON Schema Restoration Routine.")
            except Exception: pass

            if ctx.guild.me.guild_permissions.manage_channels and "categories" in backup_data:
                nuked_channels = [c for c in ctx.guild.channels if "nuked-by-harsh" in c.name.lower()]
                
                backup_channel_names = []
                for cat in backup_data["categories"]:
                    for chan in cat.get("channels", []):
                        backup_channel_names.append(chan.get("name"))

                for idx, channel in enumerate(nuked_channels):
                    if idx < len(backup_channel_names):
                        try:
                            await channel.edit(name=backup_channel_names[idx], reason="JSON Backup Sync")
                        except Exception: pass

            await status_msg.edit(content=f"{E_GREENTICK} **JSON Template Restoration Complete:** Server structure synced and verified!")
            return

        guild_backup = self.backups.get(ctx.guild.id)
        if not guild_backup:
            return await ctx.send(f"{E_DOT} **Restoration Refused:** No cached state backup located for this server. Please upload/attach a backup `.json` file!")

        status_msg = await ctx.send(f"{E_SWORD} **DECRYPTION SEQUENCE RUNNING:** Restoring system state from RAM cache...")

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
        await status_msg.edit(content=f"{E_GREENTICK} **System Normalized:** Core backup files injected. All structural metadata fully restored.")

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
    @commands.hybrid_command(name="trollstop", description="Owner Only: Dispatches a forced termination interrupt across active loops.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @commands.is_owner()
    async def trollstop(self, ctx: commands.Context):
        self.active.clear()
        await ctx.send(f"{E_GREENTICK} **System Reset:** All active threads and loop operations have been successfully terminated.")

async def setup(bot):
    await bot.add_cog(Troll(bot))
