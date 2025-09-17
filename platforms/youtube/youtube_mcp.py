"""
YouTube MCP Server Module
Provides YouTube API integration for personalized video consumption data.
"""

import os
import httpx
from typing import Dict, List
from mcp.server.fastmcp import FastMCP
from .youtube_token_manager import get_token_manager

# YouTube API configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def _get_valid_oauth_token(access_token: str = None) -> str:
    """
    获取有效的OAuth令牌的统一逻辑
    优先级：
    1. 显式传入的access_token（如果不为None且不为空字符串）
    2. 令牌管理器自动获取的有效令牌（优先使用，自动刷新）
    3. 环境变量中的令牌（作为备用）
    """
    # 1. 如果显式传入了有效的access_token，直接使用
    if access_token and access_token.strip() and access_token != "null":
        return access_token
    
    # 2. 优先尝试使用令牌管理器获取有效令牌（自动刷新）
    try:
        token_manager = get_token_manager()
        managed_token = token_manager.get_valid_access_token()
        if managed_token:
            return managed_token
    except Exception as e:
        print(f"⚠️ 令牌管理器获取失败: {e}")
    
    # 3. 备用：尝试从环境变量获取
    env_token = os.getenv("YOUTUBE_ACCESS_TOKEN")
    if env_token and env_token.strip():
        return env_token
    
    return None

def _ensure_valid_oauth_token(access_token: str = None) -> tuple[str, dict]:
    """
    确保获取有效的OAuth令牌，如果需要会自动刷新
    返回: (token, status_info)
    """
    # 首先尝试获取令牌
    token = _get_valid_oauth_token(access_token)
    
    if not token:
        return None, {
            "error": "OAuth2 access token required",
            "note": "This endpoint requires user authentication",
            "required_scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
            "setup_instructions": "Please provide access_token parameter or set up OAuth2 authentication"
        }
    
    # 如果没有显式传入token，检查是否需要自动刷新
    if not (access_token and access_token.strip() and access_token != "null"):
        try:
            token_manager = get_token_manager()
            status = token_manager.get_token_status()
            
            # 如果令牌即将过期（5分钟内），自动刷新
            if not isinstance(status, dict) or "error" in status:
                pass  # 继续使用现有token
            elif status.get("needs_refresh", False) or status.get("remaining_time", 0) <= 300:
                print(f"🔄 检测到令牌即将过期，自动刷新中...")
                refreshed_token = token_manager.get_valid_access_token()
                if refreshed_token:
                    token = refreshed_token
                    print(f"✅ 令牌自动刷新成功")
        except Exception as e:
            print(f"⚠️ 自动刷新检查失败，使用现有令牌: {e}")
    
    return token, None


