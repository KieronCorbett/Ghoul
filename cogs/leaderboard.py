import discord
from discord.ext import commands
from discord import app_commands
import json
from datetime import datetime

CROWN_EMOJIS = {
    1: "<:GoldCrown:1369638600647376947>",
    2: "<:SilverCrown:1369638603147186177>",
    3: "<:BronzeCrown:1369638606016348170>",
}

class LeaderboardView(discord.ui.View):
    def __init__(self, cog, user: discord.User):
        super().__init__(timeout=60)
        self.cog = cog
        self.author = user

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.success)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the person who used the command can refresh it.", ephemeral=True)
            return

        # Reload and rebuild embed
        self.cog.profiles = self.cog.load_profiles()
        embed = await self.cog.create_leaderboard_embed()
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.defer()

class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.profiles = self.load_profiles()

    def load_profiles(self):
        try:
            with open("xp_profiles.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    async def create_leaderboard_embed(self) -> discord.Embed:
        sorted_profiles = sorted(self.profiles.items(), key=lambda x: x[1].get("level", 0), reverse=True)
        top_10 = sorted_profiles[:10]

        embed = discord.Embed(
            title="**__Rejected's Community Leaderboard!__**",
            description="**__Top 10 Members__**\n",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )

        # Server thumbnail
        guild_icon = self.bot.guilds[0].icon
        if guild_icon:
            embed.set_thumbnail(url=guild_icon.url)

        # Footer
        embed.set_footer(text="Zero's Services", icon_url=self.bot.user.display_avatar.url)

        for idx, (user_id, data) in enumerate(top_10, start=1):
            user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
            if not user:
                continue

            level = data.get("level", 1)
            xp = data.get("xp", 0)
            rank = CROWN_EMOJIS.get(idx, f"**{idx}.**")
            embed.description += (
                f"> {rank} **{user.name}** Level: **{level}** | XP: **{xp}**\n"
                f"> ____________________________________________________________________________________________\n"
            )

        if not top_10:
            embed.description = "No users to display."

        return embed

    @app_commands.command(name="leaderboard", description="Display the server's leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        embed = await self.create_leaderboard_embed()
        view = LeaderboardView(self, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @leaderboard.error
    async def leaderboard_error(self, interaction: discord.Interaction, error: Exception):
        print(f"Error during leaderboard command: {error}")
        await interaction.response.send_message("An error occurred while fetching the leaderboard.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))