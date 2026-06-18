import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime
import os
import shutil

# --- 🚀 RE-OPTIMIZED CONFIG TO BYPASS YT DETECTION ---
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',
    # Bot detection ko thanda karne ke liye critical options:
    'extractor_args': {
        'youtube': {
            'player_client': ['android_music', 'web'],
            'skip': ['webpage']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
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
        
        # Stream URL extraction with fallback check
        url = info.get('url') or info.get('formats')[0]['url']
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
                f"{self.music_record} **Now Playing**\n\n"
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

    @commands.hybrid_command(name="play", aliases=["p"], description="Play music from YT/Spotify")
    @app_commands.describe(search="Song name or link")
    async def play(self, ctx, *, search: str):
        # 1. Voice Connection Check
        if not ctx.author.voice:
            return await ctx.send(f"{self.cross} Join a Voice Channel first!")
        
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        # 2. Data Initialization
        if ctx.guild.id not in self.queue: self.queue[ctx.guild.id] = []
        if ctx.guild.id not in self.volume: self.volume[ctx.guild.id] = 1.0

        m = await ctx.send(f"{self.loading} Processing...")

        # 3. Spotify Link Cleaning
        if "spotify.com" in search:
            search = search.split("?")[0]
            await m.edit(content=f"{self.loading} Extracting Spotify metadata...")
            # Note: Spotify streams generally require Title lookup on YouTube fallback

        # 4. YT-DLP Search Block with dynamic query fix
        try:
            query = search if search.startswith("http") else f"ytsearch:{search}"
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = self.bot.loop
                # Extract data asynchronously to keep Railway container stable
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
            
            if not data:
                return await m.edit(content="❌ No results found on YouTube.")
                
            if 'entries' in data:
                # If it's a search result query block
                if not data['entries']:
                    return await m.edit(content="❌ No entries found.")
                info = data['entries'][0]
            else:
                # If it's a direct YouTube video URL link
                info = data
                
        except Exception as e:
            print(f"YT-DLP Critical Error: {e}")
            return await m.edit(content=f"{self.cross} YouTube Error: `IP Blocked or Bot Detected`. Try generic song names instead of direct links!")

        # 5. Play Logic
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
            
