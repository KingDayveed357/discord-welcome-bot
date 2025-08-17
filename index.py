import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get configuration
USER_TOKEN = os.getenv("DISCORD_TOKEN")
YOUR_USER_ID = int(os.getenv("DISCORD_USER_ID"))

if not USER_TOKEN:
    logging.error("Missing DISCORD_TOKEN in .env")
    exit(1)

if not YOUR_USER_ID:
    logging.error("Missing DISCORD_USER_ID in .env")
    exit(1)

# Selfbot setup - NOTE: Intents are handled differently in discord-py-self
bot = commands.Bot(
    command_prefix="!",
    self_bot=True,
    connector_kwargs={
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }
)

@bot.event
async def on_connect():
    logging.info("Connected to Discord")

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        target = await bot.fetch_user(YOUR_USER_ID)
        await target.send(
            f"🚨 New member in {member.guild.name}:\n"
            f"• Name: {member}\n"
            f"• ID: {member.id}\n"
            f"• Created: {member.created_at}"
        )
    except Exception as e:
        logging.error(f"Notification failed: {e}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

try:
    bot.run(USER_TOKEN)
except Exception as e:
    logging.error(f"Bot crashed: {e}")


# import discord
# from discord.ext import commands
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# USER_TOKEN = os.getenv("DISCORD_TOKEN")

# if not USER_TOKEN:
#     raise RuntimeError("No token found in DISCORD_TOKEN")

# # Explicit user agent for self-bots
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
# }

# bot = commands.Bot(
#     command_prefix="!",
#     self_bot=True,
#     connector_kwargs={"headers": headers}
# )

# @bot.event
# async def on_connect():
#     print("Connected to Discord...")

# @bot.event
# async def on_ready():
#     print(f"Successfully logged in as {bot.user}")

# @bot.command()
# async def ping(ctx):
#     await ctx.send("Pong!")

# try:
#     bot.run(USER_TOKEN, reconnect=True)
# except discord.LoginFailure:
#     print("""
#     Failed to login. Possible reasons:
#     1. Token is invalid/revoked
#     2. Account has 2FA but token doesn't start with 'mfa.'
#     3. Discord is blocking self-bots from your IP
#     """)