import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import datetime
import os
import shutil
import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# --- SPOTIFY SETUP (Optional but recommended) ---
# Agar aapke paas Client ID/Secret nahi hai, toh ye sirf link read karega
sp = None
try:
    # Aap Spotify Developer Dashboard se ye le sakte hain (Free)
    # Warna ye block skip ho jayega
    auth_manager = SpotifyClientCredentials(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET")
    sp = spotipy.Spotify(auth_manager=auth_manager)
except:
    pass

# --- CONFIG ---
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch1',
    'source_address': '0.0.0.0',
    # Bypass Headers
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
    }
}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

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

    async def start_playing(self, ctx, info):
        url = info['url']
        source = await discord.FFmpegOpusAudio.from_probe(url, executable=self.get_ffmpeg(), **FFMPEG_OPTIONS)
        vol = self.volume.get(ctx.guild.id, 1.0)
        source = discord.PCMVolumeTransformer(source, volume=vol)
        ctx.voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
        
        embed = discord.Embed(color=0x1DB954) # Spotify Green
        if info.get('thumbnail'): embed.set_image(url=info['thumbnail'])
        embed.description = (
            f"{self.music_record} **Now Playing**\n\n"
            f"{self.blue_arrow} **[{info['title']}]({info.get('webpage_url')})**\n"
            f"{self.green_arrow} **Source:** Spotify/YT Logic\n"
            f"{self.green_arrow} **Requested by:** {ctx.author.mention}"
        )
        await ctx.send(embed=embed)

    async def play_next(self, ctx):
        if self.queue.get(ctx.guild.id):
            info = self.queue[ctx.guild.id].pop(0)
            await self.start_playing(ctx, info)

    @commands.hybrid_command(name="play", aliases=["p"])
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice: return await ctx.send(f"{self.cross} Join a VC!")
        if not ctx.voice_client: await ctx.author.voice.channel.connect()
        
        if ctx.guild.id not in self.queue: self.queue[ctx.guild.id] = []
        if ctx.guild.id not in self.volume: self.volume[ctx.guild.id] = 1.0

        m = await ctx.send(f"{self.loading} Processing your request...")

        # --- SPOTIFY LINK DETECTION ---
        if "spotify.com" in search:
            if "track" in search:
                # Gaane ka naam nikalne ke liye (Basic logic without API)
                track_id = search.split("track/")[1].split("?")[0]
                if sp:
                    track = sp.track(track_id)
                    search = f"{track['name']} {track['artists'][0]['name']}"
                else:
                    # Agar Spotify API nahi hai, toh title fetch karne ka try karein
                    return await m.edit(content=f"{self.cross} Please provide Spotify API credentials in code.")
            else:
                return await m.edit(content=f"{self.cross} Only Spotify Track links are supported for now.")

        # --- YT-DLP SEARCH ---
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{search}", download=False))
            
            if not data or 'entries' not in data: return await m.edit(content="❌ No results.")
            info = data['entries'][0]
        except Exception as e:
            return await m.edit(content=f"{self.cross} YouTube/Spotify Error: `Sign-in required` (IP Blocked).")

        if ctx.voice_client.is_playing():
            self.queue[ctx.guild.id].append(info)
            return await m.edit(content=f"📝 Added to Queue: `{info['title']}`")

        await m.delete()
        await self.start_playing(ctx, info)

async def setup(bot):
    await bot.add_cog(Music(bot))