def setup_youtube_mcp(mcp: FastMCP):
    """Setup YouTube-related MCP tools."""
    
    @mcp.tool()
    def test_youtube_credentials() -> str:
        """Test YouTube API credentials."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return "❌ YouTube API key not found in environment variables"
        
        return f"✅ YouTube API key found: Key={api_key[:8]}..."
    
    @mcp.tool()
    def refresh_youtube_token() -> Dict:
        """手动刷新YouTube访问令牌"""
        token_manager = get_token_manager()
        new_token = token_manager.force_refresh()
        
        if new_token:
            return {
                "success": True,
                "message": "✅ 成功刷新YouTube访问令牌",
                "new_token": new_token[:30] + "..."
            }
        else:
            return {
                "success": False,
                "message": "❌ 刷新YouTube访问令牌失败"
            }
    
    @mcp.tool()
    def auto_refresh_youtube_token_if_needed() -> Dict:
        """自动检查并刷新YouTube访问令牌（如果需要的话）"""
        try:
            token_manager = get_token_manager()
            
            # 检查当前令牌状态
            status = token_manager.get_token_status()
            
            if "error" in status:
                return {
                    "success": False,
                    "message": "❌ 无法获取令牌状态",
                    "error": status["error"]
                }
            
            needs_refresh = status.get("needs_refresh", False)
            remaining_time = status.get("remaining_time", 0)
            
            if needs_refresh or remaining_time <= 300:  # 5分钟内过期
                print(f"🔄 令牌即将过期（剩余 {remaining_time} 秒），开始自动刷新...")
                
                # 获取有效令牌（会自动刷新）
                new_token = token_manager.get_valid_access_token()
                
                if new_token:
                    return {
                        "success": True,
                        "action": "refreshed",
                        "message": "✅ 自动刷新YouTube访问令牌成功",
                        "new_token": new_token[:30] + "...",
                        "remaining_time": 3600  # 新令牌通常有效1小时
                    }
                else:
                    return {
                        "success": False,
                        "action": "refresh_failed",
                        "message": "❌ 自动刷新YouTube访问令牌失败"
                    }
            else:
                return {
                    "success": True,
                    "action": "no_refresh_needed",
                    "message": f"✅ 令牌仍然有效，剩余 {remaining_time} 秒",
                    "remaining_time": remaining_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ 自动刷新过程中出错: {str(e)}",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_youtube_token_status() -> Dict:
        """获取YouTube令牌状态信息"""
        token_manager = get_token_manager()
        return token_manager.get_token_status()
    
    @mcp.tool()
    def setup_youtube_oauth(client_id: str, client_secret: str) -> Dict:
        """
        设置YouTube OAuth2认证（首次认证）
        
        Args:
            client_id: Google OAuth2 Client ID
            client_secret: Google OAuth2 Client Secret
            
        Returns:
            包含认证状态和下一步操作的字典
        """
        try:
            from .youtube_oauth_helper import get_device_code, poll_for_token
            import json
            import os
            
            # 验证输入
            if not client_id or not client_secret:
                return {
                    "success": False,
                    "error": "Client ID和Client Secret都是必需的",
                    "next_steps": "请提供有效的Google OAuth2凭据"
                }
            
            # 获取设备代码
            print("🔄 正在获取设备代码...")
            device_info = get_device_code(client_id)
            
            if not device_info or 'device_code' not in device_info:
                return {
                    "success": False,
                    "error": "获取设备代码失败",
                    "details": device_info,
                    "troubleshooting": [
                        "检查Client ID是否正确",
                        "确保在Google Cloud Console中启用了YouTube Data API v3",
                        "确保OAuth客户端类型为'TV and Limited Input device'"
                    ]
                }
            
            # 返回用户需要执行的操作
            return {
                "success": True,
                "status": "waiting_for_authorization",
                "verification_url": device_info.get('verification_url', 'https://www.google.com/device'),
                "user_code": device_info.get('user_code'),
                "device_code": device_info.get('device_code'),
                "expires_in": device_info.get('expires_in', 1800),
                "interval": device_info.get('interval', 5),
                "instructions": [
                    f"1. 在任何设备上打开浏览器访问: {device_info.get('verification_url', 'https://www.google.com/device')}",
                    f"2. 输入代码: {device_info.get('user_code')}",
                    "3. 使用你的Google账户登录并授权PersonalizationMCP",
                    "4. 完成授权后，调用 complete_youtube_oauth 工具完成设置"
                ],
                "next_tool": "complete_youtube_oauth",
                "temp_data": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "device_code": device_info.get('device_code')
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"设置OAuth认证时出错: {str(e)}",
                "troubleshooting": [
                    "检查网络连接",
                    "验证Google Cloud Console配置",
                    "确保API配额未超限"
                ]
            }
    
    @mcp.tool()
    def complete_youtube_oauth(client_id: str, client_secret: str, device_code: str) -> Dict:
        """
        完成YouTube OAuth2认证（获取令牌）
        
        Args:
            client_id: Google OAuth2 Client ID
            client_secret: Google OAuth2 Client Secret  
            device_code: 从setup_youtube_oauth获得的设备代码
            
        Returns:
            认证完成状态
        """
        try:
            from .youtube_oauth_helper import poll_for_token
            import json
            import os
            
            print("⏳ 正在等待用户授权...")
            
            # 轮询获取令牌
            tokens = poll_for_token(client_id, client_secret, device_code, interval=5)
            
            if not tokens or 'access_token' not in tokens:
                return {
                    "success": False,
                    "error": "获取访问令牌失败",
                    "possible_reasons": [
                        "用户未完成授权",
                        "设备代码已过期",
                        "授权被拒绝"
                    ],
                    "next_steps": "请重新运行 setup_youtube_oauth 开始新的认证流程"
                }
            
            # 保存令牌到文件
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'access_token': tokens['access_token'],
                'refresh_token': tokens.get('refresh_token'),
                'token_type': tokens.get('token_type', 'Bearer'),
                'expires_in': tokens.get('expires_in', 3600),
                'scope': tokens.get('scope', 'https://www.googleapis.com/auth/youtube.readonly'),
                'refreshed_at': int(__import__('time').time())
            }
            
            # 保存到youtube_tokens.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            tokens_file = os.path.join(current_dir, 'youtube_tokens.json')
            
            with open(tokens_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # 更新环境变量
            os.environ['YOUTUBE_ACCESS_TOKEN'] = tokens['access_token']
            
            return {
                "success": True,
                "message": "✅ YouTube OAuth2认证设置完成！",
                "token_info": {
                    "access_token": f"{tokens['access_token'][:30]}...",
                    "token_type": token_data['token_type'],
                    "expires_in": f"{token_data['expires_in']}秒",
                    "scope": token_data['scope']
                },
                "features_unlocked": [
                    "获取点赞视频 (get_youtube_liked_videos)",
                    "获取订阅列表 (get_youtube_subscriptions)", 
                    "获取播放列表 (get_youtube_playlists)"
                ],
                "auto_refresh": "令牌将自动刷新，无需手动管理"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"完成OAuth认证时出错: {str(e)}",
                "troubleshooting": [
                    "确保已完成浏览器授权",
                    "检查设备代码是否正确",
                    "验证网络连接"
                ]
            }

    @mcp.tool()
    def get_youtube_subscriptions(access_token: str = None) -> Dict:
        """Get user's YouTube channel subscriptions (requires OAuth2 access token)."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        # 使用新的自动刷新逻辑
        oauth_token, error_info = _ensure_valid_oauth_token(access_token)
        
        if not oauth_token:
            return error_info
        
        try:
            url = "https://www.googleapis.com/youtube/v3/subscriptions"
            params = {
                "key": api_key,
                "part": "snippet,contentDetails",
                "mine": "true",
                "maxResults": 50
            }
            headers = {
                "Authorization": f"Bearer {oauth_token}"
            }
            
            response = httpx.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data:
                subscriptions = []
                for item in data["items"]:
                    sub_info = {
                        "channel_id": item["snippet"]["resourceId"]["channelId"],
                        "channel_title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "subscribed_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "channel_url": f"https://www.youtube.com/channel/{item['snippet']['resourceId']['channelId']}"
                    }
                    subscriptions.append(sub_info)
                
                return {
                    "total_subscriptions": len(subscriptions),
                    "subscriptions": subscriptions
                }
            else:
                return {"message": "No subscriptions found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch subscriptions: {str(e)}"}


    @mcp.tool()
    def get_youtube_playlists(access_token: str = None) -> Dict:
        """Get user's YouTube playlists (requires OAuth2 access token)."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        # 改进的令牌获取逻辑
        oauth_token = _get_valid_oauth_token(access_token)
        
        if not oauth_token:
            return {
                "error": "OAuth2 access token required",
                "note": "This endpoint requires user authentication",
                "required_scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
                "setup_instructions": "Please provide access_token parameter or set YOUTUBE_ACCESS_TOKEN environment variable"
            }
        
        try:
            url = "https://www.googleapis.com/youtube/v3/playlists"
            params = {
                "key": api_key,
                "part": "snippet,contentDetails",
                "mine": "true",
                "maxResults": 50
            }
            headers = {
                "Authorization": f"Bearer {oauth_token}"
            }
            
            response = httpx.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data:
                playlists = []
                for item in data["items"]:
                    playlist_info = {
                        "playlist_id": item["id"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"],
                        "created_at": item["snippet"]["publishedAt"],
                        "video_count": item["contentDetails"]["itemCount"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"] if "thumbnails" in item["snippet"] else None,
                        "url": f"https://www.youtube.com/playlist?list={item['id']}"
                    }
                    playlists.append(playlist_info)
                
                return {
                    "total_playlists": len(playlists),
                    "playlists": playlists
                }
            else:
                return {"message": "No playlists found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch playlists: {str(e)}"}

    @mcp.tool()
    def get_youtube_liked_videos(access_token: str = None, max_results: int = 20) -> Dict:
        """Get user's liked YouTube videos (requires OAuth2 access token)."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        # 改进的令牌获取逻辑
        oauth_token = _get_valid_oauth_token(access_token)
        
        if not oauth_token:
            return {
                "error": "OAuth2 access token required",
                "note": "This endpoint requires user authentication",
                "required_scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
                "setup_instructions": "Please provide access_token parameter or set YOUTUBE_ACCESS_TOKEN environment variable"
            }
        
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "key": api_key,
                "part": "snippet,statistics",
                "myRating": "like",
                "maxResults": min(max_results, 50)
            }
            headers = {
                "Authorization": f"Bearer {oauth_token}"
            }
            
            response = httpx.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data:
                liked_videos = []
                for item in data["items"]:
                    video_info = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "view_count": item["statistics"].get("viewCount", "N/A"),
                        "like_count": item["statistics"].get("likeCount", "N/A"),
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']}"
                    }
                    liked_videos.append(video_info)
                
                return {
                    "total_liked_videos": len(liked_videos),
                    "liked_videos": liked_videos
                }
            else:
                return {"message": "No liked videos found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch liked videos: {str(e)}"}

    @mcp.tool()
    def search_youtube_videos(query: str, max_results: int = 10) -> Dict:
        """Search YouTube videos by query."""
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
                "maxResults": min(max_results, 50),  # API limit
                "order": "relevance"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data:
                videos = []
                for item in data["items"]:
                    video_info = {
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "description": item["snippet"]["description"][:200] + "..." if len(item["snippet"]["description"]) > 200 else item["snippet"]["description"],
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    }
                    videos.append(video_info)
                
                return {
                    "query": query,
                    "total_results": data.get("pageInfo", {}).get("totalResults", 0),
                    "videos": videos
                }
            else:
                return {"error": "No videos found"}
                
        except Exception as e:
            return {"error": f"Failed to search videos: {str(e)}"}

    @mcp.tool()
    def get_video_details(video_id: str) -> Dict:
        """Get detailed information about a specific YouTube video."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        if not video_id:
            return {"error": "Video ID is required"}
        
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "key": api_key,
                "id": video_id,
                "part": "snippet,statistics,contentDetails"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data and data["items"]:
                video = data["items"][0]
                
                # Parse duration (PT4M13S format)
                duration = video["contentDetails"]["duration"]
                
                return {
                    "video_id": video_id,
                    "title": video["snippet"]["title"],
                    "channel": video["snippet"]["channelTitle"],
                    "description": video["snippet"]["description"],
                    "published_at": video["snippet"]["publishedAt"],
                    "duration": duration,
                    "view_count": video["statistics"].get("viewCount", "N/A"),
                    "like_count": video["statistics"].get("likeCount", "N/A"),
                    "comment_count": video["statistics"].get("commentCount", "N/A"),
                    "thumbnail": video["snippet"]["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "tags": video["snippet"].get("tags", [])
                }
            else:
                return {"error": "Video not found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch video details: {str(e)}"}

    @mcp.tool()
    def get_channel_info(channel_id: str) -> Dict:
        """Get information about a YouTube channel."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        if not api_key:
            return {"error": "YouTube API key not configured"}
        
        if not channel_id:
            return {"error": "Channel ID is required"}
        
        try:
            url = "https://www.googleapis.com/youtube/v3/channels"
            params = {
                "key": api_key,
                "id": channel_id,
                "part": "snippet,statistics,contentDetails"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data and data["items"]:
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
                    "country": channel["snippet"].get("country", "N/A")
                }
            else:
                return {"error": "Channel not found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch channel info: {str(e)}"}

    @mcp.tool()
    def get_trending_videos(region_code: str = "US", max_results: int = 10) -> Dict:
        """Get trending YouTube videos for a specific region."""
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
                "maxResults": min(max_results, 50)
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "items" in data:
                videos = []
                for item in data["items"]:
                    video_info = {
                        "video_id": item["id"],
                        "title": item["snippet"]["title"],
                        "channel": item["snippet"]["channelTitle"],
                        "view_count": item["statistics"].get("viewCount", "N/A"),
                        "like_count": item["statistics"].get("likeCount", "N/A"),
                        "published_at": item["snippet"]["publishedAt"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "url": f"https://www.youtube.com/watch?v={item['id']}"
                    }
                    videos.append(video_info)
                
                return {
                    "region": region_code,
                    "trending_videos": videos
                }
            else:
                return {"error": "No trending videos found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch trending videos: {str(e)}"}

    @mcp.tool()
    def get_youtube_config() -> str:
        """Get YouTube API configuration status."""
        api_key = os.getenv("YOUTUBE_API_KEY")
        
        config_info = f"""YouTube API Configuration:
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
        return config_info
