import discord
from discord.ext import commands
from datetime import datetime

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name='☁︱𝖫𝖾𝖿𝗍')
        if channel is None:
            return

        embed = discord.Embed(
            title="**__Member Has Left__**\n",
            description=(
                f"{member.mention} **We hope to see you again someday!** <:51395bnhajirouheartlove:1369642841944358933>\n\n"
                "**Oh no! What will we do without you...**)"
            ),
            color=discord.Color.from_str("#ff0000")
        )

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(
            text=f"Zero's Services • {datetime.utcnow().strftime('%d.%m.%Y %H:%M UTC')}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
        )

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leave(bot))