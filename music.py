import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime
import os
import shutil

# --- UPDATED CONFIG TO BYPASS BOT DETECTION ---
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',
    # Bot detection bypass headers
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
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
    async def pause_resume(self, i: discord.Interaction, b):
        vc = i.guild.voice_client
        if not vc: return
        if vc.is_paused(): vc.resume(); b.label = "II"
        else: vc.pause(); b.label = "▶"
        await i.response.edit_message(view=self)

    @discord.ui.button(label="▶I", style=discord.ButtonStyle.secondary)
    async def skip(self, i: discord.Interaction, b):
        if i.guild.voice_client: i.guild.voice_client.stop()
        await i.response.send_message("⏭️ Skipped!", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.volume = {}
        # Emojis
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.music_record = "<a:4778musicrecordspin:1494220147618218046>"
        self.blue_arrow = "<a:blue_arrow:1494220576313573536>"
        self.green_arrow = "<:GreenArrow:1494220659029442570>"
        self.cross = "<a:spider_cross:1494181311525687347>"

    def get_ffmpeg(self):
        p = os.path.join(os.getcwd(), "ffmpeg")
        if os.path.exists(p): os.chmod(p, 0o755); return p
        return "ffmpeg"

    async def play_next(self, ctx):
        if self.queue.get(ctx.guild.id):
            info = self.queue[ctx.guild.id].pop(0)
            await self.start_playing(ctx, info)

    async def start_playing(self, ctx, info):
        url = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url, executable=self.get_ffmpeg(), **FFMPEG_OPTIONS)
        vol = self.volume.get(ctx.guild.id, 1.0)
        source = discord.PCMVolumeTransformer(source, volume=vol)
        ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
        
        embed = self.make_embed(info, ctx.author)
        await ctx.send(embed=embed, view=MusicView(self.bot))

    def make_embed(self, info, author):
        embed = discord.Embed(color=0x000000)
        if info.get('thumbnail'): embed.set_image(url=info['thumbnail'])
        embed.description = (
            f"{self.music_record} **Now Playing**\n\n"
            f"{self.blue_arrow} **[{info['title']}]({info.get('webpage_url')})**\n"
            f"{self.green_arrow} **Requested by:** {author.mention}"
        )
        return embed

    @commands.hybrid_command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice: return await ctx.send(f"{self.cross} Join a VC!")
        if not ctx.voice_client: await ctx.author.voice.channel.connect()
        
        if ctx.guild.id not in self.queue: self.queue[ctx.guild.id] = []
        if ctx.guild.id not in self.volume: self.volume[ctx.guild.id] = 1.0

        m = await ctx.send(f"{self.loading} Searching `{search}`...")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                # Use extractor directly to bypass some bot checks
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{search}", download=False))
            
            if not data or 'entries' not in data: return await m.edit(content="❌ No results found.")
            info = data['entries'][0]
        except Exception as e:
            # Better error reporting
            err_msg = str(e).split('.')[0] # Shorten the error
            return await m.edit(content=f"{self.cross} YouTube Error: `{err_msg}`\nTry a different song or direct link.")

        if ctx.voice_client.is_playing():
            self.queue[ctx.guild.id].append(info)
            return await m.edit(content=f"📝 Added to Queue: `{info['title']}`")

        await m.delete()
        await self.start_playing(ctx, info)

async def setup(bot):
    await bot.add_cog(Music(bot))
