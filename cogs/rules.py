import discord
from discord.ext import commands
from datetime import datetime

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="postrules")
    @commands.has_permissions(administrator=True)
    async def postrules(self, ctx):
        embed = discord.Embed(
            title="**__Community Rules!__**",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )

        embed.description = (
            "Welcome to the community! Please follow these rules to help keep the server safe and enjoyable for everyone:\n\n"
            "1. **Respect Everyone** – Treat all members with kindness. No hate speech, racism, sexism, or discrimination of any kind.\n"
            "2. **No Spamming** – Avoid flooding chat with repeated messages, emojis, or excessive mentions.\n"
            "3. **Keep Channels Relevant** – Use channels for their intended purpose. Off-topic content will be removed.\n"
            "4. **No Advertising** – Self-promotion, invite links, or unsolicited DMs are not allowed without staff approval.\n"
            "5. **Appropriate Content Only** – Keep all discussions and media safe-for-work. NSFW content is strictly prohibited.\n"
            "6. **No Cheating or Exploits** – Glitching, hacking, or any unfair behavior in bots, games, or giveaways is forbidden.\n"
            "7. **Follow Discord TOS** – All members must follow the official [Discord Terms of Service](https://discord.com/terms).\n"
            "8. **Listen to Staff** – Staff decisions are final. If you have concerns, bring them up respectfully in DMs or support tickets.\n\n"
            "By participating in this server, you agree to follow these rules. Violations may result in warnings, mutes, kicks, or bans."
        )

        embed.set_footer(text="Zero's Services", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @postrules.error
    async def postrules_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        else:
            await ctx.send("An error occurred while posting the rules.")
            print(f"Error in !postrules: {error}")

async def setup(bot):
    await bot.add_cog(Rules(bot))