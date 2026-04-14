import discord
from discord.ext import commands

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🔁 ROLE TOGGLE COMMAND
    @commands.command(name="role")
    async def role(self, ctx, member: discord.Member = None, *, role_name: str = None):
        """
        Usage: !role @user RoleName
        """

        if member is None or role_name is None:
            return await ctx.send("❌ Usage: !role @user <role name>")

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


    # 🎭 ROLE ICON COMMAND (ONLY ICON)
    @commands.command(name="roleicon")
    async def roleicon(self, ctx, role: discord.Role = None, emoji: str = None):
        """
        Usage:
        !roleicon @role 😎
        !roleicon @role <:emoji:123>
        """

        if role is None or emoji is None:
            return await ctx.send("❌ Usage: !roleicon @role <emoji>")

        try:
            # 🎭 Unicode emoji
            if len(emoji) <= 4:
                await role.edit(display_icon=emoji.encode("utf-8"))

            # 🔥 Custom emoji
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


async def setup(bot):
    await bot.add_cog(Role(bot))
