# import discord
# from discord.ext import commands
# import logging
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Enable logging
# logging.basicConfig(level=logging.INFO)

# # Get configuration from environment variables
# USER_TOKEN = os.getenv("DISCORD_TOKEN")
# YOUR_USER_ID = int(os.getenv("DISCORD_USER_ID"))

# intents = discord.Intents.default()
# intents.members = True  # Required for join events

# bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)

# @bot.event
# async def on_ready():
#     logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

# @bot.event
# async def on_member_join(member):
#     try:
#         you = await bot.fetch_user(YOUR_USER_ID)
#         await you.send(f" New member joined: {member.name} ({member.id})")
#     except Exception as e:
#         logging.error(f"Error sending DM: {e}")

# bot.run(USER_TOKEN)


import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

USER_TOKEN = os.getenv("DISCORD_TOKEN")

if not USER_TOKEN:
    raise RuntimeError("No token found in DISCORD_TOKEN")

# Explicit user agent for self-bots
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

bot = commands.Bot(
    command_prefix="!",
    self_bot=True,
    connector_kwargs={"headers": headers}
)

@bot.event
async def on_connect():
    print("Connected to Discord...")

@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

try:
    bot.run(USER_TOKEN, reconnect=True)
except discord.LoginFailure:
    print("""
    Failed to login. Possible reasons:
    1. Token is invalid/revoked
    2. Account has 2FA but token doesn't start with 'mfa.'
    3. Discord is blocking self-bots from your IP
    """)