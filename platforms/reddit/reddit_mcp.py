"""
Reddit MCP tools for PersonalizationMCP.

This module provides Reddit API integration with OAuth2 authentication
and personal data access capabilities.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import os
from .reddit_oauth_helper import RedditOAuthHelper
from .reddit_token_manager import RedditTokenManager


def setup_reddit_mcp(mcp: FastMCP) -> None:
    """Set up Reddit MCP tools."""
    
    async def _ensure_valid_oauth_token() -> Optional[str]:
        """Ensure we have a valid OAuth token, refreshing if necessary."""
        token_manager = RedditTokenManager("/Users/liangweiyang/Desktop/works/PersonalizationMCP/platforms/reddit/reddit_tokens.json")
        return token_manager.get_valid_access_token()
    
    async def _make_reddit_api_request(endpoint: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Make authenticated request to Reddit API."""
        if not access_token:
            access_token = await _ensure_valid_oauth_token()
            if not access_token:
                return {
                    "status": "error",
                    "message": "No valid OAuth token available. Please complete OAuth authentication first."
                }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "PersonalizationMCP/1.0.0 (Personal data aggregator)"
        }
        
        url = f"https://oauth.reddit.com{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    @mcp.tool()
    def test_reddit_credentials(random_string: str = "") -> Dict[str, Any]:
        """Test Reddit API credentials."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return {"result": "❌ Reddit API credentials not found in config"}
        
        # Mask the client ID for security
        masked_id = client_id[:8] + "..."
        return {"result": f"✅ Reddit API credentials found: Client ID={masked_id}"}
    
    @mcp.tool()
    def get_reddit_config(random_string: str = "") -> Dict[str, Any]:
        """Get Reddit API configuration status."""
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
        
        if not client_id or not client_secret:
            return {
                "status": "not_configured",
                "message": "Reddit API not configured"
            }
        
        return {
            "status": "configured",
            "has_client_id": bool(client_id),
            "has_client_secret": bool(client_secret),
            "has_redirect_uri": bool(redirect_uri),
            "redirect_uri": redirect_uri
        }
    
    @mcp.tool()
    def setup_reddit_oauth(client_id: str, client_secret: str, redirect_uri: str = "") -> Dict[str, Any]:
        """
        Setup Reddit OAuth2 authentication (initial authentication).
        
        Args:
            client_id: Reddit Client ID
            client_secret: Reddit Client Secret
            redirect_uri: Optional redirect URI (defaults to environment variable or http://localhost:8888/callback)
        """
        # Use provided redirect_uri or get from environment or use default
        if not redirect_uri:
            redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8888/callback")
        
        try:
            oauth_helper = RedditOAuthHelper(client_id, client_secret, redirect_uri)
            auth_data = oauth_helper.generate_auth_url()
            
            return {
                "status": "success",
                "message": "Please visit the following URL to authorize the application:",
                "authorization_url": auth_data["auth_url"],
                "redirect_uri": auth_data["redirect_uri"],
                "state": auth_data["state"],
                "next_step": "After authorization, you'll be redirected to a URL with a 'code' parameter. Copy that code and use complete_reddit_oauth function."
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to setup Reddit OAuth: {str(e)}"
            }
    
    @mcp.tool()
    def complete_reddit_oauth(client_id: str, client_secret: str, authorization_code: str, redirect_uri: str = "") -> Dict[str, Any]:
        """
        Complete Reddit OAuth2 authentication (get tokens).
        
        Args:
            client_id: Reddit Client ID
            client_secret: Reddit Client Secret
            authorization_code: Authorization code from Reddit callback
            redirect_uri: Optional redirect URI (should match the one used in setup_reddit_oauth)
        """
        # Use provided redirect_uri or get from environment or use default
        if not redirect_uri:
            redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8888/callback")
        
        try:
            oauth_helper = RedditOAuthHelper(client_id, client_secret, redirect_uri)
            
            # Exchange code for tokens
            tokens = asyncio.run(oauth_helper.exchange_code_for_tokens(authorization_code))
            
            # Save tokens
            token_manager = RedditTokenManager("/Users/liangweiyang/Desktop/works/PersonalizationMCP/platforms/reddit/reddit_tokens.json")
            token_manager.save_tokens(tokens)
            
            return {
                "status": "success",
                "message": "✅ Reddit OAuth authentication completed successfully!",
                "tokens_saved": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to complete Reddit OAuth: {str(e)}"
            }
    
    @mcp.tool()
    def refresh_reddit_token(random_string: str = "") -> Dict[str, Any]:
        """Manually refresh Reddit access token."""
        try:
            token_manager = RedditTokenManager("/Users/liangweiyang/Desktop/works/PersonalizationMCP/platforms/reddit/reddit_tokens.json")
            tokens = token_manager.load_tokens()
            
            if not tokens or "refresh_token" not in tokens:
                return {
                    "status": "error",
                    "message": "No refresh token available"
                }
            
            new_access_token = token_manager._refresh_token(tokens["refresh_token"])
            
            if new_access_token:
                return {
                    "status": "success",
                    "message": "✅ Reddit token refreshed successfully"
                }
            else:
                return {
                    "status": "error", 
                    "message": "Failed to refresh token"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Token refresh failed: {str(e)}"
            }
    
    @mcp.tool()
    def auto_refresh_reddit_token_if_needed(random_string: str = "") -> Dict[str, Any]:
        """Auto check and refresh Reddit access token if needed."""
        try:
            token_manager = RedditTokenManager("/Users/liangweiyang/Desktop/works/PersonalizationMCP/platforms/reddit/reddit_tokens.json")
            access_token = token_manager.get_valid_access_token()
            
            if access_token:
                return {
                    "status": "success",
                    "message": "✅ Reddit token is valid or has been refreshed"
                }
            else:
                return {
                    "status": "error",
                    "message": "No valid token available, please re-authenticate"
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Auto refresh failed: {str(e)}"
            }
    
    @mcp.tool()
    def get_reddit_token_status(random_string: str = "") -> Dict[str, Any]:
        """Get Reddit token status information."""
        try:
            token_manager = RedditTokenManager("/Users/liangweiyang/Desktop/works/PersonalizationMCP/platforms/reddit/reddit_tokens.json")
            return {
                "status": "success",
                "token_info": token_manager.get_token_status()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get token status: {str(e)}"
            }
    
    # Basic Reddit API tools
    @mcp.tool()
    def get_current_user_profile(access_token: str = "") -> Dict[str, Any]:
        """Get current user's Reddit profile information."""
        try:
            result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "user_profile": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user profile: {str(e)}"
            }
    
    @mcp.tool() 
    def get_user_subreddits(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's subscribed subreddits.
        
        Args:
            access_token: Optional access token
            limit: Number of subreddits to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))  # Ensure limit is between 1 and 100
            endpoint = f"/subreddits/mine/subscriber?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "subreddits": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user subreddits: {str(e)}"
            }
    
    # === 用户基本信息 API ===
    
    @mcp.tool()
    def get_user_trophies(access_token: str = "") -> Dict[str, Any]:
        """Get current user's Reddit trophies and achievements."""
        try:
            result = asyncio.run(_make_reddit_api_request("/api/v1/me/trophies", access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "trophies": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user trophies: {str(e)}"
            }
    
    @mcp.tool()
    def get_user_preferences(access_token: str = "") -> Dict[str, Any]:
        """Get current user's Reddit preferences and settings."""
        try:
            result = asyncio.run(_make_reddit_api_request("/api/v1/me/prefs", access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "preferences": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user preferences: {str(e)}"
            }
    
    @mcp.tool()
    def get_user_karma_breakdown(access_token: str = "") -> Dict[str, Any]:
        """Get user's karma breakdown by subreddit."""
        try:
            result = asyncio.run(_make_reddit_api_request("/api/v1/me/karma", access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "karma_breakdown": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get karma breakdown: {str(e)}"
            }
    
    # === 订阅和社区 API ===
    
    @mcp.tool()
    def get_moderated_subreddits(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get subreddits where user is a moderator.
        
        Args:
            access_token: Optional access token
            limit: Number of subreddits to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/subreddits/mine/moderator?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "moderated_subreddits": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get moderated subreddits: {str(e)}"
            }
    
    @mcp.tool()
    def get_contributor_subreddits(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get subreddits where user has contributor permissions.
        
        Args:
            access_token: Optional access token
            limit: Number of subreddits to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/subreddits/mine/contributor?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "contributor_subreddits": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get contributor subreddits: {str(e)}"
            }
    
    # === 内容历史 API ===
    
    @mcp.tool()
    def get_user_submitted_posts(username: str = "", access_token: str = "", limit: int = 100, sort: str = "new") -> Dict[str, Any]:
        """
        Get user's submitted posts.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of posts to return (1-100, default 100)
            sort: Sort order (new, hot, top, default: new)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/submitted?limit={limit}&sort={sort}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "submitted_posts": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get submitted posts: {str(e)}"
            }
    
    @mcp.tool()
    def get_user_comments(username: str = "", access_token: str = "", limit: int = 100, sort: str = "new") -> Dict[str, Any]:
        """
        Get user's comments.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of comments to return (1-100, default 100)
            sort: Sort order (new, hot, top, default: new)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/comments?limit={limit}&sort={sort}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "comments": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get comments: {str(e)}"
            }
    
    @mcp.tool()
    def get_user_overview(username: str = "", access_token: str = "", limit: int = 100, sort: str = "new") -> Dict[str, Any]:
        """
        Get user's posts and comments overview (mixed timeline).
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of items to return (1-100, default 100)
            sort: Sort order (new, hot, top, default: new)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/overview?limit={limit}&sort={sort}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "overview": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user overview: {str(e)}"
            }
    
    # === 保存和收藏 API ===
    
    @mcp.tool()
    def get_saved_content(username: str = "", access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's saved posts and comments.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of items to return (1-100, default 100)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/saved?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "saved_content": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get saved content: {str(e)}"
            }
    
    @mcp.tool()
    def get_hidden_posts(username: str = "", access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's hidden posts.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of items to return (1-100, default 100)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/hidden?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "hidden_posts": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get hidden posts: {str(e)}"
            }
    
    # === 投票历史 API ===
    
    @mcp.tool()
    def get_upvoted_content(username: str = "", access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's upvoted posts.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of items to return (1-100, default 100)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/upvoted?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "upvoted_content": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get upvoted content: {str(e)}"
            }
    
    @mcp.tool()
    def get_downvoted_content(username: str = "", access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's downvoted posts.
        
        Args:
            username: Username (optional, defaults to current user)
            access_token: Optional access token
            limit: Number of items to return (1-100, default 100)
        """
        try:
            if not username:
                # Get current user's username first
                user_result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
                if "status" in user_result and user_result["status"] == "error":
                    return user_result
                username = user_result.get("name", "")
            
            limit = max(1, min(limit, 100))
            endpoint = f"/user/{username}/downvoted?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "downvoted_content": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get downvoted content: {str(e)}"
            }
    
    # === 消息通知 API ===
    
    @mcp.tool()
    def get_inbox_messages(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's inbox messages (requires privatemessages scope).
        
        Args:
            access_token: Optional access token
            limit: Number of messages to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/message/inbox?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "inbox_messages": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get inbox messages: {str(e)}"
            }
    
    @mcp.tool()
    def get_unread_messages(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's unread messages (requires privatemessages scope).
        
        Args:
            access_token: Optional access token
            limit: Number of messages to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/message/unread?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "unread_messages": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get unread messages: {str(e)}"
            }
    
    @mcp.tool()
    def get_sent_messages(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        Get user's sent messages (requires privatemessages scope).
        
        Args:
            access_token: Optional access token
            limit: Number of messages to return (1-100, default 100)
        """
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/message/sent?limit={limit}"
            
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if "status" in result and result["status"] == "error":
                return result
            
            return {
                "status": "success",
                "sent_messages": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get sent messages: {str(e)}"
            }
