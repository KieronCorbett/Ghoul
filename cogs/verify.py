import discord
from discord.ext import commands

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_id = None  # Set this after posting

    @commands.command(name="postverify")
    @commands.has_permissions(administrator=True)
    async def postverify(self, ctx):
        embed = discord.Embed(
            title="**__Community Rules!__**",
            description=(
                "Please read the rules above.\n\n"
                "React with ✅ to acknowledge and gain access to the server."
            ),
            color=0xff0000
        )
        embed.set_footer(text="Zero's Services", icon_url=self.bot.user.display_avatar.url)

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")

        self.message_id = msg.id  # Save this if you want persistence across bot restarts

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != self.message_id:
            return
        if str(payload.emoji) != "✅":
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member is None or member.bot:
            return

        role = discord.utils.get(guild.roles, name="Verified")
        if role:
            await member.add_roles(role, reason="Acknowledged rules via reaction")

async def setup(bot):
    await bot.add_cog(Verify(bot))