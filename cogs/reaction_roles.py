import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "reaction_config.json"

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    config = json.load(f)
                    if "messages" not in config:
                        config["messages"] = {}
                    if "emoji_roles" not in config:
                        config["emoji_roles"] = {}
                    return config
                except json.JSONDecodeError:
                    print(f"Error loading {CONFIG_FILE}, creating a new one.")
                    return {"messages": {}, "emoji_roles": {}}
        else:
            print(f"{CONFIG_FILE} not found, creating a new one.")
            self.save_config()
            return {"messages": {}, "emoji_roles": {}}

    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    @commands.command(name="send_all_embeds")
    @commands.has_permissions(administrator=True)
    async def send_all_embeds(self, ctx):
        embeds = {
            "age": {
                "title": "What is your age?",
                "text": "Please select your age group:",
                "description": {
                    "🔞": "18+",  # replace with "<:eighteen:123456789012345678>": "18+",
                    "🧒": "17-"
                }
            },
            "gender": {
                "title": "What is your gender?",
                "text": "Please select your gender:",
                "description": {
                    "🧔": "Male",
                    "👩": "Female"
                }
            },
            "platform": {
                "title": "What do you game on?",
                "text": "Please select your platform:",
                "description": {
                    "🎮": "Console",
                    "💻": "PC",
                    "📱": "Mobile"
                }
            },
            "games": {
                "title": "What games do you play?",
                "text": "Please select your games:",
                "description": {
                    "🎯": "Call Of Duty",
                    "👹": "Dead By Daylight",
                    "🧱": "Minecraft",
                    "⚔️": "Overwatch",
                    "🤖": "Roblox",
                }
            },
            "pings": {
                "title": "What would you like to be updated on?",
                "text": "Please select your pings:",
                "description": {
                    "🤖": "Bot Updates",    
                    "🌟": "New Features",   
                    "📅": "Server Events",  
                    "📢": "Announcements",  
                }
            }
        }

        for key, embed_data in embeds.items():
            if key in self.config["messages"]:
                msg_id = self.config["messages"][key]
                msg = await ctx.fetch_message(msg_id)
                updated_desc = embed_data["text"] + "\n\n" + "\n".join(f"{emoji} - {role}" for emoji, role in embed_data["description"].items())
                await msg.edit(embed=discord.Embed(title=embed_data["title"], description=updated_desc, color=discord.Color.purple()))
            else:
                desc = embed_data["text"] + "\n\n" + "\n".join(f"{emoji} - {role}" for emoji, role in embed_data["description"].items())
                embed = discord.Embed(title=embed_data["title"], description=desc, color=discord.Color.from_str("#ff0000"))
                msg = await ctx.send(embed=embed)

                self.config["messages"][key] = msg.id
                self.config["emoji_roles"][str(msg.id)] = embed_data["description"]

                for emoji in embed_data["description"]:
                    await msg.add_reaction(emoji)

        self.save_config()
        await ctx.send("✅ All reaction role embeds sent and saved!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        msg_id = str(payload.message_id)
        if msg_id not in self.config["emoji_roles"]:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        emoji = str(payload.emoji)
        role_name = self.config["emoji_roles"][msg_id].get(emoji)
        if not role_name:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        msg_id = str(payload.message_id)
        if msg_id not in self.config["emoji_roles"]:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        emoji = str(payload.emoji)
        role_name = self.config["emoji_roles"][msg_id].get(emoji)
        if not role_name:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))