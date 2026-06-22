import discord
from discord.ext import commands
import aiohttp

class ServerDeco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function: Jo image ka URL dhoondhegi (Reply, Attachment, ya Direct Link se)
    async def get_image_url(self, ctx, argument: str = None):
        # 1. Agar kisi message par REPLY kiya gaya hai
        if ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                return replied_msg.attachments[0].url
            # Agar reply wale message mein koi link ho
            elif replied_msg.content.startswith("http"):
                return replied_msg.content.strip()

        # 2. Agar command ke saath file UPLOAD ki gayi hai
        if ctx.message.attachments:
            return ctx.message.attachments[0].url

        # 3. Agar command ke saath text mein LINK diya gaya hai
        if argument and argument.startswith("http"):
            return argument.strip()

        return None

    # Helper function: URL se image download karke bytes mein badalne ke liye
    async def download_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None

    # --- COMMANDS FOR SERVER ---

    @commands.command(name="setservericon")
    @commands.has_permissions(manage_guild=True)
    async def set_server_icon(self, ctx, *, link: str = None):
        """Server ka icon badle (Reply, Upload, ya Link se)"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please kisi image par reply karein, file upload karein, ya image ka link dein!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await ctx.guild.edit(icon=image_bytes)
                await ctx.send("✅ Server icon successfully change ho gaya hai!")
            else:
                await ctx.send("❌ Image download karne mein dikkat aayi.")
        except discord.Forbidden:
            await ctx.send("❌ Mere paas server icon change karne ki permission nahi hai.")
        except Exception as e:
            await ctx.send(f"❌ Ek error aayi: `{e}`")

    @commands.command(name="setserverbanner")
    @commands.has_permissions(manage_guild=True)
    async def set_server_banner(self, ctx, *, link: str = None):
        """Server ka banner badle (Reply, Upload, ya Link se) - Needs Server Boost"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please kisi image par reply karein, file upload karein, ya image ka link dein!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await ctx.guild.edit(banner=image_bytes)
                await ctx.send("✅ Server banner successfully change ho gaya hai!")
            else:
                await ctx.send("❌ Image download karne mein dikkat aayi.")
        except discord.Forbidden:
            await ctx.send("❌ Mere paas banner change karne ki permission nahi hai ya server boosted nahi hai.")
        except Exception as e:
            await ctx.send(f"❌ Ek error aayi: `{e}`")


    # --- COMMANDS FOR BOT ---

    @commands.command(name="setboticon")
    @commands.is_owner() # Bot ka icon sirf bot owner badal sake
    async def set_bot_icon(self, ctx, *, link: str = None):
        """Bot ka avatar/icon badle (Reply, Upload, ya Link se)"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please kisi image par reply karein, file upload karein, ya image ka link dein!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await self.bot.user.edit(avatar=image_bytes)
                await ctx.send("✅ Bot ka avatar/icon successfully change ho gaya hai!")
            else:
                await ctx.send("❌ Image download karne mein dikkat aayi.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Discord error (Shayad aap bahut jaldi-jaldi change kar rahe hain): `{e}`")
        except Exception as e:
            await ctx.send(f"❌ Ek error aayi: `{e}`")

# Setup function cog ko register karne ke liye
async def setup(bot):
    await bot.add_cog(ServerDeco(bot))
  
