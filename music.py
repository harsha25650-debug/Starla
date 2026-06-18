import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime
import os
import shutil

# --- 🚀 UPDATED SOUNDCLOUD BYPASS CONFIG ---
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'scsearch1',
    'source_address': '0.0.0.0',
    'force_generic_extractor': False, # Raw stream extraction helper
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
    }
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

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
        if os.path.exists(p): 
            try: os.chmod(p, 0o755)
            except: pass
            return p
        return "ffmpeg"

    async def play_music(self, ctx, info):
        if not ctx.voice_client: return
        
        # 🔥 MULTI-FALLBACK URL EXTRACTOR (Isse stream load fail nahi hoga)
        url = None
        if 'url' in info:
            url = info['url']
        elif 'formats' in info and len(info['formats']) > 0:
            url = info['formats'][0]['url']
            
        if not url:
            return await ctx.send(f"{self.cross} Audio Error: `Could not extract playable stream URL.`")
            
        exe = self.get_ffmpeg()
        
        try:
            source = await discord.FFmpegOpusAudio.from_probe(url, executable=exe, **FFMPEG_OPTIONS)
            vol = self.volume.get(ctx.guild.id, 1.0)
            source = discord.PCMVolumeTransformer(source, volume=vol)
            
            ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            
            embed = discord.Embed(color=0x1DB954)
            if info.get('thumbnail'): 
                embed.set_image(url=info['thumbnail'])
            embed.description = (
                f"{self.music_record} **Now Playing (SoundCloud)**\n\n"
                f"{self.blue_arrow} **[{info['title']}]({info.get('webpage_url')})**\n"
                f"{self.green_arrow} **Requested by:** {ctx.author.mention}"
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"{self.cross} Audio Error: `{e}`")

    async def play_next(self, ctx):
        if self.queue.get(ctx.guild.id) and len(self.queue[ctx.guild.id]) > 0:
            info = self.queue[ctx.guild.id].pop(0)
            await self.play_music(ctx, info)

    @commands.hybrid_command(name="play", aliases=["p"], description="Play music from SoundCloud")
    @app_commands.describe(search="Song name or SoundCloud link")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(f"{self.cross} Join a Voice Channel first!")
        
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        if ctx.guild.id not in self.queue: self.queue[ctx.guild.id] = []
        if ctx.guild.id not in self.volume: self.volume[ctx.guild.id] = 1.0

        m = await ctx.send(f"{self.loading} Searching SoundCloud...")

        if "youtube.com" in search or "youtu.be" in search or "spotify.com" in search:
            return await m.edit(content=f"{self.cross} Links are disabled! Please type the **Song Name and Artist** text instead.")

        # 🔥 Stream Extraction Fix Block
        try:
            query = search if search.startswith("http") else f"scsearch:{search}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = self.bot.loop
                # Re-fetch info with download=False but extracting all sub-entries
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False, process=True))
            
            if not data:
                return await m.edit(content="❌ No results found on SoundCloud.")
                
            if 'entries' in data:
                if not data['entries']:
                    return await m.edit(content="❌ No entries found.")
                info = data['entries'][0]
            else:
                info = data
                
        except Exception as e:
            print(f"SoundCloud Critical Error: {e}")
            return await m.edit(content=f"{self.cross} Music Engine Error: `Failed to fetch audio stream`.")

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            self.queue[ctx.guild.id].append(info)
            return await m.edit(content=f"📝 **Added to Queue:** `{info['title']}`")

        await m.delete()
        await self.play_music(ctx, info)

    @commands.hybrid_command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
            ctx.voice_client.stop()
            await ctx.send("⏭️ **Skipped!**")
        else:
            await ctx.send(f"{self.cross} Nothing is playing.")

async def setup(bot):
    await bot.add_cog(Music(bot))
    
