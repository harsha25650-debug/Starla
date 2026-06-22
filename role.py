import discord
from discord.ext import commands
from discord import app_commands
import aiohttp

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔐 PERMISSION CHECK (OWNER BYPASS)
    def has_perm_or_owner():
        async def predicate(ctx):
            if ctx.author.id == ctx.bot.owner_id:
                return True
            return ctx.author.guild_permissions.manage_roles
        return commands.check(predicate)

    # 🎨 EMBED BUILDER
    def create_embed(self, title, description, color):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )
        return embed

    # 🖼️ HELPER: Image URL ya Emoji nikalne ke liye
    async def get_image_or_emoji(self, ctx, argument: str = None):
        # 1. Agar kisi message par REPLY kiya gaya hai
        if ctx.message.reference:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if replied_msg.attachments:
                return "url", replied_msg.attachments[0].url
            elif replied_msg.content.startswith("http"):
                return "url", replied_msg.content.strip()

        # 2. Agar command ke saath file UPLOAD ki gayi hai
        if ctx.message.attachments:
            return "url", ctx.message.attachments[0].url

        # 3. Agar command ke saath text (Link ya Emoji) diya gaya hai
        if argument:
            argument = argument.strip()
            if argument.startswith("http"):
                return "url", argument
            else:
                return "emoji", argument

        return None, None

    # ⬇️ HELPER: URL se image download karne ke liye
    async def download_image(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None

    # 🔁 ROLE TOGGLE (EMBED VERSION)
    @commands.hybrid_command(name="role", description="Add or remove a role")
    @app_commands.describe(member="Target user", role="Select role")
    @has_perm_or_owner()
    async def role(self, ctx, member: discord.Member, role: discord.Role):

        # 🚨 PERMISSION CHECK
        if not ctx.guild.me.guild_permissions.manage_roles:
            embed = self.create_embed(
                "⛔ Permission Missing",
                "I need **Manage Roles** permission.",
                discord.Color.red()
            )
            return await ctx.send(embed=embed)

        # 🚨 ROLE POSITION CHECK
        if role >= ctx.guild.me.top_role:
            embed = self.create_embed(
                "⛔ Role Hierarchy Error",
                "This role is higher than my role.",
                discord.Color.red()
            )
            return await ctx.send(embed=embed)

        if member.top_role >= ctx.guild.me.top_role:
            embed = self.create_embed(
                "⛔ Cannot Modify User",
                "This user has higher or equal role than me.",
                discord.Color.red()
            )
            return await ctx.send(embed=embed)

        try:
            # 🔁 TOGGLE SYSTEM
            if role in member.roles:
                await member.remove_roles(role, reason=f"Removed by {ctx.author}")

                embed = self.create_embed(
                    "❌ Role Removed",
                    f"{member.mention} se `{role.name}` remove kar diya gaya.",
                    discord.Color.red()
                )

            else:
                await member.add_roles(role, reason=f"Added by {ctx.author}")

                embed = self.create_embed(
                    "✅ Role Added",
                    f"{member.mention} ko `{role.name}` de diya gaya.",
                    discord.Color.green()
                )

            embed.set_footer(text=f"Action by {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = self.create_embed(
                "⛔ Permission Error",
                "Role assign/remove nahi kar pa raha (hierarchy issue).",
                discord.Color.red()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = self.create_embed(
                "⚠️ Unexpected Error",
                f"{e}",
                discord.Color.orange()
            )
            await ctx.send(embed=embed)

    # 🎭 ROLE ICON (UPGRADED VERSION)
    @commands.hybrid_command(name="roleicon", description="Set role icon via Image, Link, Reply or Emoji")
    @app_commands.describe(role="Target role", input_data="Emoji or Image Link (Optional if replying/uploading)")
    @has_perm_or_owner()
    async def roleicon(self, ctx, role: discord.Role, *, input_data: str = None):
        await ctx.typing()

        # 🚨 ROLE POSITION CHECK
        if role >= ctx.guild.me.top_role:
            return await ctx.send("⛔ This role is higher than my role.")

        # Data type aur source check karein
        data_type, source = await self.get_image_or_emoji(ctx, input_data)

        if not data_type:
            return await ctx.send("❌ Please kisi image par reply karein, file upload karein, link dein, ya koi emoji use karein!")

        try:
            # --- AGAR IMAGE/LINK HAI ---
            if data_type == "url":
                image_bytes = await self.download_image(source)
                if image_bytes:
                    await role.edit(display_icon=image_bytes)
                else:
                    return await ctx.send("❌ Image download karne mein dikkat aayi.")

            # --- AGAR UNICODE YA CUSTOM EMOJI HAI ---
            elif data_type == "emoji":
                if len(source) <= 4:  # Unicode Emoji (e.g., ⭐)
                    await role.edit(display_icon=source.encode("utf-8"))

                elif source.startswith("<:") or source.startswith("<a:"):  # Custom Guild Emoji
                    emoji_id = int(source.split(":")[2][:-1])
                    guild_emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

                    if guild_emoji is None:
                        return await ctx.send("❌ Yeh emoji is server mein nahi mila.")

                    await role.edit(display_icon=await guild_emoji.read())
                else:
                    return await ctx.send("❌ Invalid emoji ya format.")

            # Success Embed
            embed = self.create_embed(
                "✨ Role Icon Updated",
                f"{role.mention} ka icon successfully update ho gaya hai.",
                discord.Color.purple()
            )
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ Mere paas roles manage karne ki permission nahi hai.")
        except Exception as e:
            await ctx.send(f"⚠️ Failed to update role icon. Error: `{e}`")

    # ❗ ERROR HANDLER
    @role.error
    @roleicon.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Role(bot))
            
