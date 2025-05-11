import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not before.premium_since and after.premium_since:
            await self.send_boost_embed(after)

    async def send_boost_embed(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='☁︱𝖡𝗈𝗈𝗌𝗍𝗂𝗇𝗀')
        if channel is None:
            return

        embed = discord.Embed(
            title="<a:0boost:1368948144120926258>  **__SERVER BOOSTER__** <a:0boost:1368948144120926258> \n",
            description=(
                f"**{member.mention} just boosted the server! Please open a ticket to find out about the extra perks we have to offer!**\n\n"
                "<:11_Mod_Book_Golden:1369638611267620874> **Ticket:** <#1368699203504574554>\n"
            ),
            color=discord.Color.from_str("#ff0000") 
        )                               

        embed.set_author(name=str(member), icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(
            text=f"Zero's Services • {datetime.utcnow().strftime('%d.%m.%Y %H:%M UTC')}",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url
        )

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Boost(bot))