"""Reddit service layer used by CLI and MCP adapter."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import os

from platforms.reddit.reddit_token_manager import RedditTokenManager


TOKEN_PATH = str((Path(__file__).resolve().parents[1] / "platforms" / "reddit" / "reddit_tokens.json"))


async def _ensure_valid_oauth_token() -> Optional[str]:
    token_manager = RedditTokenManager(TOKEN_PATH)
    return token_manager.get_valid_access_token()


async def _make_reddit_api_request(endpoint: str, access_token: Optional[str] = None) -> Dict[str, Any]:
    if not access_token:
        access_token = await _ensure_valid_oauth_token()
        if not access_token:
            return {
                "status": "error",
                "message": "No valid OAuth token available. Please complete OAuth authentication first.",
            }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "PersonalizationMCP/1.0.0 (Personal data aggregator)",
    }
    url = f"https://oauth.reddit.com{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


class RedditService:
    @staticmethod
    def credentials_status() -> Dict[str, Any]:
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        if not client_id or not client_secret:
            return {"result": "❌ Reddit API credentials not found in config"}
        return {"result": f"✅ Reddit API credentials found: Client ID={client_id[:8]}..."}

    @staticmethod
    def get_config() -> Dict[str, Any]:
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        redirect_uri = os.getenv("REDDIT_REDIRECT_URI")
        if not client_id or not client_secret:
            return {"status": "not_configured", "message": "Reddit API not configured"}
        return {
            "status": "configured",
            "has_client_id": bool(client_id),
            "has_client_secret": bool(client_secret),
            "has_redirect_uri": bool(redirect_uri),
            "redirect_uri": redirect_uri,
        }

    @staticmethod
    def refresh_token() -> Dict[str, Any]:
        try:
            token_manager = RedditTokenManager(TOKEN_PATH)
            tokens = token_manager.load_tokens()
            if not tokens or "refresh_token" not in tokens:
                return {"status": "error", "message": "No refresh token available"}

            new_access_token = token_manager._refresh_token(tokens["refresh_token"])
            if new_access_token:
                return {"status": "success", "message": "✅ Reddit token refreshed successfully"}
            return {"status": "error", "message": "Failed to refresh token"}
        except Exception as e:
            return {"status": "error", "message": f"Token refresh failed: {str(e)}"}

    @staticmethod
    def auto_refresh_if_needed() -> Dict[str, Any]:
        try:
            token_manager = RedditTokenManager(TOKEN_PATH)
            access_token = token_manager.get_valid_access_token()
            if access_token:
                return {"status": "success", "message": "✅ Reddit token is valid or has been refreshed"}
            return {"status": "error", "message": "No valid token available, please re-authenticate"}
        except Exception as e:
            return {"status": "error", "message": f"Auto refresh failed: {str(e)}"}

    @staticmethod
    def token_status() -> Dict[str, Any]:
        try:
            token_manager = RedditTokenManager(TOKEN_PATH)
            return {"status": "success", "token_info": token_manager.get_token_status()}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get token status: {str(e)}"}

    @staticmethod
    def get_current_user_profile(access_token: str = "") -> Dict[str, Any]:
        try:
            result = asyncio.run(_make_reddit_api_request("/api/v1/me", access_token or None))
            if result.get("status") == "error":
                return result
            return {"status": "success", "user_profile": result}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get user profile: {str(e)}"}

    @staticmethod
    def get_user_subreddits(access_token: str = "", limit: int = 100) -> Dict[str, Any]:
        try:
            limit = max(1, min(limit, 100))
            endpoint = f"/subreddits/mine/subscriber?limit={limit}"
            result = asyncio.run(_make_reddit_api_request(endpoint, access_token or None))
            if result.get("status") == "error":
                return result
            return {"status": "success", "subreddits": result}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get user subreddits: {str(e)}"}
