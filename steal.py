import discord
from discord.ext import commands
import aiohttp
import asyncio

class Steal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Custom Emojis Config
        self.loading_icon = "<a:spider_red_dot:1494179666133516411>"
        self.success_icon = "<a:greentick:1494180392440303777>"
        self.cross_icon = "<a:spider_cross:1494181311525687347>"

    # 🔐 PERMISSION CHECK
    def can_manage_expressions():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            
            if ctx.author.guild_permissions.manage_expressions:
                return True
            
            # Custom Error if permission check fails
            cross = "<a:spider_cross:1494181311525687347>"
            embed = discord.Embed(
                description=f"{cross} **Access denied | owner/premiumUser only command**", 
                color=0x000000
            )
            await ctx.send(embed=embed)
            return False
        return commands.check(predicate)

    @commands.command(name="steal")
    @can_manage_expressions()
    @commands.bot_has_permissions(manage_expressions=True)
    async def steal(self, ctx):
        # 1. Check for reply
        if not ctx.message.reference:
            embed = discord.Embed(
                description=f"{self.cross_icon} **Please reply to a message with an emoji/sticker**", 
                color=0x000000
            )
            return await ctx.send(embed=embed)

        replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        
        emoji_data = None
        sticker_data = None

        # 2. Extract Data
        if "<" in replied_msg.content and ":" in replied_msg.content:
            import re
            match = re.search(r"<(a?):(\w+):(\d+)>", replied_msg.content)
            if match:
                ext = "gif" if match.group(1) else "png"
                emoji_data = {
                    "name": match.group(2), 
                    "url": f"https://cdn.discordapp.com/emojis/{match.group(3)}.{ext}"
                }

        if replied_msg.stickers:
            sticker = replied_msg.stickers[0]
            sticker_data = {"name": sticker.name, "url": sticker.url}

        if not emoji_data and not sticker_data:
            embed = discord.Embed(description=f"{self.cross_icon} **No stealable asset found**", color=0x000000)
            return await ctx.send(embed=embed)

        # 3. Initial Embed
        embed = discord.Embed(title="Asset Stealer", description="Choose an action below", color=0x000000)
        if emoji_data: embed.set_thumbnail(url=emoji_data['url'])
        elif sticker_data: embed.set_thumbnail(url=sticker_data['url'])

        view = StealView(emoji_data, sticker_data, ctx.author, self.loading_icon, self.success_icon, self.cross_icon)
        await ctx.send(embed=embed, view=view)

# 🔘 UPDATED VIEW
class StealView(discord.ui.View):
    def __init__(self, emoji_data, sticker_data, user, loading, success, cross):
        super().__init__(timeout=60)
        self.emoji_data = emoji_data
        self.sticker_data = sticker_data
        self.user = user
        self.loading = loading
        self.success = success
        self.cross = cross

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message(f"{self.cross} This menu is not for you.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Steal Emoji", style=discord.ButtonStyle.secondary)
    async def steal_emoji(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(description=f"{self.loading} **Stealing...**", color=0x000000), 
            view=None
        )
        await asyncio.sleep(2)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.emoji_data['url']) as resp:
                    img = await resp.read()
            
            new_emoji = await interaction.guild.create_custom_emoji(
                name=self.emoji_data['name'], image=img, reason=f"Stolen by {self.user}"
            )
            await interaction.edit_original_response(
                embed=discord.Embed(description=f"{self.success} **Added Successfully!** {new_emoji}", color=0x000000)
            )
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(description=f"{self.cross} **Error:** `{e}`", color=0x000000))

    @discord.ui.button(label="Steal Sticker", style=discord.ButtonStyle.secondary)
    async def steal_sticker(self, interaction: discord.Interaction, button):
        await interaction.response.edit_message(
            embed=discord.Embed(description=f"{self.loading} **Stealing...**", color=0x000000), 
            view=None
        )
        await asyncio.sleep(2)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.sticker_data['url']) as resp:
                    img = await resp.read()
            
            with open("stolen.png", "wb") as f: f.write(img)
            await interaction.guild.create_sticker(
                name=self.sticker_data['name'], description="Stolen", emoji="😎", file=discord.File("stolen.png")
            )
            await interaction.edit_original_response(
                embed=discord.Embed(description=f"{self.success} **Sticker Added Successfully!**", color=0x000000)
            )
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(description=f"{self.cross} **Error:** `{e}`", color=0x000000))

async def setup(bot):
    await bot.add_cog(Steal(bot))
  
