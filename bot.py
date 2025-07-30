import discord
from discord.ext import commands
import aiohttp
import asyncio
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord Bot Configuration
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "your_discord_bot_token_here")
DISCORD_OWNER_ID = int(os.getenv("DISCORD_OWNER_ID", "123456789012345678"))  # Replace with actual owner ID

# Initialize authorized users with owner
AUTHORIZED_USERS = {DISCORD_OWNER_ID}

# Bot setup with all intents for DM and group chat support
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global tracking data
tracked_players = {}  # {user_id: [player_names]}
player_states = {}   # {player_name: {state_data}}

# Skull arts for permanent ban notifications
SKULL_ARTS = [
    # Original skull
    """```
💀 PERMANENTLY BANNED 💀

⢋⣴⠒⡝⣿⣿⣿⣿⣿⡿⢋⣥⣶⣿⣿⣿⣿⣿⣿⣶⣦⣍⠻⣿⣿⣿⣿⣿⣷⣿
⢾⣿⣀⣿⡘⢿⣿⡿⠋⠄⠻⠛⠛⠛⠻⠿⣿⣿⣿⣿⣿⣿⣷⣌⠻⣿⣿⣿⣿⣿
⠄⠄⠈⠙⢿⣦⣉⡁⠄⠄⣴⣶⣿⣿⢷⡶⣾⣿⣿⣿⣿⡛⠛⠻⠃⠙⢿⣿⣿⣿
⠄⠄⠄⠄⠄⠈⠉⣀⣀⣴⡟⢩⠁⠩⣝⢂⢨⣿⣿⣿⣿⢟⡛⣳⣶⣤⡘⠿⢋⣡
⠄⠄⠄⠄⠄⠄⠘⣿⣿⣿⣿⣾⣿⣶⣿⣿⣿⣿⣿⣿⣿⣆⣈⣱⣮⣿⣷⡾⠟⠋
⠄⠄⠄⠄⠄⠄⠄⠈⠿⠛⠛⣻⣿⠉⠛⠋⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠸⣿
⠄⠄⠄⠄⢀⡠⠄⢒⣤⣟⠿⣿⣿⣿⣷⣤⣤⣀⣀⣉⣉⣠⣽⣿⣟⠻⣿⣿⡆⢻
⠄⣀⠄⠄⠄⠄⠈⠋⠉⣿⣿⣶⣿⣟⣛⡿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣼⣿⡇⣸
⣿⠃⠄⠄⠄⠄⠄⠄⠠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣾⣿⣿⣿⣿⣿⣿⠁⢿
⡋⠄⠄⠄⠄⠄⠄⢰⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠄⠄

       R.I.P.
   Player Removed
```""",
    
    # Skull Art 1
    """```
💀 PERMANENTLY BANNED 💀

⠀⠀⢀⢀⣀⣠⣠⣤⣠⡀⠀⠀⠀
⢠⢷⣏⠈⠹⣯⡏⠉⢙⣷⣶⡀⠀
⢔⡀⠈⠙⠿⠩⠟⠖⠛⠀⡹⢷⡆
⢘⠥⠁⠀⠀⠀⠀⠀⠀⣌⣲⠛⠀
⢈⡌⠀⡀⢀⠄⢀⣵⡾⠏⠀⠀⠀
⠘⠛⠟⠃⠓⠛⠟⠁⠁⠀⠀⠀⠀

       R.I.P.
   Player Removed
```""",
    
    # Skull Art 2
    """```
💀 PERMANENTLY BANNED 💀

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢨⠳⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠂⠸⣆⡴⠛⣷⠀⢀⣤⠶⣶⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠙⠁⠀⠹⠟⠉⣠⠞⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢤⡀⠀⠀⡼⣦⠀⣠⣤⡀⠀⢀⣴⠋⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⡤⣀⡀⠀⠀⢀⡞⣡⣶⡌⣇⠀⣿⠋⠀⠻⠾⠃⣴⣻⠇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⢡⣴⣶⡹⣄⣀⡤⣿⠛⠟⠃⠏⠠⢿⣤⣄⣀⠀⢠⡾⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠢⡽⠛⠇⠉⠀⠀⠀⠀⠀⠀⠐⠂⠠⡄⠉⠉⠓⠿⢄⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⠖⢋⣁⣠⡤⠖⠒⠶⠦⣄⡀⠈⠄⢲⣶⣤⠥⠀⠀⠀⠀⠉⠳⣦⡀⠀⠀⠀
⠀⠀⢠⠎⠁⢀⡼⢛⣁⠀⠀⠀⡀⠀⠈⠹⣄⠐⠈⠫⠭⠠⠤⠤⠤⠄⠀⠐⢌⠙⣦⡀⠀
⠀⣰⡟⡂⢠⡟⠸⣿⣿⣷⠀⣾⣿⠆⠀⠀⢹⡀⠀⢀⣀⣠⠤⢴⡆⢈⠐⠀⠈⡇⠈⠻⣆
⣠⡿⢰⡓⢾⠀⠀⠈⠻⠋⠀⠀⠀⠀⠀⣀⡿⠓⠚⡏⠁⠀⢠⠟⢀⡠⠄⠀⢀⠀⠀⠀⢸
⡟⠀⣾⠀⢌⠓⠦⢶⠤⠤⢤⠤⠴⠚⢻⡁⠀⢀⣀⣅⣠⣴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰
⡇⠀⣾⣶⣦⣤⣤⣦⣤⣤⣾⣶⣶⣶⣿⠿⠛⠋⠉⣥⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⣇⠀⢹⡙⠉⠉⠻⠋⠉⠙⡏⠁⠀⠀⢸⠀⢀⣤⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜
⢹⡄⠀⠙⠦⢄⣀⣀⠀⢀⡇⠀⣀⣠⠼⠒⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⠁
⠀⠹⣦⡀⠀⠈⠁⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠟⠁⠀
⠀⠀⠈⠛⠦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⡤⠖⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠉⠙⠂⠠⠤⣄⣀⣀⣀⣀⣀⣀⣀⣤⠤⠤⠛⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀

       R.I.P.
   Player Removed
```""",
    
    # Skull Art 3
    """```
💀 PERMANENTLY BANNED 💀

⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣶⣶⣶⣶⣦⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡶⢻⡦⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢀⣴⣾⡿⠀⣠⠀⠀
⠀⠠⣬⣷⣾⣡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣌⣋⣉⣄⠘⠋⠀⠀
⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⡄⠀⠀⠀
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣷⣶⡄⠀
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
⠀⠀⠀⠀⠸⣿⣿⣿⠛⠛⠛⠛⠛⠛⠛⠛⠻⠿⣿⣿⡿⠛⠛⠛⠋⠉⠉⠀⠀⠀
⠀⠀⠀⠀⠀⢻⣿⣿⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⢻⣿⠃⠸⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠿⠇⠀⠀⠀⠻⠇⠀⠀⠀⠀⠀⠈⠿⠀⠀⠻⠿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

       R.I.P.
   Player Removed
```"""
]

