import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class SnipeView(discord.ui.View):
    def __init__(self, snipes, user):
        super().__init__(timeout=120)
        self.snipes = snipes[::-1]
        self.index = 0
        self.user = user

    def format_time(self, time):
        diff = datetime.utcnow() - time
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
            title=f"Deleted Message {self.index+1}/{len(self.snipes)}",
            color=discord.Color.purple()
        )

        embed.add_field(name="👤 Author", value=data["author"], inline=False)
        embed.add_field(name="⏱ Deleted", value=self.format_time(data["time"]), inline=False)
        embed.add_field(name="📩 Content", value=data["content"], inline=False)

        embed.set_footer(
            text=f"Requested by {self.user}",
            icon_url=self.user.display_avatar.url
        )

        embed.set_thumbnail(url=data["avatar"])
        return embed

    async def interaction_check(self, interaction):
        return interaction.user == self.user

    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def first(self, interaction: discord.Interaction, button):
        self.index = 0
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button):
        await interaction.message.delete()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button):
        if self.index < len(self.snipes) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def last(self, interaction: discord.Interaction, button):
        self.index = len(self.snipes) - 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}

    # 🔐 PERMISSION CHECK (OWNER BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True

            return ctx.author.guild_permissions.manage_messages

        return commands.check(predicate)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        data = {
            "content": message.content if message.content else "*No content*",
            "author": message.author.mention,
            "avatar": message.author.display_avatar.url,
            "time": datetime.utcnow()
        }

        if message.channel.id not in self.snipes:
            self.snipes[message.channel.id] = []

        self.snipes[message.channel.id].append(data)

        if len(self.snipes[message.channel.id]) > 20:
            self.snipes[message.channel.id].pop(0)

    # 🔍 SNIPE COMMAND (PREFIX + SLASH)
    @commands.hybrid_command(name="snipe", description="View deleted messages")
    @has_perm_or_owner()
    async def snipe(self, ctx):

        if ctx.channel.id not in self.snipes or not self.snipes[ctx.channel.id]:
            return await ctx.send("No recently deleted messages.")

        view = SnipeView(self.snipes[ctx.channel.id], ctx.author)
        await ctx.send(embed=view.get_embed(), view=view)

    # ❗ ERROR HANDLER
    @snipe.error
    async def snipe_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Snipe(bot))
