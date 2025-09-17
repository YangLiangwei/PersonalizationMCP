# Steam Platform Integration

This module provides Steam API integration for the PersonalizationMCP server.

## Features

- 🎮 Get your game library with detailed statistics and playtime
- 📊 View recent gaming activity and currently playing games
- 🏆 Get detailed game information and achievements
- 👥 Compare games with friends and get recommendations
- 📈 Analyze gaming habits and preferences

## Configuration

Required environment variables:
- `STEAM_API_KEY`: Your Steam Web API key
- `STEAM_USER_ID`: Your Steam user ID

## Files

- `steam_mcp.py`: Main Steam MCP integration module
- `README.md`: This documentation file

## API Key Setup

1. Visit [Steam Web API Key page](https://steamcommunity.com/dev/apikey)
2. Log in to your Steam account
3. Enter a domain name (you can use `localhost` for development)
4. Copy the generated API key

## Steam User ID

1. Go to your Steam profile page
2. Look at the URL, for example: `https://steamcommunity.com/profiles/76561198123456789/`
3. The number `76561198123456789` is your Steam ID
