import discord
from discord.ext import commands

# --- 🎭 CUSTOM EMOJIS ---
E_VERIFIED = "<a:verified:1434044320830459935>"
E_DOT = "<a:spider_red_dot:1494179666133516411>"

class AFKView(discord.ui.View):
    def __init__(self, ctx, reason, cog):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.reason = reason
        self.cog = cog

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Yeh tumhare liye nahi hai!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Global", style=discord.ButtonStyle.gray)
    async def global_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_afk(interaction, "global")

    @discord.ui.button(label="Guild Only", style=discord.ButtonStyle.gray)
    async def guild_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_afk(interaction, str(interaction.guild.id))

    async def set_afk(self, interaction, afk_type):
        self.cog.afk_users[self.ctx.author.id] = {"reason": self.reason, "type": afk_type}
        await self.cog.set_nick(self.ctx.author, True)
        
        embed = discord.Embed(
            description=f"{E_VERIFIED} **You are now AFK**\n{self.ctx.author.mention}, Reason: **{self.reason}**",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        embed.set_thumbnail(url=self.ctx.author.display_avatar.url)
        await interaction.response.edit_message(content=None, embed=embed, view=None)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try: await self.message.edit(view=self)
        except: pass

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    async def set_nick(self, user, is_afk):
        try:
            if is_afk:
                if not user.display_name.startswith("[AFK]"):
                    await user.edit(nick=f"[AFK] {user.display_name}")
            else:
                if user.display_name.startswith("[AFK]"):
                    await user.edit(nick=user.display_name.replace("[AFK] ", ""))
        except: pass

    @commands.hybrid_command(name="afk", description="Set your AFK status")
    async def afk(self, ctx, *, reason: str = "I am AFK :)"):
        embed = discord.Embed(
            title="System Alert: Set Status Matrix",
            description=f"{E_DOT} Choose whether you want to attach this operational status across the entire system **Globally** or isolate it to **this Guild Server** node only.",
            color=discord.Color.from_rgb(47, 49, 54)
        )
        view = AFKView(ctx, reason, self)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        # AFK hatane wala logic
        if message.author.id in self.afk_users:
            data = self.afk_users[message.author.id]
            if data["type"] == "global" or data["type"] == str(message.guild.id):
                del self.afk_users[message.author.id]
                await self.set_nick(message.author, False)
                await message.channel.send(f"{E_VERIFIED} Welcome back **{message.author.name}**!", delete_after=5)

        # Ping alert logic
        for mention in message.mentions:
            if mention.id in self.afk_users:
                data = self.afk_users[mention.id]
                if data["type"] == "global" or data["type"] == str(message.guild.id):
                    embed = discord.Embed(
                        description=f"{E_DOT} **{mention.name}** is currently AFK: **{data['reason']}**",
                        color=discord.Color.from_rgb(47, 49, 54)
                    )
                    embed.set_thumbnail(url=mention.display_avatar.url)
                    await message.reply(embed=embed, mention_author=False)

async def setup(bot):
    await bot.add_cog(AFK(bot))
    
