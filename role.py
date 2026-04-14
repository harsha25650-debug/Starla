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
                await ctx.send(f"❌ Role `{role.name}` removed from {member.mention} successfully ✔️")
            else:
                await member.add_roles(role)
                await ctx.send(f"✅ Role `{role.name}` added to {member.mention} successfully ✔️")

        except discord.Forbidden:
            await ctx.send("⛔ I don't have permission to manage this role.")

        except Exception:
            await ctx.send("⚠️ Unexpected error occurred.")


    # 🎭 ROLE ICON COMMAND
    @commands.command(name="roleicon")
    async def roleicon(self, ctx, role_name: str = None, emoji: str = None):
        """
        Usage: !roleicon RoleName 😎
        """

        if role_name is None or emoji is None:
            return await ctx.send("❌ Usage: !roleicon <role name> <emoji>")

        role = discord.utils.get(ctx.guild.roles, name=role_name)

        if role is None:
            return await ctx.send(f"❌ Role `{role_name}` not found.")

        try:
            # emoji unicode ko bytes me convert
            await role.edit(display_icon=emoji.encode("utf-8"))

            await ctx.send(f"✨ Icon for role `{role.name}` updated successfully ✔️")

        except discord.Forbidden:
            await ctx.send("⛔ I don't have permission to edit this role.")

        except Exception:
            await ctx.send("⚠️ Failed to set role icon. Server may not support this feature.")


async def setup(bot):
    await bot.add_cog(Role(bot))
