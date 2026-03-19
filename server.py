#!/usr/bin/env python3
"""
PersonalizationMCP Server
Main server that integrates multiple platforms for personalized AI interactions.
"""

from __future__ import annotations

import os
from typing import Callable, Iterable

from mcp.server.fastmcp import FastMCP

# Import platform modules
from platforms.steam.steam_mcp import setup_steam_mcp
from platforms.youtube.youtube_mcp import setup_youtube_mcp
from platforms.bilibili.bilibili_mcp import setup_bilibili_mcp
from platforms.spotify.spotify_mcp import setup_spotify_mcp
from platforms.reddit.reddit_mcp import setup_reddit_mcp


TOOL_PROFILES: dict[str, set[str] | None] = {
    # Keep backwards compatibility: expose everything.
    "full": None,
    # A safer default profile for assistant integrations.
    "safe": {
        "test_connection",
        "get_personalization_status",
        # Steam
        "test_steam_credentials",
        "get_steam_config",
        "get_steam_library",
        "get_steam_recent_activity",
        "get_steam_profile",
        # YouTube (public + token status)
        "test_youtube_credentials",
        "get_youtube_config",
        "search_youtube_videos",
        "get_video_details",
        "get_channel_info",
        "get_trending_videos",
        "get_youtube_token_status",
        # Bilibili (mostly read-only)
        "test_bilibili_credentials",
        "get_bilibili_config",
        "get_bilibili_user_info",
        "search_bilibili_videos",
        "get_bilibili_video_info",
        # Spotify + Reddit health checks only
        "test_spotify_credentials",
        "get_spotify_config",
        "test_reddit_credentials",
        "get_reddit_config",
    },
    # A minimal ops/debug profile.
    "minimal": {"test_connection", "get_personalization_status"},
}


def _build_tool_filter(mcp: FastMCP, allowed_tools: set[str] | None) -> None:
    """Patch mcp.tool decorator so only allow-listed tools are registered."""
    if allowed_tools is None:
        return

    original_tool = mcp.tool

    def filtered_tool(*dargs, **dkwargs):
        # @mcp.tool without params (rare, but support it)
        if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
            func = dargs[0]
            if func.__name__ not in allowed_tools:
                return func
            return original_tool(func)

        # @mcp.tool() or @mcp.tool(name="...")
        def decorator(func: Callable):
            tool_name = dkwargs.get("name") or func.__name__
            if tool_name not in allowed_tools:
                return func
            return original_tool(*dargs, **dkwargs)(func)

        return decorator

    mcp.tool = filtered_tool


def build_personalization_status() -> str:
    """Build overall personalization server status string."""
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

Server Version: 1.5.0
Total Platforms: {sum([steam_configured, youtube_configured, bilibili_configured, spotify_configured, reddit_configured])} active, 2 planned

Configuration Status:
- Steam API: {'Ready' if steam_configured else 'Needs setup'}
- YouTube API: {'Ready' if youtube_configured else 'Needs setup'}
- Bilibili API: {'Ready' if bilibili_configured else 'Needs setup'}
- Spotify API: {'Ready' if spotify_configured else 'Needs setup'}
- Reddit API: {'Ready' if reddit_configured else 'Needs setup'}
"""
    return status_info


def create_mcp_server(profile: str = "full", extra_allowed_tools: Iterable[str] | None = None) -> FastMCP:
    """Create and configure MCP server with optional tool exposure profile."""
    if profile not in TOOL_PROFILES:
        raise ValueError(f"Unknown profile '{profile}'. Available: {', '.join(TOOL_PROFILES.keys())}")

    mcp = FastMCP("PersonalizationMCP")

    base_allowlist = TOOL_PROFILES[profile]
    if base_allowlist is None:
        effective_allowlist = None
    else:
        effective_allowlist = set(base_allowlist)
        if extra_allowed_tools:
            effective_allowlist.update(t for t in extra_allowed_tools if t)

    _build_tool_filter(mcp, effective_allowlist)

    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    @mcp.tool()
    def test_connection() -> str:
        """Test if the MCP server is working."""
        return "✅ MCP Server is working perfectly!"

    @mcp.tool()
    def get_personalization_status() -> str:
        """Get overall personalization server status."""
        return build_personalization_status()

    # Setup platform integrations (tool filter will decide what gets exposed)
    setup_steam_mcp(mcp)
    setup_youtube_mcp(mcp)
    setup_bilibili_mcp(mcp)
    setup_spotify_mcp(mcp)
    setup_reddit_mcp(mcp)

    return mcp


def main() -> None:
    """Run server using environment-driven profile.

    Environment variables:
    - MCP_TOOL_PROFILE: full|safe|minimal (default: full)
    - MCP_EXTRA_ALLOWED_TOOLS: comma-separated extra tool names
    """
    profile = os.getenv("MCP_TOOL_PROFILE", "full").strip() or "full"
    extra = [x.strip() for x in os.getenv("MCP_EXTRA_ALLOWED_TOOLS", "").split(",") if x.strip()]
    mcp = create_mcp_server(profile=profile, extra_allowed_tools=extra)
    mcp.run()


if __name__ == "__main__":
    main()
