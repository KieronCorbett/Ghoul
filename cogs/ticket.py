import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import io
import asyncio

TICKET_CATEGORY_ID = 1368698340220342303
LOG_CHANNEL_ID = 1370117705679638528
SUPPORT_ROLE_NAME = "Support"
TICKET_PANEL_CHANNEL_ID = 1368699203504574554  # Channel to post ticket panel

class CloseTicketButton(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        support_role = discord.utils.get(interaction.guild.roles, name=SUPPORT_ROLE_NAME)
        if support_role not in interaction.user.roles:
            await interaction.response.send_message("You do not have permission to close this ticket.", ephemeral=True)
            return

        await interaction.response.send_message("Closing ticket and saving transcript...", ephemeral=True)

        transcript = await self.generate_transcript(interaction.channel)
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        file = discord.File(io.StringIO(transcript), filename=f"transcript-{interaction.channel.name}.txt")

        embed = discord.Embed(
            title="Ticket Closed",
            description=f"Ticket {interaction.channel.name} closed by {interaction.user.mention}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Zero's Services", icon_url=interaction.client.user.display_avatar.url)
        await log_channel.send(embed=embed, file=file)

        await interaction.channel.send("This ticket will be deleted in 10 seconds.")
        await asyncio.sleep(10)
        await interaction.channel.delete()

    async def generate_transcript(self, channel):
        transcript = f"Transcript for {channel.name}\nGenerated on {datetime.utcnow().isoformat()} UTC\n\n"
        async for message in channel.history(limit=None, oldest_first=True):
            time = message.created_at.strftime("[%Y-%m-%d %H:%M UTC]")
            author = f"{message.author}"
            content = message.content
            transcript += f"{time} {author}: {content}\n"
        return transcript

class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Help", description="Need assistance or guidance?", emoji="❓"),
            discord.SelectOption(label="Concern", description="Report a problem or issue.", emoji="📢"),
            discord.SelectOption(label="Suggestions", description="Have ideas to improve?", emoji="💡"),
            discord.SelectOption(label="Booster Perks", description="Access your booster perks!", emoji="💎")
        ]
        super().__init__(
            placeholder="Choose a category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"  # ✅ This is required for persistent views
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = guild.get_channel(TICKET_CATEGORY_ID)
        support_role = discord.utils.get(guild.roles, name=SUPPORT_ROLE_NAME)

        existing = discord.utils.get(category.text_channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message("You already have a ticket open.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            reason="New ticket created"
        )

        embed = discord.Embed(
            title="__**Support + Help System**__",
            description=f"Thank you {user.mention} for opening a ticket. A staff member will be with you shortly.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name="HV's Ticket System", icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Zero's Services", icon_url=interaction.client.user.display_avatar.url)

        view = CloseTicketButton(user)
        await channel.send(content=f"{user.mention}", embed=embed, view=view)

        # Reset dropdown to default placeholder by deferring
        await interaction.response.defer(ephemeral=True, thinking=False)
        await interaction.followup.send(f"Your ticket has been created: {channel.mention}", ephemeral=True)

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_ticket_panel", description="Post the main ticket panel")
    async def setup_ticket_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="__**Support + Help System**__",
            description="If you require assistance, have a concern, or need help accessing perks — open a ticket using the dropdown below.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name="HV's Ticket System", icon_url=interaction.user.display_avatar.url)
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text="Zero's Services", icon_url=self.bot.user.display_avatar.url)
        embed.set_image(url="attachment://ticket.gif")

        view = TicketDropdownView()
        file = discord.File("assets/ticket.gif", filename="ticket.gif")

        ticket_channel = interaction.guild.get_channel(TICKET_PANEL_CHANNEL_ID)
        await ticket_channel.send(embed=embed, view=view, file=file)
        await interaction.response.send_message("Ticket panel sent to the designated channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ticket(bot))