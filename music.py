import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime

# --- CONFIG ---
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    'quiet': True,
    'extract_flat': True,
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

class MusicView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="II", style=discord.ButtonStyle.secondary)
    async def pause_resume(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if not vc: return
        if vc.is_paused():
            vc.resume()
            button.label = "II"
        else:
            vc.pause()
            button.label = "▶"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="▶I", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ **Skipped!**", ephemeral=True)

    @discord.ui.button(label="■", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⏹️ **Stopped!**", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.music_record = "<a:4778musicrecordspin:1494220147618218046>"
        self.blue_arrow = "<a:blue_arrow:1348026098004525096>"
        self.green_arrow = "<:GreenArrow:1364257579550773362>"
        self.success = "<a:greentick:1494180392440303777>"
        self.cross = "<a:spider_cross:1494181311525687347>"

    @commands.hybrid_command(name="play", aliases=["p"], description="Play music")
    @app_commands.describe(search="Song name or link")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(f"{self.cross} You must be in a Voice Channel!")

        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(f"{self.cross} Could not connect to VC: `{e}`")

        await ctx.send(f"{self.loading} Searching for `{search}`...")

        async with ctx.typing():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                    url = info['url']
                except:
                    return await ctx.send(f"{self.cross} No results found.")

            # Discord Voice check before playing
            try:
                source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source)
            except Exception as e:
                return await ctx.send(f"{self.cross} Voice Error: `{e}`. Make sure FFmpeg and PyNaCl are installed.")

        embed = discord.Embed(color=0x000000)
        embed.set_image(url=info.get('thumbnail'))
        embed.description = (
            f"{self.music_record} **Now Playing...**\n\n"
            f"{self.blue_arrow} **[{info['title']}]({info['webpage_url']})**\n"
            f"{self.green_arrow} **{info['uploader']}**\n\n"
            f"{self.green_arrow} Requested by: {ctx.author.mention}\n"
            f"{self.green_arrow} {self.music_record} **YouTube Music**"
        )
        embed.set_footer(text=f"Duration: {str(datetime.timedelta(seconds=info['duration']))}")
        
        await ctx.send(embed=embed, view=MusicView(self.bot))

    @commands.hybrid_command(name="nonstop", aliases=["247", "24/7"], description="Keep bot in VC 24/7")
    async def toggle_247(self, ctx):
        # PERMISSIONS REMOVED: Any user can now use this
        guild_id = str(ctx.guild.id)
        current_status = self.bot.db.get(f"247_{guild_id}", False)
        
        if not current_status:
            if not ctx.author.voice:
                return await ctx.send(f"{self.cross} You need to be in a VC to enable 24/7 mode!")
            
            self.bot.db.set(f"247_{guild_id}", True)
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()
            
            await ctx.send(f"{self.success} **24/7 Mode Activated!**")
        else:
            self.bot.db.set(f"247_{guild_id}", False)
            await ctx.send(f"{self.cross} **24/7 Mode Deactivated!**")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id and after.channel is None:
            guild_id = str(member.guild.id)
            if self.bot.db.get(f"247_{guild_id}", False):
                if before.channel:
                    try:
                        await before.channel.connect()
                    except:
                        pass

async def setup(bot):
    await bot.add_cog(Music(bot))
                    
