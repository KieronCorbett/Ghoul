import discord
from discord.ext import commands
import asyncio

class PurgeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)  # 15-second cooldown per user
    async def purge(self, ctx, amount: int):
        # Ensure the amount is between 1 and 100
        if amount < 1 or amount > 100:
            await ctx.send("Please specify a number between 1 and 100.")
            return

        # Delete messages
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.commandOnCooldown):
            await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.", delete_after=5)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permissions to use this command.", delete_after=5)
        else:
            await ctx.send(f"An error occurred: {error}", delete_after=5)

async def setup(bot):
    await bot.add_cog(PurgeBot(bot))