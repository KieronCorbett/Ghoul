import discord
from discord.ext import commands
from discord import app_commands
from utils import xp_manager
from PIL import Image, ImageDraw, ImageFont, ImageOps
import aiohttp
import io
import os

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profiles = xp_manager.load_profiles()

    async def fetch_image(self, url):
        print(f"Fetching image from {url}")  # Debug log
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"Failed to fetch image, status code {resp.status}")  # Debug log
                    return None
                print(f"Image fetched successfully.")  # Debug log
                return Image.open(io.BytesIO(await resp.read())).convert("RGBA")

    def draw_text_with_outline(self, draw, position, text, font, fill, outline_color="black", outline_width=2):
        x, y = position
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        draw.text(position, text, font=font, fill=fill)

    @app_commands.command(name="setbio", description="Set your profile bio")
    @app_commands.describe(text="Your new bio text")
    async def set_bio(self, interaction: discord.Interaction, text: str):
        profile = xp_manager.get_user_profile(self.profiles, interaction.user.id)
        profile["bio"] = text[:100]
        xp_manager.save_profiles(self.profiles)
        await interaction.response.send_message("✅ Bio updated!", ephemeral=True)

    @app_commands.command(name="setcolour", description="Set your profile theme color")
    @app_commands.describe(hex_code="Hex code of your profile color (e.g., #ff0000)")
    async def set_colour(self, interaction: discord.Interaction, hex_code: str):
        if not hex_code.startswith("#") or len(hex_code) != 7:
            await interaction.response.send_message("🔴 Invalid hex code. Use format like `#ff0000`.", ephemeral=True)
            return
        profile = xp_manager.get_user_profile(self.profiles, interaction.user.id)
        profile["color"] = hex_code
        xp_manager.save_profiles(self.profiles)
        await interaction.response.send_message(f"✅ Profile color updated to `{hex_code}`!", ephemeral=True)

    @app_commands.command(name="setbackground", description="Set your profile background image URL")
    @app_commands.describe(url="Link to your background image")
    async def set_background(self, interaction: discord.Interaction, url: str):
        if not url.startswith("http"):
            await interaction.response.send_message("🔴 Invalid URL. Must start with http/https.", ephemeral=True)
            return
        profile = xp_manager.get_user_profile(self.profiles, interaction.user.id)
        profile["background"] = url
        xp_manager.save_profiles(self.profiles)
        await interaction.response.send_message("✅ Background image updated!", ephemeral=True)

    @app_commands.command(name="profile", description="View your XP profile")
    async def profile(self, interaction: discord.Interaction):
        print("Profile command triggered.")  # Debug log
        await interaction.response.defer()

        user = interaction.user
        profile = xp_manager.get_user_profile(self.profiles, user.id)
        xp, level = profile["xp"], profile["level"]
        bio = profile["bio"]
        color = profile.get("color", "#00ff00")
        bg_url = profile.get("background")

        # Load background
        custom_bg_url = profile.get("background_url")
        if custom_bg_url:
            print(f"Loading custom background from URL: {custom_bg_url}")  # Debug log
            bg = await self.fetch_image(custom_bg_url)
            if bg:
                bg = bg.resize((800, 300))
            else:
                print("Using default background image.")  # Debug log
                bg = Image.open("assets/profile_background.png").convert("RGBA").resize((800, 300))
        else:
            print("Using default background image.")  # Debug log
            bg = Image.open("assets/profile_background.png").convert("RGBA").resize((800, 300))

        draw = ImageDraw.Draw(bg)
        font_big = ImageFont.truetype("/usr/share/fonts/chromeos/monotype/arialnb.ttf", 36)  # Bold
        font_small = ImageFont.truetype("/usr/share/fonts/chromeos/monotype/arialn.ttf", 22)  # Regular
        font_bar = ImageFont.truetype("/usr/share/fonts/chromeos/monotype/arialnb.ttf", 26)  # Bold

        # Username (bold, underlined, outlined)
        username_text = f"{user.name}"
        self.draw_text_with_outline(draw, (250, 20), username_text, font_big, fill="white")
        underline_width = draw.textlength(username_text, font=font_big)
        draw.line((250, 60, 250 + underline_width, 60), fill="white", width=2)

        # Avatar (circular)
        avatar = await self.fetch_image(user.display_avatar.url)
        avatar = avatar.resize((100, 100))
        mask = Image.new("L", avatar.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 100, 100), fill=255)
        avatar = ImageOps.fit(avatar, (100, 100), centering=(0.5, 0.5))
        avatar.putalpha(mask)
        bg.paste(avatar, (120, 100), avatar)

        # XP / Level (outlined)
        self.draw_text_with_outline(draw, (250, 100), f"Level: {level}", font_small, fill="white")
        self.draw_text_with_outline(draw, (250, 135), f"XP: {xp}", font_small, fill="white")

        # Progress bar
        bar_x, bar_y, bar_width, bar_height = 250, 180, 500, 30
        progress = min(xp / (5 * (level ** 2) + 50 * level + 100 + (level ** 2) * 10), 1)
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill="white", outline="black", width=2)
        draw.rectangle([bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height], fill="red")

        # Bio
        draw.text((250, 225), bio, font=font_small, fill="white")

        # Finalize
        buffer = io.BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        # Debug: Check image size
        print(f"Generated profile image size: {len(buffer.getvalue())} bytes.")

        file = discord.File(buffer, filename="profile.png")

        # Log: Confirm sending process
        print("Preparing to send profile image...")

        embed = discord.Embed(color=discord.Color.from_str(color))
        embed.set_image(url="attachment://profile.png")
        embed.set_footer(text="Zero's Services", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()

        # Log: Confirm sending the embed
        print("Sending profile image...")
        await interaction.followup.send(file=file, embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))