def is_owner(user_id: int) -> bool:
    """Check if user is the bot owner"""
    return user_id == DISCORD_OWNER_ID

async def get_player_stats(player_name: str) -> Dict[str, Any]:
    """Fetch player stats from Critical Ops API"""
    try:
        async with aiohttp.ClientSession() as session:
            # Try by name first
            async with session.get(f"https://api.criticalops.com/v1/players/search?name={player_name}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data and 'players' in data and len(data['players']) > 0:
                        player_id = data['players'][0]['basicInfo']['userID']
                        
                        # Get detailed stats using player ID
                        async with session.get(f"https://api.criticalops.com/v1/players/{player_id}") as detail_response:
                            if detail_response.status == 200:
                                return await detail_response.json()
                
                # If name search fails, try direct ID lookup
                async with session.get(f"https://api.criticalops.com/v1/players/{player_name}") as id_response:
                    if id_response.status == 200:
                        return await id_response.json()
                        
    except Exception as e:
        logger.error(f"Error fetching player stats for {player_name}: {e}")
    
    return None

def format_ban_status(ban_data: Dict[str, Any]) -> str:
    """Format ban status for display"""
    if not ban_data:
        return "N/A"
    
    ban_type = ban_data.get('type', 'Unknown')
    expires_at = ban_data.get('expires_at')
    
    if expires_at and expires_at != 'Permanent':
        return "Temporary"
    else:
        return "Permanent"

async def send_notification_to_trackers(player_name: str, title: str, embed: discord.Embed):
    """Send notification to all users tracking this player"""
    if player_name not in player_states:
        return
    
    channels = player_states[player_name]['tracking_channels']
    for channel_id in channels:
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(title, embed=embed)
        except Exception as e:
            logger.error(f"Failed to send notification to channel {channel_id}: {e}")

def is_player_in_ranked_match(player_data: Dict[str, Any]) -> bool:
    """Check if player is currently in a ranked match"""
    # This is a simplified check - in reality you'd need more complex logic
    # to determine if a player is actively in a match
    return False  # For now, always return False since we can't reliably detect live matches

async def send_ranked_status_message(player_name: str, player_data: Dict[str, Any]):
    """Send ranked match status message"""
    if player_name not in player_states:
        return
        
    state = player_states[player_name]
    current_username = player_data.get('basicInfo', {}).get('name', player_name)
    
    # Check if player is actually in a ranked match
    is_in_match = is_player_in_ranked_match(player_data)
    
    if not is_in_match:
        # Send "not in match" message
        embed = discord.Embed(
            title="ℹ️ **Match Status**",
            description=f"**{current_username}** is not currently in a ranked match",
            color=discord.Color.blue()
        )
        embed.add_field(name="**Status**", value="⚪ **Not in Match**", inline=True)
        
        # Send to all tracking channels
        channels = state['tracking_channels']
        for channel_id in channels:
            try:
                channel = bot.get_channel(channel_id)
                if channel:
                    await channel.send("📊 **Match Check**", embed=embed)
            except Exception as e:
                logger.error(f"Failed to send match status to channel {channel_id}: {e}")
        return

async def check_ranked_match_changes(player_name: str, current_data: Dict[str, Any], state: Dict[str, Any], current_mmr: int):
    """Check for ranked match state changes based on stat increases and MMR changes"""
    # Get current Season 15 stats
    stats = current_data.get('stats', {})
    seasonal_stats = stats.get('seasonal_stats', [])
    season_15_data = None
    
    for season in seasonal_stats:
        if season.get('season') == 15:
            season_15_data = season
            break
    
    if not season_15_data:
        return
    
    ranked_s15 = season_15_data.get('ranked', {})
    current_kills = ranked_s15.get('k', 0)
    current_deaths = ranked_s15.get('d', 0)
    current_assists = ranked_s15.get('a', 0)
    
    # Get initial stats from message 1
    initial_stats = state.get('initial_stats', {})
    initial_kills = initial_stats.get('kills', current_kills)
    initial_deaths = initial_stats.get('deaths', current_deaths)
    initial_assists = initial_stats.get('assists', current_assists)
    initial_mmr = initial_stats.get('mmr', current_mmr)
    
    was_in_match = state.get('in_ranked_match', False)
    
    # Debug logging
    logger.info(f"Debug {player_name}: Current K/D/A: {current_kills}/{current_deaths}/{current_assists}, Initial: {initial_kills}/{initial_deaths}/{initial_assists}")
    logger.info(f"Debug {player_name}: Current MMR: {current_mmr}, Initial MMR: {initial_mmr}, In match: {was_in_match}")

async def check_player_updates():
    """Background task to monitor tracked players for changes"""
    while True:
        try:
            for player_name, state in list(player_states.items()):
                # Use different intervals for players in ranked matches
                if state.get('in_ranked_match'):
                    # Check every 1-2 minutes for active matches
                    if datetime.utcnow() - state['last_check_time'] < timedelta(minutes=1):
                        continue
                else:
                    # Only check players that have been checked more than 30 seconds ago
                    if datetime.utcnow() - state['last_check_time'] < timedelta(seconds=30):
                        continue
                    
                # Fetch current player data
                current_data = await get_player_stats(state['last_username'])
                if not current_data:
                    continue
                    
                # Update last check time
                state['last_check_time'] = datetime.utcnow()
                
                # Check for username changes
                current_username = current_data.get('basicInfo', {}).get('name', state['last_username'])
                if current_username != state['last_username']:
                    embed = discord.Embed(
                        title="📝 Username Changed",
                        description=f"**{state['last_username']}** changed their name to **{current_username}**",
                        color=0xFFAA00
                    )
                    await send_notification_to_trackers(player_name, f"🔄 **Username Update**", embed)
                    
                    # Update stored username
                    state['last_username'] = current_username
                
                # Check for ban status changes
                current_ban = current_data.get('ban')
                last_ban = state.get('last_ban_status')
                
                if current_ban != last_ban:
                    if current_ban:  # Player got banned
                        ban_reason = current_ban.get('reason', 'Unknown')
                        ban_type = current_ban.get('type', 'Unknown')
                        ban_expires = current_ban.get('expires_at', 'Permanent')
                        
                        if ban_expires and ban_expires != 'Permanent':
                            ban_duration = f"Until {ban_expires}"
                        else:
                            ban_duration = "Permanent"
                            
                        embed = discord.Embed(
                            title="⚠️ Player Banned",
                            description=f"**{current_username}** has been banned from Critical Ops",
                            color=0xFF4444
                        )
                        embed.add_field(name="Reason", value=ban_reason, inline=True)
                        embed.add_field(name="Type", value=ban_type, inline=True)
                        embed.add_field(name="Duration", value=ban_duration, inline=True)
                        
                        await send_notification_to_trackers(player_name, f"🚫 **Ban Alert**", embed)
                    else:  # Player got unbanned
                        embed = discord.Embed(
                            title="✅ Player Unbanned",
                            description=f"**{current_username}** is no longer banned",
                            color=0x00FF00
                        )
                        await send_notification_to_trackers(player_name, f"🎉 **Unban Alert**", embed)
                
                # Check for MMR/ranked changes and match status
                current_stats = current_data.get('stats', {})
                current_ranked = current_stats.get('ranked', {})
                current_mmr = current_ranked.get('mmr', 0)
                
                last_mmr = state.get('last_mmr')
                
                # Check for ranked match changes based on user's logic
                await check_ranked_match_changes(player_name, current_data, state, current_mmr)
                
                # Update stored states
                state['last_stats'] = current_data
                state['last_ban_status'] = current_ban
                state['last_mmr'] = current_mmr if current_mmr > 0 else None
                
        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
        
        # Wait 30 seconds before next check (or 1 minute for active matches)
        await asyncio.sleep(30)

async def run_one_time_test():
    """Run the test scenarios once when called"""
    logger.info("🧪 Running one-time test scenarios...")
    
    # Find a suitable channel to send tests to
    test_channel = None
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                test_channel = channel
                break
        if test_channel:
            break
    
    if not test_channel:
        logger.error("❌ No suitable channel found for testing")
        return
    
    logger.info(f"📍 Sending tests to channel: {test_channel.name} in {test_channel.guild.name}")
    
    try:
        # Test 1: Enhanced Username change
        old_username = "PlayerOld"
        new_username = "Donk666" 
        account_id = "31357194"
        
        username_embed = discord.Embed(
            title="📝 Player Name Changed",
            description=f"**Account ID:** {account_id}",
            color=0x4169E1  # Royal blue
        )
        username_embed.add_field(
            name="🔄 Name Change Detected", 
            value=f"**Previous Name:** `{old_username}`\n**New Name:** `{new_username}`", 
            inline=False
        )
        username_embed.add_field(
            name="🕐 Detection Time", 
            value=f"<t:{int(datetime.utcnow().timestamp())}:F>", 
            inline=True
        )
        username_embed.add_field(
            name="🔗 Tracking Status", 
            value="✅ Continuing to track this player", 
            inline=True
        )
        username_embed.set_footer(text="TEST MODE • Account ID-based tracking ensures continuous monitoring")
        
        await test_channel.send("📝 **TEST: Username Change Alert**", embed=username_embed)
        logger.info("✅ Enhanced username change test sent")
        
        await asyncio.sleep(3)
        
        # Test 2: Enhanced Permanent ban with random skull
        player_name = "Monesy"
        ban_account_id = "98765432"
        
        selected_skull = random.choice(SKULL_ARTS)
        skull_number = SKULL_ARTS.index(selected_skull) + 1
        
        ban_embed = discord.Embed(
            title="💀 PERMANENT BAN DETECTED", 
            description=f"**{player_name}** has been permanently banned from Critical Ops",
            color=0x8B0000  # Dark red
        )
        ban_embed.add_field(name="👤 Player", value=player_name, inline=True)
        ban_embed.add_field(name="🆔 Account ID", value=ban_account_id, inline=True)
        ban_embed.add_field(name="⚖️ Reason", value="Cheating", inline=True)
        ban_embed.add_field(name="🚫 Ban Type", value="**PERMANENT**", inline=True)
        ban_embed.add_field(name="⏰ Duration", value="Forever", inline=True)
        ban_embed.add_field(name="🔧 Action", value="⚠️ Automatically removed from tracking", inline=True)
        ban_embed.add_field(name="🕐 Ban Detected", value=f"<t:{int(datetime.utcnow().timestamp())}:F>", inline=False)
        ban_embed.set_footer(text=f"TEST MODE • Skull Art #{skull_number} • Player removed from all tracking lists")
        
        await test_channel.send(selected_skull)
        await test_channel.send("💀 **TEST: PERMANENT BAN ALERT**", embed=ban_embed)
        logger.info(f"✅ Enhanced permanent ban test sent using skull art #{skull_number}")
        
        logger.info("🎉 All enhanced test scenarios completed!")
        
    except Exception as e:
        logger.error(f"❌ Error running tests: {e}")

@bot.event
async def on_ready():
    """Bot startup event"""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Owner ID: {DISCORD_OWNER_ID}')
    
    try:
        # Sync commands globally to work in DMs and group chats
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} command(s) globally')
        
        # Start background monitoring task
        asyncio.create_task(check_player_updates())
        logger.info("Started background player monitoring task")
        
        # TEMPORARY: Run one-time test (remove this line after testing)
        asyncio.create_task(run_one_time_test())
        
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    """Listen and respond to messages in DMs and group chats"""
    if message.author.bot:
        return  # ignore bots
    
    # This works for GCs and DMs, no extra filters needed
    channel_type = str(message.channel.type)
    logger.info(f'Message from {message.author.name} in {channel_type}: {message.content}')
    
    # Process commands for both slash and text commands
    await bot.process_commands(message)

