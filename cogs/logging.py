import discord
from discord.ext import commands
from datetime import datetime

LOG_CHANNEL_ID = 1368696126236262500

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, embed: discord.Embed):
        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} ({member}) joined the server.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Account Created", value=discord.utils.format_dt(member.created_at, style='F'))
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} ({member}) left the server.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if before.channel is None:
                action = f"joined voice channel {after.channel.mention}"
                color = 0x3498db
            elif after.channel is None:
                action = f"left voice channel {before.channel.mention}"
                color = 0xe67e22
            else:
                action = f"moved from {before.channel.mention} to {after.channel.mention}"
                color = 0x9b59b6

            embed = discord.Embed(
                title="Voice Channel Update",
                description=f"{member.mention} {action}.",
                color=color,
                timestamp=datetime.utcnow()
            )
            await self.send_log(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="Message Deleted",
            description=f"Message by {message.author.mention} deleted in {message.channel.mention}.",
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Content", value=message.content or "*No text content*", inline=False)
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="Message Edited",
            description=f"Message by {before.author.mention} edited in {before.channel.mention}.",
            color=0xf1c40f,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Before", value=before.content or "*No text*", inline=False)
        embed.add_field(name="After", value=after.content or "*No text*", inline=False)
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                action = "Timed Out"
                color = 0xffa500
                value = discord.utils.format_dt(after.timed_out_until, style='F')
            else:
                action = "Timeout Removed"
                color = 0x2ecc71
                value = "Timeout ended or removed."

            embed = discord.Embed(
                title=action,
                description=f"{after.mention}",
                color=color,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Until", value=value)
            await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(
            title="Member Banned",
            description=f"{user.mention} ({user}) was banned.",
            color=0x992d22,
            timestamp=datetime.utcnow()
        )
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(
            title="Member Unbanned",
            description=f"{user.mention} ({user}) was unbanned.",
            color=0x27ae60,
            timestamp=datetime.utcnow()
        )
        await self.send_log(embed)

    @commands.Cog.listener()
    async def on_member_kick(self, guild, user):
        embed = discord.Embed(
            title="Member Kicked",
            description=f"{user.mention} ({user}) was kicked from the server.",
            color=0xd35400,
            timestamp=datetime.utcnow()
        )
        await self.send_log(embed)

async def setup(bot):
    await bot.add_cog(Logging(bot))
