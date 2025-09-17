#!/usr/bin/env python3
"""
PersonalizationMCP Server
Main server that integrates multiple platforms for personalized AI interactions.
"""

import os
from mcp.server.fastmcp import FastMCP

# Import platform modules
from platforms.steam.steam_mcp import setup_steam_mcp
from platforms.youtube.youtube_mcp import setup_youtube_mcp
from platforms.bilibili.bilibili_mcp import setup_bilibili_mcp
from platforms.spotify.spotify_mcp import setup_spotify_mcp
from platforms.reddit.reddit_mcp import setup_reddit_mcp

# Create main MCP server
mcp = FastMCP("PersonalizationMCP")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b

@mcp.tool()
def test_connection() -> str:
    """Test if the MCP server is working."""
    return "✅ MCP Server is working perfectly!"

# Setup platform integrations
def setup_all_platforms():
    """Setup all platform integrations."""
    
    # Steam integration
    setup_steam_mcp(mcp)
    
    # YouTube integration
    setup_youtube_mcp(mcp)
    
    # Bilibili integration
    setup_bilibili_mcp(mcp)
    
    # Spotify integration
    setup_spotify_mcp(mcp)
    
    # Reddit integration
    setup_reddit_mcp(mcp)
    
    # Future platform integrations can be added here:
    # setup_twitter_mcp(mcp)
    # setup_github_mcp(mcp)

@mcp.tool()
def get_personalization_status() -> str:
    """Get overall personalization server status."""
    steam_configured = bool(os.getenv("STEAM_API_KEY") and os.getenv("STEAM_USER_ID"))
    youtube_configured = bool(os.getenv("YOUTUBE_API_KEY"))
    bilibili_configured = bool(os.getenv("BILIBILI_SESSDATA") and os.getenv("BILIBILI_BILI_JCT"))
    spotify_configured = bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))
    reddit_configured = bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"))
    
    status_info = f"""PersonalizationMCP Server Status:

🎮 Steam Integration: {'✅ Active' if steam_configured else '❌ Not configured'}
🎥 YouTube Integration: {'✅ Active' if youtube_configured else '❌ Not configured'}
📺 Bilibili Integration: {'✅ Active' if bilibili_configured else '❌ Not configured'}
🎵 Spotify Integration: {'✅ Active' if spotify_configured else '❌ Not configured'}
📱 Reddit Integration: {'✅ Active' if reddit_configured else '❌ Not configured'}
🐦 Twitter Integration: ⏳ Coming soon
💻 GitHub Integration: ⏳ Coming soon

Server Version: 1.4.0
Total Platforms: {sum([steam_configured, youtube_configured, bilibili_configured, spotify_configured, reddit_configured])} active, 2 planned

Configuration Status:
- Steam API: {'Ready' if steam_configured else 'Needs setup'}
- YouTube API: {'Ready' if youtube_configured else 'Needs setup'}
- Bilibili API: {'Ready' if bilibili_configured else 'Needs setup'}
- Spotify API: {'Ready' if spotify_configured else 'Needs setup'}
"""
    return status_info

if __name__ == "__main__":
    # Setup all platform integrations
    setup_all_platforms()
    
    # Start the server
    mcp.run()
