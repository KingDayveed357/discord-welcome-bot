import discord
from discord.ext import commands
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# !! REPLACE THESE !!
USER_TOKEN = "MTM1OTlyNzY5MjU30DUwODg4MQ.G4Y8lf.7dwTADUUOSQ6py0hotgAaptVw2Lpl27iR8fdLc"  # From DevTools
YOUR_USER_ID = 1359227692578508881      # Your Discord ID (right-click profile → Copy ID)

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