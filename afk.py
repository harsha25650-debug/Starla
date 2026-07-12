import discord
from discord.ext import commands
from discord import app_commands

# --- 🎭 Fallback Emojis Mapped Internally ---
E_DOT = "<a:spider_red_dot:1494179666133516411>"
E_VERIFIED = "<a:verified:1434044320830459935>"
E_SWORD = "<:bd_sword:1495476833720729836>"

# ==================================
# 🔘 AFK SELECTION VIEW CONTROL
# ==================================
class AFKView(discord.ui.View):
    def __init__(self, author, reason, cog):
        super().__init__(timeout=30)
        self.author = author
        self.reason = reason
        self.cog = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("❌ **Access Denied:** This structural prompt is isolated to the command executor.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Global", style=discord.ButtonStyle.gray)
    async def global_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        v = getattr(self.cog.bot, 'emojis_dict', {}).get("verified", E_VERIFIED)
        
        afk_data = self.cog.get_afk_data()
        afk_data[str(self.author.id)] = {"reason": self.reason, "pings": [], "type": "global"}
        self.cog.save_afk_data(afk_data)
        
        await self.cog.set_afk_nickname(interaction.user)
        
        embed = discord.Embed(
            description=f"{v} **You are now AFK**\n{self.author.mention}, Reason: **{self.reason}**",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_thumbnail(url=self.author.display_avatar.url)
        embed.set_footer(text="Global Network AFK Matrix Triggered")
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)

    @discord.ui.button(label="Guild Only", style=discord.ButtonStyle.gray)
    async def guild_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild:
            return await interaction.response.send_message("❌ Guild contexts are required for localized deployments.", ephemeral=True)
            
        v = getattr(self.cog.bot, 'emojis_dict', {}).get("verified", E_VERIFIED)
        
        afk_data = self.cog.get_afk_data()
        afk_data[str(self.author.id)] = {"reason": self.reason, "pings": [], "type": str(interaction.guild.id)}
        self.cog.save_afk_data(afk_data)
        
        await self.cog.set_afk_nickname(interaction.user)
        
        embed = discord.Embed(
            description=f"{v} **You are now AFK**\n{self.author.mention}, Reason: **{self.reason}**",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_thumbnail(url=self.author.display_avatar.url)
        embed.set_footer(text=f"Localized Guild Scope Active: {interaction.guild.name}")
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)

# ==================================
# 🤖 AFK STATUS MANAGEMENT EXTENSION
# ==================================
class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_afk_data(self):
        if hasattr(self.bot, 'db') and self.bot.db:
            return self.bot.db.get("afk.registry", {})
        return {}

    def save_afk_data(self, data):
        if hasattr(self.bot, 'db') and self.bot.db:
            self.bot.db.set("afk.registry", data)

    async def set_afk_nickname(self, user):
        if isinstance(user, discord.Member):
            try:
                if not user.display_name.startswith("[AFK]"):
                    await user.edit(nick=f"[AFK] {user.display_name}", reason="AFK profile activation mapping.")
            except Exception:
                pass

    # --- 💤 HYBRID AFK ACTIVATION ROUTINE ---
    @commands.hybrid_command(name="afk", description="Suspends your active status parameters within the system network.")
    @app_commands.describe(reason="The status payload reason for the suspension.")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def afk(self, ctx: commands.Context, *, reason: str = "I am AFK :)"):
        dot = getattr(self.bot, 'emojis_dict', {}).get("spider_red_dot", E_DOT)
        
        embed = discord.Embed(
            title="System Alert: Set Status Matrix",
            description=f"{dot} Choose whether you want to attach this operational status across the entire system **Globally** or isolate it to **this Guild Server** node only.",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        
        view = AFKView(ctx.author, reason, self)
        await ctx.send(embed=embed, view=view)

    # --- 💬 ASYNCHRONOUS EVENT TRAFFIC MONITOR ---
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        afk_data = self.get_afk_data()
        user_id_str = str(message.author.id)

        # 1. REMOVE AFK CONDITION TRIGGER
        if user_id_str in afk_data:
            data = afk_data[user_id_str]
            if data["type"] == "global" or data["type"] == str(message.guild.id):
                v = getattr(self.bot, 'emojis_dict', {}).get("verified", E_VERIFIED)
                sword = getattr(self.bot, 'emojis_dict', {}).get("bd_sword", E_SWORD)
                pings = data.get("pings", [])
                
                # De-register from database record logs
                del afk_data[user_id_str]
                self.save_premium_users = self.save_afk_data(afk_data)
                
                # Restore nickname metadata layout configuration profiles
                try:
                    if message.author.display_name.startswith("[AFK]"):
                        new_nick = message.author.display_name.replace("[AFK] ", "")
                        await message.author.edit(nick=new_nick, reason="AFK removal execution.")
                except Exception:
                    pass

                embed = discord.Embed(
                    description=f"{v} **Welcome Back:** {message.author.mention}, your status parameters have been safely synchronized back to active operations.",
                    color=discord.Color.from_rgb(47, 49, 54)
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await message.channel.send(embed=embed, delete_after=6)

                # Process offloaded direct message notifications safely
                if pings:
                    ping_msg = f"{sword} **Diagnostic Logs: While your application node was offline, you were tagged in these networks:**\n" + "\n".join(pings)
                    try: await message.author.send(ping_msg)
                    except Exception: pass

        # 2. INCOMING MENTION MONITORING ALERTS
        for mention in message.mentions:
            mention_id_str = str(mention.id)
            if mention_id_str in afk_data:
                data = afk_data[mention_id_str]
                if data["type"] == "global" or data["type"] == str(message.guild.id):
                    dot = getattr(self.bot, 'emojis_dict', {}).get("spider_red_dot", E_DOT)
                    
                    # Store tracking payload inside internal cache
                    data["pings"].append(f"• 👤 `{message.author.name}` tagged you inside **{message.guild.name}** -> <#{message.channel.id}>")
                    self.save_afk_data(afk_data)
                    
                    embed = discord.Embed(
                        description=f"{dot} **Status Alert:** {mention.mention} is currently running an offline diagnostic state.\n\n💬 **Reason Payload:** `{data['reason']}`",
                        color=discord.Color.from_rgb(47, 49, 54)
                    )
                    embed.set_thumbnail(url=mention.display_avatar.url)
                    await message.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(AFK(bot))
        
