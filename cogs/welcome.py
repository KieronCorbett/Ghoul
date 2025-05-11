import discord
from discord.ext import commands
from datetime import datetime

# Welcomes New Members To The Server
# This cog sends a welcome message to a specific channel when a new member joins the server.
# The message includes a thank you note, links to rules, self-roles, main lounge, and introductions.
# It also includes an embedded image and a footer with the current date and time.

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name='☁︱𝑾-𝑬-𝑳-𝑪-𝑶-𝑴-𝑬')
        if channel is None:
            return

        embed = discord.Embed(
            title="**__Welcome Our New Quest __**\n",
            description=(
                f"**Thank you [** {member.mention} **], We appreciate you choosing to join [ ッ ] Rejected, Have a fun time here!**\n\n"
                "**__Check out these:__**\n\n"
                "<:zz_snd:1369432476220653588> | **Intro:** <#1368704463514239116>\n"
                "<:zz_chat:1369432470583382037> | **Lounge:** <#1368672271161622568>\n"
                "<:rules:1369432447854448750> | **Roles:** <#1368681163979362354>\n"
                "<:profile:1369432441810456677> | **Rules:** <#1368679472081010838>"
            ),
            color=discord.Color.from_str("#ff0000") 
        )

        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_image(url="attachment://welcome.gif")
        embed.set_footer(
            text=f"Zero's Services • {datetime.utcnow().strftime('%d.%m.%Y %H:%M UTC')}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
        )

        file = discord.File("assets/welcome.gif", filename="welcome.gif")
        await channel.send(file=file, embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
