# Critical Ops Discord Bot

## Overview

This is a Discord bot that provides real-time tracking and monitoring of Critical Ops player statistics. The bot fetches player data from the Critical Ops API and offers live notifications for ranked matches, ban status changes, username modifications, and MMR tracking. The system is designed to work across Discord servers, DMs, and group chats with comprehensive stat-change detection for accurate match monitoring.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Bot Framework**: Discord.py with asyncio for concurrent operations and slash command support
- **Web Server**: Simple Python HTTP server for health monitoring and status checks
- **API Integration**: Direct HTTP requests to Critical Ops API (`https://api.criticalops.com/v1/`)
- **Data Storage**: In-memory storage using Python dictionaries (ephemeral, resets on restart)
- **Process Management**: Single Python process with background monitoring tasks

**Rationale**: Discord.py provides robust Discord API integration with built-in slash command support. The simple HTTP server offers basic health check capabilities without additional dependencies. In-memory storage eliminates database complexity while providing fast access for real-time monitoring.

### Authentication & Authorization
- **User Authorization**: Hardcoded whitelist of Discord user IDs stored in `AUTHORIZED_USERS` set
- **Owner Privileges**: Special bot owner permissions via `DISCORD_OWNER_ID` environment variable
- **Command Protection**: All tracking commands require authorization check before execution

**Rationale**: Hardcoded user IDs provide simple, secure access control without requiring a database or complex authentication system. This approach is ideal for a small, trusted user base and eliminates authentication complexity while maintaining security.

## Key Components

### Discord Bot Core (`bot.py`)
- **Command System**: Slash commands with `/` prefix for modern Discord integration
- **Intent Configuration**: Supports DMs, group chats, and guild messages for universal access
- **Error Handling**: Comprehensive logging and user feedback for API failures and authorization issues
- **Background Monitoring**: 30-second interval loop for checking tracked player updates
- **Global Command Sync**: Commands work across all Discord contexts (servers, DMs, group chats)

### Player Tracking System
- **Tracked Players Storage**: `{user_id: [player_names]}` mapping for user-specific tracking lists
- **Player States Cache**: Complex state management including:
  - `last_stats`: Previous API response for change detection
  - `tracking_channels`: List of Discord channels monitoring this player
  - `in_ranked_match`: Boolean flag for match state
  - `active_match_messages`: Dictionary of live match messages being updated
  - `match_start_stats`: Baseline stats when match begins for incremental tracking
  - `last_match_kda`: Previous KDA values for detecting stat changes
- **Stat-Change Detection**: Monitors Season 15 ranked stats (kills, deaths, assists) to detect when players enter/exit ranked matches
- **Real-time Match Tracking**: Live KDA updates during ranked matches with message editing
- **Multi-channel Support**: Single player can be tracked across multiple Discord channels simultaneously

### Health Monitoring Server (`simple_server.py`)
- **Health Endpoint**: `/health` returns JSON status with timestamp
- **Status API**: `/api/status` provides server and bot status information
- **Web Interface**: Simple HTML status page for manual monitoring
- **Port Configuration**: Runs on port 5000 for deployment compatibility

### Available Commands
- `/snipe <player_name>`: Start tracking a player and display current stats
- `/unsnipe <player_name>`: Stop tracking a specific player
- Authorization required for all commands based on hardcoded user whitelist

## Data Flow

1. **Command Execution**: User runs `/snipe` command → Authorization check → API call to Critical Ops → Display stats embed → Add to tracking system
2. **Background Monitoring**: Every 30 seconds → Fetch current stats for all tracked players → Compare with stored states → Detect changes (ranked matches, bans, username changes)
3. **Match Detection**: Compare Season 15 ranked stats (K/D/A) between API calls → If stats increased, player entered ranked match → Send live match notification
4. **Live Updates**: During ranked match → Continue monitoring stats → Edit existing messages with updated KDA → Detect match end via MMR change
5. **Multi-channel Broadcasting**: Send notifications to all channels tracking the specific player

## External Dependencies

### Critical Ops API
- **Base URL**: `https://api.criticalops.com/v1/`
- **Player Search**: `/players/search?name={player_name}` for finding player by username
- **Player Details**: `/players/{player_id}` for detailed stats and current status
- **No Authentication**: Public API with no rate limiting mentioned in code
- **Response Format**: JSON with nested stats including seasonal data, ban status, and basic info

### Discord API
- **Discord.py Library**: Handles all Discord interactions, slash commands, and message management
- **Required Permissions**: Send messages, embed links, use slash commands
- **Bot Token**: Required via `DISCORD_BOT_TOKEN` environment variable

## Deployment Strategy

### Environment Variables
- `DISCORD_BOT_TOKEN`: Required Discord bot token for API access
- `DISCORD_OWNER_ID`: Optional owner user ID for special permissions

### Process Management
- **Single Process**: Both bot and health server run in same Python process
- **Background Tasks**: Asyncio tasks for continuous monitoring
- **Error Recovery**: Bot continues running even if API calls fail

### Monitoring
- **Health Checks**: HTTP server on port 5000 provides status endpoints
- **Logging**: Comprehensive logging for debugging authorization and API issues
- **Graceful Degradation**: Bot functions continue even if some API calls fail

### Data Persistence
- **No Database**: All data stored in memory (resets on restart)
- **Stateless Design**: Can be restarted without data loss concerns
- **User Re-tracking**: Users need to re-run `/snipe` commands after bot restart

**Rationale**: The stateless, in-memory approach eliminates database complexity and maintenance while providing fast performance for real-time monitoring. For a Discord bot with a small user base, the tradeoff of losing tracking data on restart is acceptable for the simplicity gained.