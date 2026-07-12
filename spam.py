import discord
from discord.ext import commands
import asyncio

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_spam = {}
        
        # ✨ STARLA CUSTOM EMOJIS INTEGRATION
        self.dot_pink = "<:topggDotPink:1525756454345375764>"
        self.dot_black = "<:starlaDotBlack:1525756435089063948>"
        self.arrow = "<:starlalyf_arrowglow:1525757297475850320>"
        
        self.yes = "<:starla_opt_yes:1525757001664299102>"
        self.no = "<:starla_opt_no:1525756996886986885>"
        self.cross = "<:starlacross:1525756266604007464>"

    def get_access(self, guild_id):
        return self.bot.db.get(f"spaccess.{guild_id}", [])

    def add_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id not in users:
            users.append(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    def remove_access(self, guild_id, user_id):
        users = self.get_access(guild_id)
        if user_id in users:
            users.remove(user_id)
            self.bot.db.set(f"spaccess.{guild_id}", users)

    async def has_access(self, ctx):
        if await self.bot.is_owner(ctx.author):
            return True
        if ctx.guild:
            users = self.get_access(ctx.guild.id)
            return ctx.author.id in users
        return False

    @commands.command(name="spaccess", description="Grant spam command access to a user (Owner Only)")
    @commands.is_owner()
    async def spaccess(self, ctx, member: discord.User):
        if not ctx.guild:
            return await ctx.send(f"{self.cross} This command can only be executed within a server.")
        self.add_access(ctx.guild.id, member.id)
        await ctx.send(f"{self.yes} Access granted successfully to {member.mention}")

    @commands.command(name="spremove", description="Revoke spam command access from a user (Owner Only)")
    @commands.is_owner()
    async def spremove(self, ctx, member: discord.User):
        if not ctx.guild:
            return await ctx.send(f"{self.cross} This command can only be executed within a server.")
        self.remove_access(ctx.guild.id, member.id)
        await ctx.send(f"{self.cross} Access revoked successfully from {member.mention}")

    @commands.command(name="spam", description="Spam a specific message in batches")
    async def spam(self, ctx, *, args=None):
        if not await self.has_access(ctx):
            return await ctx.send(f"{self.no} **Access Denied:** You don't have authorization parameters.")

        if not args:
            return await ctx.send(f"{self.cross} **Usage Error:** `{ctx.prefix}spam <message> <amount>`")

        try:
            # Splits right side se taaki multi-word message block clean rahe
            parts = args.rsplit(" ", 1)
            message = parts[0]
            amount = int(parts[1])
        except Exception:
            return await ctx.send(f"{self.cross} **Format Error:** Use `{ctx.prefix}spam hello 10` or `{ctx.prefix}spam test message 5`")

        if amount <= 0:
            return await ctx.send(f"{self.cross} **Value Error:** Amount parameter must be greater than 0.")

        amount = min(amount, 300)
        channel_id = ctx.channel.id

        if self.active_spam.get(channel_id):
            return await ctx.send(f"{self.cross} A frequency loop sequence is already running in this channel node.")

        self.active_spam[channel_id] = True

        try:
            await ctx.message.delete()
        except Exception:
            pass

        sent = 0
        batch_size = 3

        while sent < amount:
            if not self.active_spam.get(channel_id):
                break

            try:
                remaining = amount - sent
                current = min(batch_size, remaining)

                msg = "\n".join([message] * current)
                await ctx.send(msg)

                sent += current
                await asyncio.sleep(1.1)

            except discord.HTTPException as e:
                if e.status == 429:
                    retry = getattr(e, "retry_after", 5)
                    await asyncio.sleep(retry + 1)
                else:
                    break
            except Exception:
                break

        self.active_spam.pop(channel_id, None)
        await ctx.send(f"{self.dot_pink} Batch execution sequence completed.")

    @commands.command(name="spstop", description="Stop any active spam operations in the channel")
    async def spstop(self, ctx):
        if not await self.has_access(ctx):
            return await ctx.send(f"{self.no} **Access Denied:** Unauthorized token signature.")

        try:
            await ctx.message.delete()
        except Exception:
            pass

        if self.active_spam.get(ctx.channel.id):
            self.active_spam[ctx.channel.id] = False
            await ctx.send(f"{self.yes} Background transmission sequence safely aborted.")
        else:
            await ctx.send(f"{self.dot_black} No background active loops detected within this channel context.")

    # ❗ RE-ENGINEERED ERROR HANDLER
    @spam.error
    @spstop.error
    @spaccess.error
    @spremove.error
    async def spam_error_handler(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send(f"{self.no} **Restricted:** Root developer privileges required.")
        else:
            await ctx.send(f"{self.cross} **An error occurred:** `{error}`")

async def setup(bot):
    await bot.add_cog(Spam(bot))
        
