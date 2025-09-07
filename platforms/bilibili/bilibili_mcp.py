"""
Bilibili MCP Server Module
Provides Bilibili API integration for personalized video consumption data.
"""

import os
import asyncio
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import nest_asyncio

try:
    from bilibili_api import user, video, misc, Credential
    from bilibili_api.exceptions import ResponseCodeException
    BILIBILI_API_AVAILABLE = True
    # Apply nest_asyncio immediately when bilibili_api is available
    nest_asyncio.apply()
except ImportError:
    BILIBILI_API_AVAILABLE = False
    # Define dummy Credential for type hints when bilibili_api is not available
    class Credential:
        pass

def setup_bilibili_mcp(mcp: FastMCP):
    """Setup Bilibili-related MCP tools."""
    
    # Enable nested event loops for MCP compatibility
    if BILIBILI_API_AVAILABLE:
        nest_asyncio.apply()
    
    def run_async(coro):
        """Helper function to run async code in sync context."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, use nest_asyncio
                return asyncio.run(coro)
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # Fallback to creating new loop
            return asyncio.run(coro)
    
    def get_credential() -> Optional[Credential]:
        """Get Bilibili credential from environment variables."""
        sessdata = os.getenv("BILIBILI_SESSDATA")
        bili_jct = os.getenv("BILIBILI_BILI_JCT")
        buvid3 = os.getenv("BILIBILI_BUVID3")
        
        if sessdata and bili_jct:
            # Extract DedeUserID from SESSDATA
            import urllib.parse
            try:
                decoded_sessdata = urllib.parse.unquote(sessdata)
                dedeuserid = decoded_sessdata.split(',')[0]
                return Credential(
                    sessdata=sessdata, 
                    bili_jct=bili_jct, 
                    buvid3=buvid3,
                    dedeuserid=dedeuserid
                )
            except:
                # Fallback to original method
                return Credential(sessdata=sessdata, bili_jct=bili_jct, buvid3=buvid3)
        return None
    
    @mcp.tool()
    def test_bilibili_credentials() -> str:
        """Test Bilibili API credentials."""
        if not BILIBILI_API_AVAILABLE:
            return "❌ bilibili-api library not installed. Run: pip install bilibili-api"
        
        sessdata = os.getenv("BILIBILI_SESSDATA")
        bili_jct = os.getenv("BILIBILI_BILI_JCT")
        
        if not sessdata or not bili_jct:
            return """❌ Bilibili credentials not found in environment variables
            
Required environment variables:
- BILIBILI_SESSDATA: Your Bilibili SESSDATA cookie
- BILIBILI_BILI_JCT: Your Bilibili bili_jct cookie
- BILIBILI_BUVID3: Your Bilibili buvid3 cookie (optional)