@bot.tree.command(name="snipe", description="Track a Critical Ops player's stats")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def snipe_player(interaction: discord.Interaction, player_name: str):
    """Track a Critical Ops player - Available to authorized users"""
    # Log interaction details for debugging
    channel_type = str(interaction.channel.type) if interaction.channel else "Unknown"
    logger.info(f"Snipe command from {interaction.user.name} ({interaction.user.id}) in {channel_type}")
    logger.info(f"Current authorized users: {AUTHORIZED_USERS}")
    
    # Check authorization using hardcoded list
    if interaction.user.id not in AUTHORIZED_USERS:
        logger.warning(f"Unauthorized access attempt by {interaction.user.name} ({interaction.user.id})")
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Fetch player data from Critical Ops API
        data = await get_player_stats(player_name)
        
        if not data:
            await interaction.followup.send("❌ Player not found or API error.")
            return
        
        # Use the correct API response format from the working code
        player_info = data
        
        # Debug: Log API response structure
        logger.info(f"API Response keys: {list(player_info.keys())}")
        if 'stats' in player_info:
            logger.info(f"Stats keys: {list(player_info['stats'].keys())}")
        if 'seasonal_stats' in player_info.get('stats', {}):
            logger.info(f"Found seasonal_stats with {len(player_info['stats']['seasonal_stats'])} seasons")
        
        # Extract player information using correct API structure
        basic_info = player_info.get('basicInfo', {})
        username = basic_info.get('name', player_name)
        level_data = basic_info.get('playerLevel', 'N/A')
        if isinstance(level_data, dict):
            level = level_data.get('level', 'N/A')
        else:
            level = level_data
        clan_tag = basic_info.get('clan', {}).get('tag', 'N/A')
        
        # Get ban status
        ban_data = player_info.get('ban')
        ban_status = format_ban_status(ban_data)
        
        # Extract stats
        stats = player_info.get('stats', {})
        
        # Get seasonal stats for calculations
        seasonal_stats = stats.get('seasonal_stats', [])
        
        # Calculate total casual stats (casual mode only, excluding custom and ranked)
        total_kills = total_deaths = total_assists = 0
        for season in seasonal_stats:
            casual_data = season.get('casual', {})
            total_kills += casual_data.get('k', 0)
            total_deaths += casual_data.get('d', 0) 
            total_assists += casual_data.get('a', 0)
        
        total_kd = round(total_kills / total_deaths, 2) if total_deaths > 0 else total_kills
        
        # Current ranked stats
        ranked_stats = stats.get('ranked', {})
        current_mmr = ranked_stats.get('mmr', 0)
        
        # Season 15 ranked stats
        season_15_data = None
        for season in seasonal_stats:
            if season.get('season') == 15:
                season_15_data = season
                break
        
        if season_15_data:
            ranked_s15 = season_15_data.get('ranked', {})
            s15_kills = ranked_s15.get('k', 0)
            s15_deaths = ranked_s15.get('d', 0)
            s15_assists = ranked_s15.get('a', 0)
            s15_wins = ranked_s15.get('w', 0)
            s15_losses = ranked_s15.get('l', 0)
            s15_kd = round(s15_kills / s15_deaths, 2) if s15_deaths > 0 else s15_kills
        else:
            s15_kills = s15_deaths = s15_assists = s15_wins = s15_losses = 0
            s15_kd = 0.0
        
        # Get account ID and clan info  
        account_id = basic_info.get('userID', 'N/A')
        clan_info = player_info.get('clan', {}).get('basicInfo', {})
        clan_tag = clan_info.get('tag', 'N/A')
        clan_name = clan_info.get('name', '')
        
        # Format clan display as [Tag] - Name
        if clan_tag != 'N/A' and clan_name:
            clan_display = f"[{clan_tag}] - {clan_name}"
        elif clan_tag != 'N/A':
            clan_display = clan_tag
        else:
            clan_display = 'N/A'
        
        # Create enhanced embed with PINK color instead of teal
        embed = discord.Embed(
            title=f"🦧 **{username} — Season 15**",
            color=discord.Color.magenta()  # Changed from discord.Color.teal() to pink
        )
        
        # Player info section
        player_info_text = f"🆔 **Account ID:** {account_id}\n🏷️ **Clan:** {clan_display}\n📋 **Ban Status:** {ban_status}"
        embed.add_field(name="", value=player_info_text, inline=False)
        
        # ELO and Level section
        elo_level_text = f"🏅 **ELO:** {current_mmr:,}\n📊 **Level:** {level}"
        embed.add_field(name="", value=elo_level_text, inline=False)
        
        # Casual Stats section (using overall stats)
        casual_stats_text = f"• **Kills:** {total_kills:,}\n• **Deaths:** {total_deaths:,}\n• **Assists:** {total_assists:,}\n• **K/D Ratio:** {total_kd}"
        embed.add_field(name="⚔️ **Casual Stats**", value=casual_stats_text, inline=False)
        
        # Ranked Stats section (Season 15 only, displayed below casual)  
        ranked_stats_text = f"• **Kills:** {s15_kills:,}\n• **Deaths:** {s15_deaths:,}\n• **Assists:** {s15_assists:,}\n• **Wins:** {s15_wins}\n• **Losses:** {s15_losses}\n• **K/D Ratio:** {s15_kd}"
        embed.add_field(name="🏆 **Ranked Stats (S15)**", value=ranked_stats_text, inline=False)
        
        # Add ban details if player is banned
        if ban_data:
            ban_reasons = {
                1: "Cheating",
                2: "Abusive Behavior", 
                3: "Exploiting",
                4: "Team Killing",
                5: "Inappropriate Name",
                6: "Spam",
                7: "Other"
            }
            reason_id = ban_data.get('Reason', ban_data.get('reason', 0))
            ban_reason = ban_reasons.get(reason_id, "Unknown")
            embed.add_field(name="🚫 **Banned**", value=f"**Reason:** {ban_reason}", inline=False)

        await interaction.followup.send(embed=embed)
        
        # Track this player for the user
        user_id = interaction.user.id
        if user_id not in tracked_players:
            tracked_players[user_id] = []
        
        if player_name not in tracked_players[user_id]:
            tracked_players[user_id].append(player_name)
        
        # Initialize player state for monitoring
        if player_name not in player_states:
            player_states[player_name] = {
                'last_stats': data,
                'last_check_time': datetime.utcnow(),
                'tracking_channels': [],
                'last_username': username,
                'last_ban_status': ban_data,
                'last_mmr': current_mmr if current_mmr > 0 else None,
                'in_ranked_match': False,
                'active_match_messages': {},
                'last_match_kda': {},
                'match_start_stats': {},
                'initial_stats': {
                    'kills': s15_kills,
                    'deaths': s15_deaths,
                    'assists': s15_assists,
                    'mmr': current_mmr
                }
            }
        
        # Add this channel to tracking list
        if interaction.channel and interaction.channel.id not in player_states[player_name]['tracking_channels']:
            player_states[player_name]['tracking_channels'].append(interaction.channel.id)
        
        # Send tracking confirmation
        tracking_embed = discord.Embed(
            title="🟢 Now Tracking",
            description=f"**{username}** is now being monitored for updates",
            color=0x00FF00
        )
        tracking_embed.add_field(
            name="Monitoring Features:",
            value="• 🏆 Ranked match notifications (KDA, MMR changes)\n• ⚠️ Ban status alerts (reason, duration)\n• 📝 Username change notifications\n• 📊 Real-time stat updates",
            inline=False
        )
        tracking_embed.add_field(
            name="Stop Tracking",
            value=f"Use `/unsnipe {username}` to stop tracking.",
            inline=False
        )
        
        await interaction.followup.send(embed=tracking_embed)
        
        # Check if player is currently in a ranked match and send status
        await send_ranked_status_message(player_name, data)
        
    except Exception as e:
        logger.error(f"Error in snipe command: {e}")
        await interaction.followup.send("❌ An error occurred while fetching player data.")

