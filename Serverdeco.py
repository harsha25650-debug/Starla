import discord
from discord.ext import commands
import aiohttp

class ServerDeco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper function: Finds the image URL (from Reply, Attachment, or Direct Link)
    async def get_image_url(self, ctx, argument: str = None):
        # 1. If the message is a REPLY to another message
        if ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                return replied_msg.attachments[0].url
            # If the replied message contains a plain URL link
            elif replied_msg.content.startswith("http"):
                return replied_msg.content.strip()

        # 2. If a file is UPLOADED directly alongside the command
        if ctx.message.attachments:
            return ctx.message.attachments[0].url

        # 3. If a text LINK/URL is provided as an argument
        if argument and argument.startswith("http"):
            return argument.strip()

        return None

    # Helper function: Downloads the image from the URL and returns bytes
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
        """Change the server icon (via Reply, Upload, or Link)"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please reply to an image, upload a file, or provide a direct image link!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await ctx.guild.edit(icon=image_bytes)
                await ctx.send("✅ Server icon has been successfully updated!")
            else:
                await ctx.send("❌ Failed to download the image. Please verify the link.")
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to change the server icon.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: `{e}`")

    @commands.command(name="setserverbanner")
    @commands.has_permissions(manage_guild=True)
    async def set_server_banner(self, ctx, *, link: str = None):
        """Change the server banner (via Reply, Upload, or Link) - Requires Server Boosting"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please reply to an image, upload a file, or provide a direct image link!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await ctx.guild.edit(banner=image_bytes)
                await ctx.send("✅ Server banner has been successfully updated!")
            else:
                await ctx.send("❌ Failed to download the image. Please verify the link.")
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to change the banner, or the server lacks the required Boost level.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: `{e}`")


    # --- COMMANDS FOR BOT ---

    @commands.command(name="setboticon")
    @commands.is_owner() # Ensures only the bot developer/owner can alter the bot's look
    async def set_bot_icon(self, ctx, *, link: str = None):
        """Change the bot's avatar/icon (via Reply, Upload, or Link)"""
        await ctx.typing()
        url = await self.get_image_url(ctx, link)

        if not url:
            return await ctx.send("❌ Please reply to an image, upload a file, or provide a direct image link!")

        try:
            image_bytes = await self.download_image(url)
            if image_bytes:
                await self.bot.user.edit(avatar=image_bytes)
                await ctx.send("✅ Bot avatar has been successfully updated!")
            else:
                await ctx.send("❌ Failed to download the image. Please verify the link.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Discord API Error (You may be changing avatars too fast): `{e}`")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: `{e}`")

# Setup function to register the cog
async def setup(bot):
    await bot.add_cog(ServerDeco(bot))
    
