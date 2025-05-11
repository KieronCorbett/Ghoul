import discord
from discord.ext import commands
from discord import app_commands
import random
from utils import xp_manager

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.profiles = xp_manager.load_profiles()  # Load profiles once at startup
        self.cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        
        # Cooldown check (10 seconds per user)
        if self.is_on_cooldown(user_id):
            return

        self.update_cooldown(user_id)

        # Get user's profile
        profile = xp_manager.get_user_profile(self.profiles, user_id)
        
        # Calculate XP gain (random 10-25 XP, doubled with booster role, +5 for server boosts)
        xp_gain = self.calculate_xp_gain(message.author)
        profile["xp"] += xp_gain
        
        # Check for level-up
        await self.check_level_up(message, profile)

    def is_on_cooldown(self, user_id):
        return user_id in self.cooldowns and self.cooldowns[user_id] > discord.utils.utcnow().timestamp()

    def update_cooldown(self, user_id):
        self.cooldowns[user_id] = discord.utils.utcnow().timestamp() + 10  # 10 seconds cooldown

    def calculate_xp_gain(self, member):
        xp_gain = random.randint(10, 25)
        if self.has_booster_role(member):
            xp_gain += 5  # Extra XP for server boosters
        return xp_gain

    def has_booster_role(self, member):
        """Check if user has server booster role"""
        return member.premium_since is not None  # Check if they boosted the server

    async def check_level_up(self, message, profile):
        next_level_xp = self.xp_required(profile["level"])
        if profile["xp"] >= next_level_xp:
            profile["xp"] -= next_level_xp
            profile["level"] += 1
            
            # Level-up message
            channel = self.bot.get_channel(1369726304743591966)  # Leveling channel
            await channel.send(f"🎉 {message.author.mention} leveled up to level {profile['level']}!")
            
            # Assign role if necessary (every 5 levels)
            if profile["level"] % 5 == 0:
                await self.create_and_assign_level_role(message.author, profile["level"])

            # Dispatch custom level-up event (for logging, etc.)
            await self.bot.dispatch("user_level_up", message.author, profile["level"])

        xp_manager.save_profiles(self.profiles)

    def xp_required(self, level):
        """Formula for XP required per level (increasing difficulty)"""
        return 5 * (level ** 2) + 50 * level + 100 + (level ** 2) * 10  # Harder XP curve after each level
    
    async def create_and_assign_level_role(self, member, level):
        """Automatically create and assign a role every 5 levels"""
        role_name = f"Level {level}"
        
        # Check if the role already exists
        role = discord.utils.get(member.guild.roles, name=role_name)
        if not role:
            # Create a new role with a color based on the level (using a gradient)
            role_color = discord.Color.from_hsv(level / 100, 1.0, 1.0)
            role = await member.guild.create_role(name=role_name, color=role_color)
            await member.send(f"🎉 You've unlocked the **{role_name}** role!")
        
        # Add the role to the member
        await member.add_roles(role)
        
        # Optionally, mention the role in the leveling channel
        channel = self.bot.get_channel(1369726304743591966)  # Leveling channel
        await channel.send(f"{member.mention} unlocked the **{role_name}** role!")

    @app_commands.command(name="addxp", description="Add XP to a user (admins only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The member to add XP to", amount="Amount of XP to add (1-1000)")
    async def addxp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount < 1 or amount > 1000:
            await interaction.response.send_message("🔴 Amount must be between 1 and 1000.", ephemeral=True)
            return

        profile = xp_manager.get_user_profile(self.profiles, user.id)
        profile["xp"] += amount
        
        # Check for level-up
        await self.check_level_up(interaction, profile)

        xp_manager.save_profiles(self.profiles)
        await interaction.response.send_message(f"✅ Added {amount} XP to {user.mention}. New total: {profile['xp']} XP.")

    @app_commands.command(name="removexp", description="Remove XP from a user (admins only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The member to remove XP from", amount="Amount of XP to remove (1-100)")
    async def removexp(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("🔴 Amount must be between 1 and 100.", ephemeral=True)
            return

        profile = xp_manager.get_user_profile(self.profiles, user.id)
        profile["xp"] = max(profile["xp"] - amount, 0)  # Prevent negative XP
        
        # Check for level-down
        next_level_xp = self.xp_required(profile["level"])
        if profile["xp"] < next_level_xp:
            profile["level"] -= 1

        xp_manager.save_profiles(self.profiles)
        await interaction.response.send_message(f"✅ Removed {amount} XP from {user.mention}. New total: {profile['xp']} XP.")

    @app_commands.command(name="resetxp", description="Reset a user's XP and level (admins only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The member to reset XP for")
    async def resetxp(self, interaction: discord.Interaction, user: discord.Member):
        profile = xp_manager.get_user_profile(self.profiles, user.id)
        profile["xp"] = 0
        profile["level"] = 1  # Reset to default level
        xp_manager.save_profiles(self.profiles)

        await interaction.response.send_message(f"✅ Reset XP and level for {user.mention}: now Level {profile['level']} with {profile['xp']} XP.")

async def setup(bot):
    await bot.add_cog(Leveling(bot))