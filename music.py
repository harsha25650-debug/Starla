import discord
from discord.ext import commands
from discord import app_commands
import wavelink

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Emojis
        self.loading = "<a:spider_red_dot:1494179666133516411>"
        self.music_record = "<a:4778musicrecordspin:1494220147618218046>"
        self.blue_arrow = "<a:blue_arrow:1494220576313573536>"
        self.green_arrow = "<:GreenArrow:1494220659029442570>"
        self.cross = "<a:spider_cross:1494181311525687347>"
        
        # Background task to connect to Lavalink Node
        self.bot.loop.create_task(self.connect_nodes())

    async def connect_nodes(self):
        """Public Free Lavalink Node connection setup"""
        await self.bot.wait_until_ready()
        
        # Free public stable node setup (No local setup required)
        nodes = [
            wavelink.Node(
                uri="http://lava.link:80", 
                password="youshallnotpass"
            )
        ]
        
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)
            print("🚀 NovaX Music Engine: Lavalink Node connected successfully!")
        except Exception as e:
            print(f"❌ Lavalink Connection Failed: {e}")

    # Event handler for tracks ending to auto-play queue
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        if not player:
            return
            
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)
            
            # Now playing notification
            ctx = player.home
            if ctx:
                embed = discord.Embed(color=0x1DB954)
                embed.description = (
                    f"{self.music_record} **Now Playing**\n\n"
                    f"{self.blue_arrow} **[{next_track.title}]({next_track.uri})**\n"
                    f"⏱️ Duration: `{datetime.timedelta(milliseconds=next_track.length)}`"
                )
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="play", aliases=["p"], description="Play premium high-quality music")
    @app_commands.describe(search="Song name or direct URL link")
    async def play(self, ctx, *, search: str):
        if not ctx.author.voice:
            return await ctx.send(f"{self.cross} Join a Voice Channel first!")

        # Connect to voice channel using wavelink player module
        if not ctx.voice_client:
            player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            player: wavelink.Player = ctx.voice_client

        # Track the context channel for updates
        player.home = ctx

        m = await ctx.send(f"{self.loading} Fetching audio stream tracks...")

        # Automatically look up track via YouTube/SoundCloud/Spotify on the server side
        tracks: wavelink.Search = await wavelink.Playable.search(search)
        if not tracks:
            return await m.edit(content=f"{self.cross} No results found for your search query.")

        if isinstance(tracks, wavelink.Playlist):
            # If it's a playlist link
            for track in tracks.tracks:
                player.queue.put(track)
            await m.edit(content=f"📝 **Added Playlist:** `{tracks.name}` ({len(tracks.tracks)} tracks) to Queue!")
        else:
            track = tracks[0]
            if player.playing:
                player.queue.put(track)
                await m.edit(content=f"📝 **Added to Queue:** `{track.title}`")
                return

            await m.delete()
            await player.play(track)
            
            embed = discord.Embed(color=0x1DB954)
            if track.artwork: 
                embed.set_thumbnail(url=track.artwork)
            embed.description = (
                f"{self.music_record} **Now Playing**\n\n"
                f"{self.blue_arrow} **[{track.title}]({track.uri})**\n"
                f"{self.green_arrow} **Requested by:** {ctx.author.mention}"
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if not player or not player.playing:
            return await ctx.send(f"{self.cross} Nothing is playing right now.")
            
        await player.skip()
        await ctx.send("⏭️ **Skipped the current song!**")

    @commands.hybrid_command(name="disconnect", aliases=["leave", "dc"])
    async def disconnect(self, ctx):
        player: wavelink.Player = ctx.voice_client
        if player:
            await player.disconnect()
            await ctx.send("👋 **Disconnected from voice channel.**")
        else:
            await ctx.send(f"{self.cross} I am not in a voice channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
    