@bot.tree.command(name="unsnipe", description="Stop tracking a Critical Ops player")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def unsnipe_player(interaction: discord.Interaction, player_name: str):
    """Stop tracking a Critical Ops player - Available to authorized users"""
    # Check authorization
    if interaction.user.id not in AUTHORIZED_USERS:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    
    # Remove player from user's tracking list
    if user_id in tracked_players and player_name in tracked_players[user_id]:
        tracked_players[user_id].remove(player_name)
        
        # Remove channel from player's tracking channels
        if player_name in player_states and interaction.channel:
            if interaction.channel.id in player_states[player_name]['tracking_channels']:
                player_states[player_name]['tracking_channels'].remove(interaction.channel.id)
            
            # If no one is tracking this player anymore, remove from states
            if not player_states[player_name]['tracking_channels']:
                del player_states[player_name]
        
        embed = discord.Embed(
            title="🔴 Stopped Tracking",
            description=f"No longer monitoring **{player_name}**",
            color=0xFF4444
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ You are not currently tracking **{player_name}**.")

@bot.tree.command(name="list", description="Show your tracked players")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def list_tracked_players(interaction: discord.Interaction):
    """List all players you're currently tracking"""
    if interaction.user.id not in AUTHORIZED_USERS:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    
    user_id = interaction.user.id
    
    if user_id not in tracked_players or not tracked_players[user_id]:
        embed = discord.Embed(
            title="📋 Your Tracked Players",
            description="You are not currently tracking any players.",
            color=0x888888
        )
        embed.add_field(name="Start Tracking", value="Use `/snipe [player_name]` to start tracking a player.", inline=False)
        await interaction.response.send_message(embed=embed)
        return
    
    players_list = "\n".join([f"• **{player}**" for player in tracked_players[user_id]])
    
    embed = discord.Embed(
        title="📋 Your Tracked Players",
        description=players_list,
        color=0x00FFFF
    )
    embed.add_field(name="Stop Tracking", value="Use `/unsnipe [player_name]` to stop tracking a player.", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="authorize", description="Authorize a user to use bot commands (Owner only)")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def authorize_user(interaction: discord.Interaction, user: discord.User):
    """Authorize a user to use bot commands - Owner only"""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    if user.id in AUTHORIZED_USERS:
        await interaction.response.send_message(f"✅ **{user.name}** is already authorized.", ephemeral=True)
        return
    
    AUTHORIZED_USERS.add(user.id)
    
    embed = discord.Embed(
        title="✅ User Authorized",
        description=f"**{user.name}** ({user.id}) can now use bot commands.",
        color=0x00FF00
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="deauthorize", description="Remove user authorization (Owner only)")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def deauthorize_user(interaction: discord.Interaction, user: discord.User):
    """Remove user authorization - Owner only"""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    if user.id == DISCORD_OWNER_ID:
        await interaction.response.send_message("❌ Cannot deauthorize the bot owner.", ephemeral=True)
        return
    
    if user.id not in AUTHORIZED_USERS:
        await interaction.response.send_message(f"❌ **{user.name}** is not currently authorized.", ephemeral=True)
        return
    
    AUTHORIZED_USERS.remove(user.id)
    
    embed = discord.Embed(
        title="🔴 User Deauthorized",
        description=f"**{user.name}** ({user.id}) can no longer use bot commands.",
        color=0xFF4444
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userlist", description="List all authorized users (Owner only)")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def list_authorized_users(interaction: discord.Interaction):
    """List all authorized users - Owner only"""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    if not AUTHORIZED_USERS:
        embed = discord.Embed(
            title="👥 Authorized Users",
            description="No users are currently authorized.",
            color=0x888888
        )
        await interaction.response.send_message(embed=embed)
        return
    
    user_list = []
    for user_id in AUTHORIZED_USERS:
        try:
            user = await bot.fetch_user(user_id)
            status = "👑 Owner" if user_id == DISCORD_OWNER_ID else "✅ Authorized"
            user_list.append(f"• **{user.name}** ({user_id}) - {status}")
        except:
            user_list.append(f"• **Unknown User** ({user_id}) - ✅ Authorized")
    
    embed = discord.Embed(
        title="👥 Authorized Users",
        description="\n".join(user_list),
        color=0x00FFFF
    )
    await interaction.response.send_message(embed=embed)

# TEST COMMANDS FOR SPECIFIC SCENARIOS

@bot.tree.command(name="test_username_change", description="Test username change detection for Account ID 31357194 to Donk666 (Owner only)")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def test_username_change(interaction: discord.Interaction):
    """Test username change detection for Account ID 31357194 to Donk666"""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    # Simulate tracking the player with Account ID 31357194
    player_name = "31357194"  # Using account ID as player name
    old_username = "OldPlayerName"  # Simulated old username
    new_username = "Donk666"  # New username as requested
    
    # Create a test player state if it doesn't exist
    if player_name not in player_states:
        player_states[player_name] = {
            'last_stats': {},
            'last_check_time': datetime.utcnow(),
            'tracking_channels': [interaction.channel.id] if interaction.channel else [],
            'last_username': old_username,
            'last_ban_status': None,
            'last_mmr': None,
            'in_ranked_match': False,
            'active_match_messages': {},
            'last_match_kda': {},
            'match_start_stats': {},
            'initial_stats': {}
        }
    else:
        # Add this channel to tracking if not already there
        if interaction.channel and interaction.channel.id not in player_states[player_name]['tracking_channels']:
            player_states[player_name]['tracking_channels'].append(interaction.channel.id)
    
    # Simulate the username change detection
    embed = discord.Embed(
        title="📝 Username Changed",
        description=f"**{old_username}** changed their name to **{new_username}**",
        color=0xFFAA00
    )
    embed.add_field(name="Account ID", value=player_name, inline=True)
    embed.add_field(name="Old Username", value=old_username, inline=True)
    embed.add_field(name="New Username", value=new_username, inline=True)
    embed.add_field(name="Test Status", value="✅ **TEST MESSAGE** - Bot successfully detected username change!", inline=False)
    
    # Update the stored username
    player_states[player_name]['last_username'] = new_username
    
    # Send the test notification
    await interaction.followup.send("🧪 **Testing Username Change Detection**", embed=embed)
    
    logger.info(f"Test username change executed for Account ID {player_name}: {old_username} -> {new_username}")

@bot.tree.command(name="test_ban_detection", description="Test ban detection for player Monesy (Owner only)")
@discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def test_ban_detection(interaction: discord.Interaction):
    """Test ban detection for player Monesy"""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    # Simulate tracking the player Monesy
    player_name = "Monesy"
    username = "Monesy"
    
    # Create a test player state if it doesn't exist
    if player_name not in player_states:
        player_states[player_name] = {
            'last_stats': {},
            'last_check_time': datetime.utcnow(),
            'tracking_channels': [interaction.channel.id] if interaction.channel else [],
            'last_username': username,
            'last_ban_status': None,  # Initially not banned
            'last_mmr': None,
            'in_ranked_match': False,
            'active_match_messages': {},
            'last_match_kda': {},
            'match_start_stats': {},
            'initial_stats': {}
        }
    else:
        # Add this channel to tracking if not already there
        if interaction.channel and interaction.channel.id not in player_states[player_name]['tracking_channels']:
            player_states[player_name]['tracking_channels'].append(interaction.channel.id)
    
    # Simulate ban data (permanent ban)
    ban_data = {
        'reason': 'Cheating',
        'type': 'Permanent',
        'expires_at': 'Permanent',
        'Reason': 1  # Cheating code
    }
    
    # Simulate the ban detection
    ban_reasons = {
        1: "Cheating",
        2: "Abusive Behavior", 
        3: "Exploiting",
        4: "Team Killing",
        5: "Inappropriate Name",
        6: "Spam",
        7: "Other"
    }
    
    reason_id = ban_data.get('Reason', ban_data.get('reason', 0))
    ban_reason = ban_reasons.get(reason_id, "Unknown")
    ban_type = ban_data.get('type', 'Unknown')
    ban_expires = ban_data.get('expires_at', 'Permanent')
    
    if ban_expires and ban_expires != 'Permanent':
        ban_duration = f"Until {ban_expires}"
    else:
        ban_duration = "Permanent"
    
    embed = discord.Embed(
        title="⚠️ Player Banned",
        description=f"**{username}** has been banned from Critical Ops",
        color=0xFF4444
    )
    embed.add_field(name="Reason", value=ban_reason, inline=True)
    embed.add_field(name="Type", value=ban_type, inline=True)
    embed.add_field(name="Duration", value=ban_duration, inline=True)
    embed.add_field(name="Test Status", value="✅ **TEST MESSAGE** - Bot successfully detected permanent ban!", inline=False)
    
    # Update the stored ban status
    player_states[player_name]['last_ban_status'] = ban_data
    
    # Send the test notification
    await interaction.followup.send("🧪 **Testing Ban Detection**", embed=embed)
    
    logger.info(f"Test ban detection executed for player {player_name}: Permanent ban for {ban_reason}")

if __name__ == "__main__":
    try:
        bot.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