To get these values:
1. Login to bilibili.com in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage tab
4. Find cookies for bilibili.com
5. Copy SESSDATA and bili_jct values"""
        
        return f"✅ Bilibili credentials found: SESSDATA={sessdata[:8]}..., bili_jct={bili_jct[:8]}..."

    @mcp.tool()
    def get_bilibili_config() -> str:
        """Get Bilibili API configuration status."""
        if not BILIBILI_API_AVAILABLE:
            return "❌ bilibili-api library not installed"
        
        credential = get_credential()
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

    @mcp.tool()
    def get_bilibili_user_info(uid: int) -> Dict:
        """Get Bilibili user profile information.
        
        Args:
            uid: Bilibili user ID (UID)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        try:
            # Create user object
            u = user.User(uid=uid)
            
            # Get user info synchronously using asyncio
            try:
                user_info = run_async(u.get_user_info())
                
                return {
                    "uid": uid,
                    "name": user_info.get("name", ""),
                    "face": user_info.get("face", ""),
                    "sign": user_info.get("sign", ""),
                    "level": user_info.get("level", 0),
                    "follower": user_info.get("follower", 0),
                    "following": user_info.get("following", 0),
                    "video_count": user_info.get("video", 0),
                    "official_verify": user_info.get("official", {}),
                    "vip": user_info.get("vip", {}),
                    "live_room": user_info.get("live_room", {})
                }
            except Exception as e:
                return {"error": f"Failed to get user info: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get user info: {str(e)}"}

    @mcp.tool()
    def get_my_bilibili_profile() -> Dict:
        """Get your own Bilibili profile information (requires login)."""
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        credential = get_credential()
        if not credential:
            return {"error": "Bilibili credentials not configured"}
        
        try:
            # Get self info
            try:
                my_info = asyncio.get_event_loop().run_until_complete(user.get_self_info(credential))
                
                return {
                    "uid": my_info.get("mid", 0),
                    "name": my_info.get("name", ""),
                    "face": my_info.get("face", ""),
                    "sign": my_info.get("sign", ""),
                    "level": my_info.get("level", 0),
                    "coins": my_info.get("coins", 0),
                    "experience": my_info.get("experience", {}),
                    "official_verify": my_info.get("official", {}),
                    "vip": my_info.get("vip", {})
                }
            except Exception as e:
                return {"error": f"Failed to get profile: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get profile: {str(e)}"}

    @mcp.tool()
    def get_bilibili_following_list(uid: int = None, page: int = 1) -> Dict:
        """Get Bilibili user's following list.
        
        Args:
            uid: User ID. If not provided, gets your own following list (requires login)
            page: Page number (default: 1)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        credential = get_credential()
        
        try:
            if uid:
                # Get specific user's following list
                u = user.User(uid=uid, credential=credential)
            else:
                # Get own following list (requires login)
                if not credential:
                    return {"error": "Login required to get your own following list"}
                
                # Get self UID first
                try:
                    my_info = asyncio.get_event_loop().run_until_complete(user.get_self_info(credential))
                    my_uid = my_info.get("mid", 0)
                    u = user.User(uid=my_uid, credential=credential)
                except Exception as e:
                    return {"error": f"Failed to get user info: {str(e)}"}
            
            # Get following list
            try:
                following_data = asyncio.get_event_loop().run_until_complete(u.get_followings(pn=page))
                
                following_list = []
                for follow in following_data.get("list", []):
                    following_list.append({
                        "uid": follow.get("mid", 0),
                        "name": follow.get("uname", ""),
                        "face": follow.get("face", ""),
                        "sign": follow.get("sign", ""),
                        "official_verify": follow.get("official_verify", {}),
                        "vip": follow.get("vip", {})
                    })
                
                return {
                    "total": following_data.get("total", 0),
                    "page": page,
                    "following_list": following_list
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get following list: {str(e)}"}

    @mcp.tool()
    def search_bilibili_videos(keyword: str, page: int = 1, order: str = "totalrank") -> Dict:
        """Search Bilibili videos by keyword.
        
        Args:
            keyword: Search keyword
            page: Page number (default: 1)
            order: Sort order - totalrank, click, pubdate, dm, stow (default: totalrank)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        try:
            try:
                search_result = asyncio.run(
                    misc.web_search_by_type(keyword, search_type="video", 
                                           page=page, order=order)
                )
                
                videos = []
                for video_info in search_result.get("result", []):
                    videos.append({
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
                        "url": f"https://www.bilibili.com/video/{video_info.get('bvid', '')}"
                    })
                
                return {
                    "keyword": keyword,
                    "page": page,
                    "total_results": search_result.get("numResults", 0),
                    "videos": videos
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    @mcp.tool()
    def get_bilibili_user_videos(uid: int, page: int = 1) -> Dict:
        """Get videos uploaded by a Bilibili user.
        
        Args:
            uid: User ID
            page: Page number (default: 1)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        try:
            u = user.User(uid=uid)
            
            try:
                videos_data = asyncio.get_event_loop().run_until_complete(u.get_videos(pn=page))
                
                videos = []
                for video_info in videos_data.get("list", {}).get("vlist", []):
                    videos.append({
                        "bvid": video_info.get("bvid", ""),
                        "aid": video_info.get("aid", 0),
                        "title": video_info.get("title", ""),
                        "description": video_info.get("description", ""),
                        "duration": video_info.get("length", ""),
                        "play": video_info.get("play", 0),
                        "danmaku": video_info.get("video_review", 0),
                        "created": video_info.get("created", 0),
                        "pic": video_info.get("pic", ""),
                        "url": f"https://www.bilibili.com/video/{video_info.get('bvid', '')}"
                    })
                
                return {
                    "uid": uid,
                    "page": page,
                    "total_count": videos_data.get("list", {}).get("count", 0),
                    "videos": videos
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get user videos: {str(e)}"}

    @mcp.tool()
    def get_bilibili_video_info(bvid: str) -> Dict:
        """Get detailed information about a Bilibili video.
        
        Args:
            bvid: Bilibili video ID (BVID)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        try:
            v = video.Video(bvid=bvid)
            
            try:
                video_info = asyncio.get_event_loop().run_until_complete(v.get_info())
                
                return {
                    "bvid": bvid,
                    "aid": video_info.get("aid", 0),
                    "title": video_info.get("title", ""),
                    "description": video_info.get("desc", ""),
                    "duration": video_info.get("duration", 0),
                    "owner": {
                        "mid": video_info.get("owner", {}).get("mid", 0),
                        "name": video_info.get("owner", {}).get("name", ""),
                        "face": video_info.get("owner", {}).get("face", "")
                    },
                    "stats": {
                        "view": video_info.get("stat", {}).get("view", 0),
                        "danmaku": video_info.get("stat", {}).get("danmaku", 0),
                        "reply": video_info.get("stat", {}).get("reply", 0),
                        "favorite": video_info.get("stat", {}).get("favorite", 0),
                        "coin": video_info.get("stat", {}).get("coin", 0),
                        "share": video_info.get("stat", {}).get("share", 0),
                        "like": video_info.get("stat", {}).get("like", 0)
                    },
                    "pubdate": video_info.get("pubdate", 0),
                    "pic": video_info.get("pic", ""),
                    "url": f"https://www.bilibili.com/video/{bvid}"
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get video info: {str(e)}"}


    @mcp.tool()
    def get_bilibili_watch_history(page: int = 1) -> Dict:
        """Get your Bilibili watch history (requires login).
        
        Args:
            page: Page number (default: 1)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        credential = get_credential()
        if not credential:
            return {"error": "Bilibili credentials not configured. Login required to access watch history."}
        
        try:
            try:
                # Get watch history using the new API
                history_data = asyncio.get_event_loop().run_until_complete(
                    user.get_self_history(page_num=page, per_page_item=20, credential=credential)
                )
                
                history_videos = []
                # Parse the new API response format
                history_list = history_data.get("list", []) if isinstance(history_data, dict) else history_data
                
                for item in history_list:
                    # Handle all types of history items
                    business_type = item.get("history", {}).get("business", "")
                    
                    if business_type == "archive":  # Video
                        video_info = {
                            "type": "video",
                            "title": item.get("title", ""),
                            "cover": item.get("cover", ""),
                            "uri": item.get("uri", ""),
                            "history": {
                                "oid": item.get("history", {}).get("oid", 0),
                                "bvid": item.get("history", {}).get("bvid", ""),
                                "page": item.get("history", {}).get("page", 1),
                                "cid": item.get("history", {}).get("cid", 0),
                                "part": item.get("history", {}).get("part", ""),
                                "business": item.get("history", {}).get("business", ""),
                                "dt": item.get("history", {}).get("dt", 0)  # Watch timestamp
                            },
                            "progress": item.get("progress", 0),
                            "duration": item.get("duration", 0),
                            "owner": {
                                "mid": item.get("author_mid", 0),
                                "name": item.get("author_name", ""),
                                "face": item.get("author_face", "")
                            },
                            "stat": {
                                "view": item.get("view_count", 0)
                            },
                            "url": f"https://www.bilibili.com/video/{item.get('history', {}).get('bvid', '')}" if item.get('history', {}).get('bvid') else ""
                        }
                        history_videos.append(video_info)
                    elif item.get("history", {}).get("business") == "live":  # Live stream
                        live_info = {
                            "type": "live",
                            "title": item.get("title", ""),
                            "cover": item.get("cover", ""),
                            "uri": item.get("uri", ""),
                            "history": {
                                "oid": item.get("history", {}).get("oid", 0),
                                "business": item.get("history", {}).get("business", ""),
                                "dt": item.get("history", {}).get("dt", 0)
                            },
                            "live_status": item.get("live_status", 0),
                            "owner": {
                                "mid": item.get("author_mid", 0),
                                "name": item.get("author_name", ""),
                                "face": item.get("author_face", "")
                            }
                        }
                        history_videos.append(live_info)
                    else:
                        # Handle other types or unknown types
                        generic_info = {
                            "type": business_type or "unknown",
                            "title": item.get("title", ""),
                            "cover": item.get("cover", ""),
                            "uri": item.get("uri", ""),
                            "history": item.get("history", {}),
                            "progress": item.get("progress", 0),
                            "duration": item.get("duration", 0),
                            "view_at": item.get("view_at", 0),
                            "owner": {
                                "mid": item.get("author_mid", 0),
                                "name": item.get("author_name", ""),
                                "face": item.get("author_face", "")
                            }
                        }
                        history_videos.append(generic_info)
                
                return {
                    "page": page,
                    "total_count": len(history_videos),
                    "watch_history": history_videos
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get watch history: {str(e)}"}

    @mcp.tool()
    def get_bilibili_favorites(uid: int = None, page: int = 1) -> Dict:
        """Get Bilibili user's favorite folders and videos.
        
        Args:
            uid: User ID. If not provided, gets your own favorites (requires login)
            page: Page number (default: 1)
        """
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        credential = get_credential()
        
        try:
            if uid:
                # Get specific user's public favorites
                u = user.User(uid=uid, credential=credential)
            else:
                # Get own favorites (requires login)
                if not credential:
                    return {"error": "Login required to get your own favorites"}
                
                # Get self UID first
                try:
                    my_info = asyncio.get_event_loop().run_until_complete(user.get_self_info(credential))
                    my_uid = my_info.get("mid", 0)
                    u = user.User(uid=my_uid, credential=credential)
                except Exception as e:
                    return {"error": f"Failed to get user info: {str(e)}"}
            
            # Get favorite folders
            try:
                # Get favorite folders list
                folders_data = asyncio.get_event_loop().run_until_complete(u.get_favorite_list(pn=page))
                
                favorite_folders = []
                for folder in folders_data.get("list", []):
                    folder_info = {
                        "id": folder.get("id", 0),
                        "fid": folder.get("fid", 0),
                        "title": folder.get("title", ""),
                        "description": folder.get("intro", ""),
                        "cover": folder.get("cover", ""),
                        "media_count": folder.get("media_count", 0),
                        "view_count": folder.get("view_count", 0),
                        "like_count": folder.get("like_count", 0),
                        "fav_state": folder.get("fav_state", 0),
                        "ctime": folder.get("ctime", 0),
                        "mtime": folder.get("mtime", 0),
                        "state": folder.get("state", 0),
                        "type": folder.get("type", 0),
                        "upper": {
                            "mid": folder.get("upper", {}).get("mid", 0),
                            "name": folder.get("upper", {}).get("name", ""),
                            "face": folder.get("upper", {}).get("face", "")
                        }
                    }
                    favorite_folders.append(folder_info)
                
                return {
                    "uid": uid or my_uid,
                    "page": page,
                    "total_count": folders_data.get("count", 0),
                    "favorite_folders": favorite_folders
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get favorites: {str(e)}"}

    @mcp.tool()
    def get_bilibili_toview_list() -> Dict:
        """Get your Bilibili 'to view' (稍后再看) list (requires login)."""
        if not BILIBILI_API_AVAILABLE:
            return {"error": "bilibili-api library not installed"}
        
        credential = get_credential()
        if not credential:
            return {"error": "Bilibili credentials not configured. Login required to access toview list."}
        
        try:
            try:
                # Get toview list
                toview_data = asyncio.get_event_loop().run_until_complete(user.get_toview_list(credential=credential))
                
                toview_videos = []
                for video_info in toview_data.get("list", []):
                    video_data = {
                        "bvid": video_info.get("bvid", ""),
                        "aid": video_info.get("aid", 0),
                        "title": video_info.get("title", ""),
                        "description": video_info.get("desc", ""),
                        "duration": video_info.get("duration", 0),
                        "owner": {
                            "mid": video_info.get("owner", {}).get("mid", 0),
                            "name": video_info.get("owner", {}).get("name", ""),
                            "face": video_info.get("owner", {}).get("face", "")
                        },
                        "stat": {
                            "view": video_info.get("stat", {}).get("view", 0),
                            "danmaku": video_info.get("stat", {}).get("danmaku", 0),
                            "reply": video_info.get("stat", {}).get("reply", 0),
                            "favorite": video_info.get("stat", {}).get("favorite", 0),
                            "coin": video_info.get("stat", {}).get("coin", 0),
                            "share": video_info.get("stat", {}).get("share", 0),
                            "like": video_info.get("stat", {}).get("like", 0)
                        },
                        "pubdate": video_info.get("pubdate", 0),
                        "add_at": video_info.get("add_at", 0),  # Added to toview timestamp
                        "progress": video_info.get("progress", 0),  # Watch progress
                        "pic": video_info.get("pic", ""),
                        "url": f"https://www.bilibili.com/video/{video_info.get('bvid', '')}"
                    }
                    toview_videos.append(video_data)
                
                return {
                    "total_count": toview_data.get("count", 0),
                    "toview_videos": toview_videos
                }
            except Exception as e:
                return {"error": f"Failed to execute: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to get toview list: {str(e)}"}
