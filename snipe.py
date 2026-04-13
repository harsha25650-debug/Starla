import discord
from discord.ext import commands

class SnipeView(discord.ui.View):
    def __init__(self, snipes, author):
        super().__init__(timeout=60)
        self.snipes = snipes
        self.index = 0
        self.author = author

    def get_embed(self):
        snipe = self.snipes[self.index]

        embed = discord.Embed(
            description=snipe["content"],
            color=discord.Color.purple()
        )

        embed.set_author(
            name=snipe["author"],
            icon_url=snipe["avatar"]
        )

        embed.set_footer(
            text=f"Message {self.index + 1}/{len(self.snipes)}"
        )

        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.author

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.snipes) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipes = {}  # channel_id: list of messages

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        data = {
            "content": message.content or "*No text content*",
            "author": str(message.author),
            "avatar": message.author.display_avatar.url
        }

        if message.channel.id not in self.snipes:
            self.snipes[message.channel.id] = []

        self.snipes[message.channel.id].append(data)

        # limit (last 10 messages)
        if len(self.snipes[message.channel.id]) > 10:
            self.snipes[message.channel.id].pop(0)

    @commands.command()
    async def snipe(self, ctx):
        if ctx.channel.id not in self.snipes or not self.snipes[ctx.channel.id]:
            return await ctx.send("No deleted messages found.")

        snipes = self.snipes[ctx.channel.id]

        view = SnipeView(snipes, ctx.author)
        embed = view.get_embed()

        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Snipe(bot))
