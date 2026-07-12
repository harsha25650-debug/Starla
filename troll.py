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

# ==================================
# 🔘 CONFIRMATION UI VIEW CLASS
# ==================================
class NukeConfirmationView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=10.0) # 10 Seconds Timeout limit
        self.owner_id = owner_id
        self.confirmed = False
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("❌ **Access Denied:** Only the system owner can interact with this prompt.", ephemeral=True)
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
        await interaction.response.send_message(f"{E_CROSS} **Execution Aborted:** Nuke sequence cancelled by user.", ephemeral=True)
        if self.message:
            try: await self.message.delete()
            except Exception: pass

    async def on_timeout(self):
        # Auto cleanup if 10 seconds pass without interaction
        if self.message:
            try: await self.message.delete()
            except Exception: pass


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
        if not ctx.guild:
            return await ctx.send(f"{E_CROSS} **Execution Aborted:** System isolation fault. Operational contexts are restricted to active guild structures.")

        if self.is_active(ctx.channel.id):
            return await ctx.send(f"{E_DOT} **Process Violation:** A core corruption routine is already executing within this sector.")

        # --- 🔘 STAGE 0: CONFIRMATION PROMPT EMBED ---
        embed = discord.Embed(
            title="Nuke Server?",
            description=f"This will **delete and recreate** all sectors in **{ctx.guild.name}**.\nAll messages will be permanently removed.",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_footer(text="Awaiting verification • Timeout: 10 seconds")

        view = NukeConfirmationView(owner_id=ctx.author.id)
        prompt_msg = await ctx.send(embed=embed, view=view)
        view.message = prompt_msg

        # Wait for interaction or 10s timeout expiration
        await view.wait()

        if not view.confirmed:
            return

        # Purge prompt message after confirmation
        try: await prompt_msg.delete()
        except Exception: pass

        self.active[ctx.channel.id] = True
        msg = await ctx.send(f"
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2
http://googleusercontent.com/immersive_entry_chip/3
http://googleusercontent.com/immersive_entry_chip/4
http://googleusercontent.com/immersive_entry_chip/5
http://googleusercontent.com/immersive_entry_chip/6
http://googleusercontent.com/immersive_entry_chip/7
http://googleusercontent.com/immersive_entry_chip/8
        
