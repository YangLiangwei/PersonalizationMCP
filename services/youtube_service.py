"""YouTube service layer used by CLI and MCP adapter."""

from __future__ import annotations

import os
from typing import Dict

import httpx


class YouTubeService:
    @staticmethod
    def credentials_status() -> str:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return "❌ YouTube API key not found in environment variables"
        return f"✅ YouTube API key found: Key={api_key[:8]}..."

    @staticmethod
    def get_config() -> str:
        api_key = os.getenv("YOUTUBE_API_KEY")
        return f"""YouTube API Configuration:
API Key: {'✅ Configured' if api_key else '❌ Not configured'}
Status: {'🟢 Ready for public data' if api_key else '🔴 Incomplete'}

API Key Preview: {api_key[:8] + '...' if api_key else 'Not set'}

Available Features:
✅ Video search
✅ Video details
✅ Channel information
✅ Trending videos
⚠️  User subscriptions (requires OAuth2)
⚠️  Watch history (requires OAuth2)
⚠️  Playlists (requires OAuth2)

Note: Personal data requires OAuth2 authentication setup.
"""

    @staticmethod
    def search_videos(query: str, max_results: int = 10) -> Dict:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return {"error": "YouTube API key not configured"}
        if not query:
            return {"error": "Search query is required"}

        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "key": api_key,
                "q": query,
                "part": "snippet",
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": "relevance",
            }
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            videos = []
            for item in data.get("items", []):
                desc = item["snippet"].get("description", "")
                videos.append(
                    {
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "description": desc[:200] + "..." if len(desc) > 200 else desc,
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    }
                )

            return {
                "query": query,
                "total_results": data.get("pageInfo", {}).get("totalResults", 0),
                "videos": videos,
            }
        except Exception as e:
            return {"error": f"Failed to search videos: {str(e)}"}

    @staticmethod
    def get_video_details(video_id: str) -> Dict:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return {"error": "YouTube API key not configured"}
        if not video_id:
            return {"error": "Video ID is required"}

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {"key": api_key, "id": video_id, "part": "snippet,statistics,contentDetails"}
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get("items"):
                return {"error": "Video not found"}

            video = data["items"][0]
            return {
                "video_id": video_id,
                "title": video["snippet"]["title"],
                "channel": video["snippet"]["channelTitle"],
                "description": video["snippet"]["description"],
                "published_at": video["snippet"]["publishedAt"],
                "duration": video["contentDetails"]["duration"],
                "view_count": video["statistics"].get("viewCount", "N/A"),
                "like_count": video["statistics"].get("likeCount", "N/A"),
                "comment_count": video["statistics"].get("commentCount", "N/A"),
                "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "tags": video["snippet"].get("tags", []),
            }
        except Exception as e:
            return {"error": f"Failed to fetch video details: {str(e)}"}

    @staticmethod
    def get_channel_info(channel_id: str) -> Dict:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return {"error": "YouTube API key not configured"}
        if not channel_id:
            return {"error": "Channel ID is required"}

        try:
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {"key": api_key, "id": channel_id, "part": "snippet,statistics,contentDetails"}
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get("items"):
                return {"error": "Channel not found"}

            channel = data["items"][0]
            return {
                "channel_id": channel_id,
                "title": channel["snippet"]["title"],
                "description": channel["snippet"]["description"],
                "published_at": channel["snippet"]["publishedAt"],
                "subscriber_count": channel["statistics"].get("subscriberCount", "Hidden"),
                "video_count": channel["statistics"].get("videoCount", "N/A"),
                "view_count": channel["statistics"].get("viewCount", "N/A"),
                "thumbnail": channel["snippet"]["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/channel/{channel_id}",
                "country": channel["snippet"].get("country", "N/A"),
            }
        except Exception as e:
            return {"error": f"Failed to fetch channel info: {str(e)}"}

    @staticmethod
    def get_trending(region_code: str = "US", max_results: int = 10) -> Dict:
        api_key = os.getenv("YOUTUBE_API_KEY")
        if not api_key:
            return {"error": "YouTube API key not configured"}

        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "key": api_key,
                "part": "snippet,statistics",
                "chart": "mostPopular",
                "regionCode": region_code,
                "maxResults": min(max_results, 50),
            }
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            videos = []
            for item in data.get("items", []):
                videos.append(
                    {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "view_count": item["statistics"].get("viewCount", "N/A"),
                        "like_count": item["statistics"].get("likeCount", "N/A"),
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']}",
                    }
                )

            return {"region": region_code, "trending_videos": videos}
        except Exception as e:
            return {"error": f"Failed to fetch trending videos: {str(e)}"}
