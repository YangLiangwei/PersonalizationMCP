"""Shared status/service utilities."""

from __future__ import annotations

import os


def build_personalization_status() -> str:
    steam_configured = bool(os.getenv("STEAM_API_KEY") and os.getenv("STEAM_USER_ID"))
    youtube_configured = bool(os.getenv("YOUTUBE_API_KEY"))
    bilibili_configured = bool(os.getenv("BILIBILI_SESSDATA") and os.getenv("BILIBILI_BILI_JCT"))
    spotify_configured = bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))
    reddit_configured = bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"))

    return f"""PersonalizationMCP Server Status:

🎮 Steam Integration: {'✅ Active' if steam_configured else '❌ Not configured'}
🎥 YouTube Integration: {'✅ Active' if youtube_configured else '❌ Not configured'}
📺 Bilibili Integration: {'✅ Active' if bilibili_configured else '❌ Not configured'}
🎵 Spotify Integration: {'✅ Active' if spotify_configured else '❌ Not configured'}
📱 Reddit Integration: {'✅ Active' if reddit_configured else '❌ Not configured'}
🐦 Twitter Integration: ⏳ Coming soon
💻 GitHub Integration: ⏳ Coming soon

Server Version: 1.6.0
Total Platforms: {sum([steam_configured, youtube_configured, bilibili_configured, spotify_configured, reddit_configured])} active, 2 planned

Configuration Status:
- Steam API: {'Ready' if steam_configured else 'Needs setup'}
- YouTube API: {'Ready' if youtube_configured else 'Needs setup'}
- Bilibili API: {'Ready' if bilibili_configured else 'Needs setup'}
- Spotify API: {'Ready' if spotify_configured else 'Needs setup'}
- Reddit API: {'Ready' if reddit_configured else 'Needs setup'}
"""
