import discord
from discord.ext import commands
from discord import app_commands
import datetime

class SnipeView(discord.ui.View):
    def __init__(self, snipes, user):
        super().__init__(timeout=120)
        self.snipes = snipes[::-1]
        self.index = 0
        self.user = user
        
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"

    def format_time(self, time_str):
        past_time = datetime.datetime.fromisoformat(time_str)
        now = discord.utils.utcnow()
        diff = now - past_time
        seconds = int(diff.total_seconds())

        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            return f"{seconds//60}m ago"
        elif seconds < 86400:
            return f"{seconds//3600}h ago"
        else:
            return f"{seconds//86400}d ago"

    def get_embed(self):
        data = self.snipes[self.index]

        embed = discord.Embed(
            title=f"{self.ico_info} Snipe Menu | Message {self.index+1}/{len(self.snipes)}",
            color=0x2b2d31
        )

        embed.description = (
            f"{self.dot_black} **Author:** {data['author']}\n"
            f"{self.arrow} **Deleted:** `{self.format_time(data['time'])}` \n\n"
            f"**Content:**\n{data['content']}"
        )

        if data.get("attachment"):
            embed.set_image(url=data["attachment"])

        embed.set_footer(
            text=f"Requested by {self.user.name}",
            icon_url=self.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        embed.set_thumbnail(url=data["avatar"])
        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("<:starlacross:1525756266604007464> This menu belongs to someone else.", ephemeral=True)
            return False
        return True

    # ⏪ First Page
    @discord.ui.button(label="«", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = 0
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    # ◀️ Previous Page
    @discord.ui.button(label="‹", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    # ❌ Cancel Menu Button using starla_opt_no
    @discord.ui.button(emoji="<:starla_opt_no:1525756996886986885>", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

    # ▶️ Next Page
    @discord.ui.button(label="›", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.snipes) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    # ⏩ Last Page
    @discord.ui.button(label="»", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.index = len(self.snipes) - 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cross = "<:starlacross:1525756266604007464>"
        self.no = "<:starla_opt_no:1525756996886986885>"

    # 🔐 FIXED PERMISSION CHECK
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            return ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_messages
        return commands.check(predicate)

    # 🧠 SAVE SNIPE
    def save_snipe(self, channel_id, data):
        path = f"snipes.{channel_id}"
        snipes = self.bot.db.get(path, [])
        snipes.append(data)

        if len(snipes) > 20:
            snipes.pop(0)

        self.bot.db.set(path, snipes)

    # 📥 GET SNIPE
    def get_snipes(self, channel_id):
        return self.bot.db.get(f"snipes.{channel_id}", [])

    # 📡 LISTENER
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild:
            return

        attachment = None
        if message.attachments:
            attachment = message.attachments[0].url

        data = {
            "content": message.content if message.content else "*No text content (likely an embed/attachment)*",
            "author": message.author.mention,
            "avatar": message.author.display_avatar.url,
            "time": discord.utils.utcnow().isoformat(),
            "attachment": attachment
        }

        self.save_snipe(message.channel.id, data)

    # 🔍 COMMAND
    @commands.hybrid_command(name="snipe", description="View recently deleted messages inside this channel")
    @has_perm_or_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def snipe(self, ctx):
        snipes = self.get_snipes(ctx.channel.id)

        if not snipes:
            return await ctx.send(f"{self.cross} No recently deleted messages found in this channel.")

        view = SnipeView(snipes, ctx.author)
        await ctx.send(embed=view.get_embed(), view=view)

    # ❗ ERROR HANDLER
    @snipe.error
    async def snipe_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You need `Manage Messages` permission to view snipes.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Snipe(bot))
    
