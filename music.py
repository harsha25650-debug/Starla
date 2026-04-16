import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime
import os
import shutil

# --- CONFIG ---
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    'quiet': True,
    'extract_flat': True,
    'source_address': '0.0.0.0',
    'nocheckcertificate': True,
    'default_search': 'ytsearch',
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
    async def skip_btn(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭️ **Skipped!**", ephemeral=True)

    @discord.ui.button(label="■", style=discord.ButtonStyle.secondary)
    async def stop_btn(self, interaction: discord.Interaction, button):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⏹️ **Stopped!**", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.volume = {} # Default 1.0 (100%)
        
        # Emojis
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.music_record = "<a:4778musicrecordspin:1494220147618218046>"
        self.blue_arrow = "<a:blue_arrow:1494220576313573536>"
        self.green_arrow = "<:GreenArrow:1494220659029442570>"
        self.cross = "<a:spider_cross:1494181311525687347>"

    def get_ffmpeg_path(self):
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg")
        if os.path.exists(local_ffmpeg):
            try: os.chmod(local_ffmpeg, 0o755)
            except: pass
            return local_ffmpeg
        return shutil.which("ffmpeg") or "ffmpeg"

    def check_queue(self, ctx):
        if ctx.guild.id in self.queue and self.queue[ctx.guild.id]:
            next_song = self.queue[ctx.guild.id].pop(0)
            asyncio.run_coroutine_threadsafe(self.play_music(ctx, next_song, is_next=True), self.bot.loop)

    async def play_music(self, ctx, info, is_next=False):
        url = info.get('url')
        exe_path = self.get_ffmpeg_path()
        
        # Audio fix: Using PCMVolumeTransformer for better audio delivery
        source = await discord.FFmpegOpusAudio.from_probe(url, executable=exe_path, **FFMPEG_OPTIONS)
        vol = self.volume.get(ctx.guild.id, 1.0)
        transformed_source = discord.PCMVolumeTransformer(source, volume=vol)

        ctx.voice_client.play(transformed_source, after=lambda e: self.check_queue(ctx))

        if is_next:
            embed = self.create_embed(info, ctx.author)
            await ctx.send(embed=embed, view=MusicView(self.bot))

    def create_embed(self, info, author):
        web_url = info.get('webpage_url', f"https://www.youtube.com/watch?v={info.get('id')}")
        embed = discord.Embed(color=0x000000)
        if info.get('thumbnail'):
            embed.set_image(url=info.get('thumbnail'))
        
        embed.description = (
            f"{self.music_record} **Now Playing...**\n\n"
            f"{self.blue_arrow} **[{info.get('title')}]({web_url})**\n"
            f"{self.green_arrow} **Requested by:** {author.mention}"
        )
        duration = str(datetime.timedelta(seconds=info.get('duration', 0)))
        vol_percent = int(self.volume.get(author.guild.id, 1.0) * 100)
        embed.set_footer(text=f"Duration: {duration} | Volume: {vol_percent}%")
        return embed

    @commands.hybrid_command(name="play", aliases=["p"], description="Play music")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(f"{self.cross} Join a Voice Channel!")

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        # Init Queue and Vol for guild
        if ctx.guild.id not in self.queue: self.queue[ctx.guild.id] = []
        if ctx.guild.id not in self.volume: self.volume[ctx.guild.id] = 1.0

        msg = await ctx.send(f"{self.loading} Searching for `{search}`...")

        async with ctx.typing():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
                except Exception as e:
                    return await msg.edit(content=f"{self.cross} Error: `{e}`")

            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                self.queue[ctx.guild.id].append(info)
                return await msg.edit(content=f"📝 **Added to Queue:** `{info['title']}`")

            await self.play_music(ctx, info)

        embed = self.create_embed(info, ctx.author)
        await msg.edit(content=None, embed=embed, view=MusicView(self.bot))

    @commands.hybrid_command(name="skip", aliases=["s"], description="Skip current song")
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            ctx.voice_client.stop()
            await ctx.send("⏭️ **Song Skipped!**")
        else:
            await ctx.send(f"{self.cross} Nothing is playing.")

    @commands.hybrid_command(name="volume", aliases=["vol"], description="Change volume 0-100")
    async def set_volume(self, ctx, amount: int):
        if not ctx.voice_client: return await ctx.send(f"{self.cross} I'm not in VC.")
        
        if 0 <= amount <= 100:
            vol_dec = amount / 100
            self.volume[ctx.guild.id] = vol_dec
            if ctx.voice_client.source:
                ctx.voice_client.source.volume = vol_dec
            await ctx.send(f"🔊 **Volume set to {amount}%**")
        else:
            await ctx.send("Enter volume between 0-100.")

    @commands.hybrid_command(name="nonstop", aliases=["247"], description="24/7 Mode")
    async def toggle_247(self, ctx):
        guild_id = str(ctx.guild.id)
        current = self.bot.db.get(f"247_{guild_id}", False)
        self.bot.db.set(f"247_{guild_id}", not current)
        status = "Activated" if not current else "Deactivated"
        await ctx.send(f"✅ **24/7 Mode {status}!**")

async def setup(bot):
    await bot.add_cog(Music(bot))
