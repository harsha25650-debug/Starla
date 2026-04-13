import discord
from discord.ext import commands
import asyncio

# Buttons ke liye View class
class AFKView(discord.ui.View):
    def __init__(self, author, reason, cog):
        super().__init__(timeout=30)
        self.author = author
        self.reason = reason
        self.cog = cog

    @discord.ui.button(label="Global", style=discord.ButtonStyle.gray)
    async def global_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        
        self.cog.afk_users[self.author.id] = {"reason": self.reason, "pings": [], "type": "global"}
        await self.set_afk_nickname(interaction.user)
        await interaction.response.edit_message(content=f"✅ Your AFK is now set **Globally**: {self.reason}", view=None, embed=None)

    @discord.ui.button(label="Guild", style=discord.ButtonStyle.gray)
    async def guild_afk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            return await interaction.response.send_message("This is not for you!", ephemeral=True)
        
        self.cog.afk_users[self.author.id] = {"reason": self.reason, "pings": [], "type": str(interaction.guild.id)}
        await self.set_afk_nickname(interaction.user)
        await interaction.response.edit_message(content=f"✅ Your AFK is now set for **this Guild**: {self.reason}", view=None, embed=None)

    async self.set_afk_nickname(self, user):
        try:
            if not user.display_name.startswith("[AFK]"):
                await user.edit(nick=f"[AFK] {user.display_name}")
        except:
            pass # Permission error handle karne ke liye

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {} # {user_id: {"reason": str, "pings": list, "type": str}}

    @commands.command()
    async def afk(self, ctx, *, reason="I'm AFK"):
        embed = discord.Embed(
            title="Set AFK",
            description="Do you want to set AFK globally or just for this guild?",
            color=discord.Color.dark_grey()
        )
        view = AFKView(ctx.author, reason, self)
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # 1. AFK Hatane wala logic (Message bhejne par)
        if message.author.id in self.afk_users:
            data = self.afk_users[message.author.id]
            
            # Sirf tabhi hatega agar Global ho ya wahi server ho jahan set kiya tha
            if data["type"] == "global" or data["type"] == str(message.guild.id):
                pings = data["pings"]
                del self.afk_users[message.author.id]

                # Nickname wapas normal karna
                try:
                    if message.author.display_name.startswith("[AFK]"):
                        new_nick = message.author.display_name.replace("[AFK] ", "")
                        await message.author.edit(nick=new_nick)
                except: pass

                await message.channel.send(f"Welcome back {message.author.mention}! Your AFK has been removed.", delete_after=5)

                # DM mein ping list bhejna
                if pings:
                    ping_msg = "**While you were away, these users pinged you:**\n" + "\n".join(pings)
                    try:
                        await message.author.send(ping_msg)
                    except: pass

        # 2. AFK user ko ping karne par notification
        for mention in message.mentions:
            if mention.id in self.afk_users:
                data = self.afk_users[mention.id]
                # Check agar guild matching hai ya global hai
                if data["type"] == "global" or data["type"] == str(message.guild.id):
                    # Pings list mein user aur message link save karna
                    data["pings"].append(f"👤 {message.author.name} in **{message.guild.name}**")
                    await message.reply(f"⚠️ **{mention.name}** is currently AFK: {data['reason']}")

async def setup(bot):
    await bot.add_cog(AFK(bot))
            
