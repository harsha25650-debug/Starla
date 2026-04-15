import discord
from discord.ext import commands
from discord import app_commands

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

    # 🎭 ROLE ICON
    @commands.hybrid_command(name="roleicon", description="Set role icon")
    @app_commands.describe(role="Target role", emoji="Emoji")
    @has_perm_or_owner()
    async def roleicon(self, ctx, role: discord.Role, emoji: str):

        if role >= ctx.guild.me.top_role:
            return await ctx.send("⛔ This role is higher than my role.")

        try:
            if len(emoji) <= 4:
                await role.edit(display_icon=emoji.encode("utf-8"))

            elif emoji.startswith("<:") or emoji.startswith("<a:"):
                emoji_id = int(emoji.split(":")[2][:-1])
                guild_emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

                if guild_emoji is None:
                    return await ctx.send("❌ Emoji not found.")

                await role.edit(display_icon=await guild_emoji.read())

            else:
                return await ctx.send("❌ Invalid emoji.")

            embed = self.create_embed(
                "✨ Role Icon Updated",
                f"{role.mention} ka icon update ho gaya.",
                discord.Color.purple()
            )
            await ctx.send(embed=embed)

        except Exception:
            await ctx.send("⚠️ Failed to update role icon.")

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
