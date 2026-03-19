"""Bilibili service layer used by CLI and MCP adapter."""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Optional

import nest_asyncio

try:
    from bilibili_api import Credential, misc, user, video

    BILIBILI_API_AVAILABLE = True
    nest_asyncio.apply()
except ImportError:
    BILIBILI_API_AVAILABLE = False

    class Credential:  # type: ignore[no-redef]
        pass


class BilibiliService:
    @staticmethod
    def run_async(coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return asyncio.run(coro)
            return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    @staticmethod
    def get_credential() -> Optional[Credential]:
        sessdata = os.getenv("BILIBILI_SESSDATA")
        bili_jct = os.getenv("BILIBILI_BILI_JCT")
        buvid3 = os.getenv("BILIBILI_BUVID3")

        if sessdata and bili_jct:
            import urllib.parse

            try:
                decoded_sessdata = urllib.parse.unquote(sessdata)
                dedeuserid = decoded_sessdata.split(",")[0]
                return Credential(
                    sessdata=sessdata,
                    bili_jct=bili_jct,
                    buvid3=buvid3,
                    dedeuserid=dedeuserid,
                )
            except Exception:
                return Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)
        return None

    @staticmethod
    def credentials_status() -> str:
        if not BILIBILI_API_AVAILABLE:
            return "❌ bilibili-api library not installed. Run: pip install bilibili-api"

        sessdata = os.getenv("BILIBILI_SESSDATA")
        bili_jct = os.getenv("BILIBILI_BILI_JCT")
        if not sessdata or not bili_jct:
            return "❌ Bilibili credentials not found in environment variables"
        return f"✅ Bilibili credentials found: SESSDATA={sessdata[:8]}..., bili_jct={bili_jct[:8]}..."

    @staticmethod
    def get_config() -> str:
        if not BILIBILI_API_AVAILABLE:
            return "❌ bilibili-api library not installed"

        credential = BilibiliService.get_credential()
        status = "✅ Ready" if credential else "❌ Not configured"
        return f"""Bilibili API Configuration:

Library Status: {'✅ Installed' if BILIBILI_API_AVAILABLE else '❌ Not installed'}
Credentials: {status}
Authentication: {'Cookie-based' if credential else 'None'}

Available Features:
- User profile information ✅
- Following list ✅
- Video search ✅
- User videos ✅
- Favorites (requires login) {'✅' if credential else '❌'}
- Watch history (requires login) {'✅' if credential else '❌'}
- To-view list (稍后再看) (requires login) {'✅' if credential else '❌'}
"""

    @staticmethod
    def search_videos(keyword: str, page: int = 1, order: str = "totalrank") -> Dict:
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        try:
            search_result = BilibiliService.run_async(
                misc.web_search_by_type(keyword, search_type="video", page=page, order=order)
            )
            videos = []
            for video_info in search_result.get("result", []):
                videos.append(
                    {
                        "bvid": video_info.get("bvid", ""),
                        "aid": video_info.get("aid", 0),
                        "title": video_info.get("title", ""),
                        "description": video_info.get("description", ""),
                        "author": video_info.get("author", ""),
                        "mid": video_info.get("mid", 0),
                        "duration": video_info.get("duration", ""),
                        "play": video_info.get("play", 0),
                        "danmaku": video_info.get("video_review", 0),
                        "pubdate": video_info.get("pubdate", 0),
                        "pic": video_info.get("pic", ""),
                        "url": f"https://www.bilibili.com/video/{video_info.get('bvid', '')}",
                    }
                )

            return {
                "keyword": keyword,
                "page": page,
                "total_results": search_result.get("numResults", 0),
                "videos": videos,
            }
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    @staticmethod
    def get_video_info(bvid: str) -> Dict:
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        try:
            v = video.Video(bvid=bvid)
            video_info = BilibiliService.run_async(v.get_info())
            return {
                "bvid": bvid,
                "aid": video_info.get("aid", 0),
                "title": video_info.get("title", ""),
                "description": video_info.get("desc", ""),
                "duration": video_info.get("duration", 0),
                "owner": {
                    "mid": video_info.get("owner", {}).get("mid", 0),
                    "name": video_info.get("owner", {}).get("name", ""),
                },
                "stats": {
                    "view": video_info.get("stat", {}).get("view", 0),
                    "danmaku": video_info.get("stat", {}).get("danmaku", 0),
                    "reply": video_info.get("stat", {}).get("reply", 0),
                    "favorite": video_info.get("stat", {}).get("favorite", 0),
                    "coin": video_info.get("stat", {}).get("coin", 0),
                    "share": video_info.get("stat", {}).get("share", 0),
                    "like": video_info.get("stat", {}).get("like", 0),
                },
                "pubdate": video_info.get("pubdate", 0),
                "url": f"https://www.bilibili.com/video/{bvid}",
            }
        except Exception as e:
            return {"error": f"Failed to get video info: {str(e)}"}
