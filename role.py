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

    # 🔁 ROLE TOGGLE (PREFIX + SLASH)
    @commands.hybrid_command(name="role", description="Add or remove a role")
    @app_commands.describe(member="Target user", role_name="Role name")
    @has_perm_or_owner()
    async def role(self, ctx, member: discord.Member, *, role_name: str):

        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is None:
            return await ctx.send(f"❌ Role `{role_name}` not found.")

        try:
            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"❌ Role `{role.name}` removed from {member.mention} ✔️")
            else:
                await member.add_roles(role)
                await ctx.send(f"✅ Role `{role.name}` added to {member.mention} ✔️")

        except discord.Forbidden:
            await ctx.send("⛔ I don't have permission to manage this role.")

        except Exception:
            await ctx.send("⚠️ Unexpected error occurred.")

    # 🎭 ROLE ICON (PREFIX + SLASH)
    @commands.hybrid_command(name="roleicon", description="Set role icon")
    @app_commands.describe(role="Target role", emoji="Emoji or custom emoji")
    @has_perm_or_owner()
    async def roleicon(self, ctx, role: discord.Role, emoji: str):

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

        except Exception:
            await ctx.send("⚠️ Failed. Server may not support role icons.")

    # ❗ ERROR HANDLER
    @role.error
    @roleicon.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")
        else:
            await ctx.send("⚠️ Error occurred.")

async def setup(bot):
    await bot.add_cog(Role(bot))
