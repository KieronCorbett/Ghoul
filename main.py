import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Load .env variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

# Bot Setup
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

    from cogs.ticket import TicketDropdownView
    bot.add_view(TicketDropdownView())

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            extension = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"🔹 Loaded extension: {extension}")
            except Exception as e:
                print(f"❌ Failed to load {extension}: {e}")

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        await bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"✅ Loaded `{extension}`.")
    except Exception as e:
        await ctx.send(f"❌ Failed to load `{extension}`: {e}")

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"✅ Unloaded `{extension}`.")
    except Exception as e:
        await ctx.send(f"❌ Failed to unload `{extension}`: {e}")

async def main():
    await load_extensions()
    await bot.start(BOT_TOKEN)

asyncio.run(main())