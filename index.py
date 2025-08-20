import discord
from discord.ext import commands, tasks
import logging
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import asyncio

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

# Bot setup with minimal intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    self_bot=False,
    intents=intents
)

# Storage for tracking
member_cache = {}  # {guild_id: {member_id: last_seen}}
tracked_servers = set()  # Server IDs to monitor
last_checked = datetime.now(timezone.utc)

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    await initialize_member_cache()
    member_checker.start()

@tasks.loop(minutes=5)
async def member_checker():
    """Periodically check for new members"""
    global last_checked
    
    try:
        now = datetime.now(timezone.utc)
        for guild_id in list(tracked_servers):
            guild = bot.get_guild(guild_id)
            if not guild:
                continue
                
            try:
                # Get members through alternative means
                members = await get_members_stealthily(guild)
                current_members = {m.id for m in members}
                
                # Compare with cache
                new_members = current_members - set(member_cache.get(guild_id, {}).keys())
                
                for member_id in new_members:
                    member = guild.get_member(member_id)
                    if member:
                        await process_new_member(member)
                
                # Update cache
                member_cache[guild_id] = {m.id: now for m in members}
                
            except Exception as e:
                logging.error(f"Error checking guild {guild_id}: {e}")
        
        last_checked = now
        
    except Exception as e:
        logging.error(f"Member checker error: {e}")

async def get_members_stealthily(guild):
    """Alternative methods to get member list without permissions"""
    members = set()
    
    # Method 1: Check recent messages
    for channel in guild.text_channels:
        try:
            async for message in channel.history(limit=20):
                if message.author not in members:
                    members.add(message.author)
        except:
            continue
    
    # Method 2: Check voice channels
    for voice_channel in guild.voice_channels:
        for member in voice_channel.members:
            if member not in members:
                members.add(member)
    
    # Method 3: Check reactions in recent messages
    for channel in guild.text_channels:
        try:
            async for message in channel.history(limit=10):
                for reaction in message.reactions:
                    async for user in reaction.users():
                        if isinstance(user, discord.Member) and user not in members:
                            members.add(user)
        except:
            continue
    
    return members

async def process_new_member(member):
    """Handle new member detection"""
    try:
        account_age = (datetime.now(timezone.utc) - member.created_at).days
        age_info = f"{account_age} day{'s' if account_age != 1 else ''} old"
        
        if account_age < 7:
            age_info += " ⚠️ New account"
        
        # Try to send DM to the configured user
        user = await bot.fetch_user(YOUR_USER_ID)
        
        embed = discord.Embed(
            title="🚨 Possible New Member Detected",
            color=discord.Color.orange(),
            description=f"Detected through activity in {member.guild.name}",
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Username", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="Account Created", value=f"{member.created_at.strftime('%Y-%m-%d')}\n({age_info})", inline=True)
        embed.set_footer(text=f"User ID: {member.id} | Server: {member.guild.id}")
        
        await user.send(embed=embed)
        logging.info(f"Sent notification about {member} in {member.guild.name}")
        
    except Exception as e:
        logging.error(f"Failed to process new member: {e}")

async def initialize_member_cache():
    """Build initial member cache"""
    for guild in bot.guilds:
        try:
            members = await get_members_stealthily(guild)
            member_cache[guild.id] = {m.id: datetime.now(timezone.utc) for m in members}
        except Exception as e:
            logging.error(f"Failed to initialize cache for {guild.id}: {e}")

@bot.command()
async def track(ctx, server_id: int = None):
    """Start tracking a server"""
    target_id = server_id or ctx.guild.id
    tracked_servers.add(target_id)
    await ctx.send(f"✅ Now tracking server ID: {target_id}")

@bot.command()
async def untrack(ctx, server_id: int = None):
    """Stop tracking a server"""
    target_id = server_id or ctx.guild.id
    tracked_servers.discard(target_id)
    await ctx.send(f"❌ Stopped tracking server ID: {target_id}")

@bot.command()
async def list_tracked(ctx):
    """Show currently tracked servers"""
    if not tracked_servers:
        await ctx.send("Not tracking any servers")
        return
    
    msg = "Tracked servers:\n" + "\n".join(
        f"- {bot.get_guild(gid).name if bot.get_guild(gid) else f'Unknown ({gid})'}"
        for gid in tracked_servers
    )
    await ctx.send(msg[:2000])  # Discord message limit

try:
    bot.run(USER_TOKEN)
except Exception as e:
    logging.error(f"Bot crashed: {e}")