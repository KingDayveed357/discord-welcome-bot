import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)

# Get configuration from environment variables
USER_TOKEN = os.getenv("DISCORD_TOKEN")
YOUR_USER_ID = int(os.getenv("DISCORD_USER_ID"))

intents = discord.Intents.default()
intents.members = True  # Required for join events

bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_member_join(member):
    try:
        you = await bot.fetch_user(YOUR_USER_ID)
        await you.send(f"🚨 New member joined: {member.name} ({member.id})")
    except Exception as e:
        logging.error(f"Error sending DM: {e}")

bot.run(USER_TOKEN)