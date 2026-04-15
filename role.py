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

    # 🔁 ROLE TOGGLE (BEST VERSION - USES ROLE OBJECT)
    @commands.hybrid_command(name="role", description="Add or remove a role")
    @app_commands.describe(member="Target user", role="Select role")
    @has_perm_or_owner()
    async def role(self, ctx, member: discord.Member, role: discord.Role):

        # 🚨 BOT PERMISSION CHECK
        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.send("⛔ I need **Manage Roles** permission.")

        # 🚨 ROLE POSITION CHECK
        if role >= ctx.guild.me.top_role:
            return await ctx.send("⛔ This role is higher than my role.")

        # 🚨 MEMBER CHECK
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("⛔ I can't modify this user's roles.")

        try:
            if role in member.roles:
                await member.remove_roles(role, reason=f"Removed by {ctx.author}")
                await ctx.send(f"❌ Role `{role.name}` removed from {member.mention} ✔️")
            else:
                await member.add_roles(role, reason=f"Added by {ctx.author}")
                await ctx.send(f"✅ Role `{role.name}` added to {member.mention} ✔️")

        except discord.Forbidden:
            await ctx.send("⛔ Permission denied (role hierarchy issue).")

        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

    # 🎭 ROLE ICON COMMAND
    @commands.hybrid_command(name="roleicon", description="Set role icon")
    @app_commands.describe(role="Target role", emoji="Emoji")
    @has_perm_or_owner()
    async def roleicon(self, ctx, role: discord.Role, emoji: str):

        # 🚨 ROLE POSITION CHECK
        if role >= ctx.guild.me.top_role:
            return await ctx.send("⛔ This role is higher than my role.")

        try:
            # Unicode emoji
            if len(emoji) <= 4:
                await role.edit(display_icon=emoji.encode("utf-8"))

            # Custom emoji
            elif emoji.startswith("<:") or emoji.startswith("<a:"):
                emoji_id = int(emoji.split(":")[2][:-1])
                guild_emoji = discord.utils.get(ctx.guild.emojis, id=emoji_id)

                if guild_emoji is None:
                    return await ctx.send("❌ Emoji not found in this server.")

                await role.edit(display_icon=await guild_emoji.read())

            else:
                return await ctx.send("❌ Invalid emoji format.")

            await ctx.send(f"✨ Icon for {role.mention} updated successfully ✔️")

        except discord.Forbidden:
            await ctx.send("⛔ I don't have permission to edit this role.")

        except Exception as e:
            await ctx.send("⚠️ Failed. Server may not support role icons.")

    # ❗ ERROR HANDLER
    @role.error
    @roleicon.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send(f"⚠️ Error: {error}")

async def setup(bot):
    await bot.add_cog(Role(bot))
