import discord
from discord.ext import commands
import aiohttp
import asyncio
import re

class Steal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_green = "<:starlaDotGreen:1525756444782104597>"
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.ico_info = "<:starla_ico_info:1525756986283524238>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    # 🔐 PERMISSION CHECK
    def can_manage_expressions():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id or ctx.author.id == ctx.guild.owner_id:
                return True
            if ctx.author.guild_permissions.manage_expressions:
                return True
            return False
        return commands.check(predicate)

    # 📥 HELPER FUNCTION TO DOWNLOAD & ADD EMOJI
    async def process_emoji(self, ctx, session, is_animated, name, emoji_id):
        ext = "gif" if is_animated else "png"
        url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
        try:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                img = await resp.read()
            
            new_emoji = await ctx.guild.create_custom_emoji(
                name=name, image=img, reason=f"Stealed by {ctx.author}"
            )
            return new_emoji
        except Exception:
            return None

    @commands.command(name="steal", description="Steal multiple emojis via arguments or by replying to a message")
    @can_manage_expressions()
    @commands.bot_has_permissions(manage_expressions=True)
    async def steal(self, ctx, *, args: str = None):
        target_content = ""

        # 1. Check if user replied to a message
        if ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            target_content += replied_msg.content
            
            # Stickers Extraction Fallback (If any)
            if replied_msg.stickers:
                sticker = replied_msg.stickers[0]
                # Quick Sticker Process (Since stickers can only be added one by one)
                status_msg = await ctx.send(f"{self.dot_black} Processing sticker asset...")
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(sticker.url) as resp:
                            img = await resp.read()
                    new_sticker = await ctx.guild.create_sticker(
                        name=sticker.name, description="Stolen Sticker", emoji="😎", file=discord.File(fp=discord.BytesIO(img), filename="sticker.png"), reason=f"Stolen by {ctx.author}"
                    )
                    return await status_msg.edit(content=f"{self.yes} **Sticker Stolen Successfully!** | {new_sticker.name}")
                except Exception as e:
                    return await status_msg.edit(content=f"{self.cross} **Sticker Error:** `{e}`")

        # 2. Append direct command arguments if present
        if args:
            target_content += " " + args

        if not target_content.strip():
            embed = discord.Embed(
                description=f"{self.cross} **Usage Error:** Provide emojis after the command or reply to an emoji message.",
                color=0x2b2d31
            )
            return await ctx.send(embed=embed)

        # 3. Regex parser to extract ALL custom emojis inside string block
        custom_emojis = re.findall(r"<(a?):(\w+):(\d+)>", target_content)

        if not custom_emojis:
            embed = discord.Embed(description=f"{self.cross} **No stealable custom emoji assets found.**", color=0x2b2d31)
            return await ctx.send(embed=embed)

        # Remove duplicate emojis from the list to avoid double addition
        custom_emojis = list(dict.fromkeys(custom_emojis))

        status_embed = discord.Embed(
            description=f"{self.dot_black} **Extracting and processing `{len(custom_emojis)}` emoji assets...**",
            color=0x2b2d31
        )
        status_msg = await ctx.send(embed=status_embed)

        successful_emojis = []
        failed_count = 0

        async with aiohttp.ClientSession() as session:
            for is_anim, name, emoji_id in custom_emojis:
                added_emoji = await self.process_emoji(ctx, session, is_anim, name, emoji_id)
                if added_emoji:
                    successful_emojis.append(str(added_emoji))
                else:
                    failed_count += 1
                await asyncio.sleep(0.5) # Rate limit security delay

        # 4. FINAL SUCCESS RESPONSE EMBED
        final_embed = discord.Embed(
            title=f"{self.ico_info} Asset Stealer Output",
            color=0x2b2d31
        )
        
        if successful_emojis:
            emoji_chain = " ".join(successful_emojis)
            final_embed.description = f"{self.dot_green} **Successfully added {len(successful_emojis)} emoji(s):**\n\n{emoji_chain}"
        else:
            final_embed.description = f"{self.cross} **Failed to steal emoji assets.** Guild limits might be full."

        if failed_count > 0:
            final_embed.add_field(name="Failed Operations", value=f"{self.arrow} `{failed_count}` assets skipped/failed.", inline=False)

        final_embed.set_footer(text=f"Action by {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
        await status_msg.edit(embed=final_embed)

    # ❗ CLEAN PERMISSION ERROR HANDLER
    @steal.error
    async def steal_error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f"{self.no} **Access Denied:** You need `Manage Expressions` permission to steal assets.", 
                color=0x2b2d31
            )
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"{self.cross} I am missing `Manage Expressions` slots authority.")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Steal(bot))
                    
