"""
Reddit token management system.

This module handles Reddit OAuth2 token storage, retrieval, and automatic refresh.
"""

import json
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path


class RedditTokenManager:
    """Manages Reddit OAuth2 tokens with automatic refresh."""
    
    def __init__(self, token_file: str = "platforms/reddit/reddit_tokens.json"):
        """
        Initialize token manager.
        
        Args:
            token_file: Path to token storage file
        """
        self.token_file = Path(token_file)
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_tokens(self, token_data: Dict[str, Any]) -> None:
        """
        Save tokens to file.
        
        Args:
            token_data: Token response from Reddit API
        """
        # Add expiration timestamp
        if "expires_in" in token_data:
            token_data["expires_at"] = time.time() + token_data["expires_in"]
        
        # Add refresh timestamp
        token_data["refreshed_at"] = time.time()
        
        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)
    
    def load_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Load tokens from file.
        
        Returns:
            Token data or None if not found
        """
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def get_valid_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token or None if unavailable
        """
        tokens = self.load_tokens()
        if not tokens:
            return None
        
        # Check if token is still valid (with 5-minute buffer)
        expires_at = tokens.get("expires_at", 0)
        if time.time() < (expires_at - 300):  # 5-minute buffer
            return tokens.get("access_token")
        
        # Token is expired or about to expire, try to refresh
        if "refresh_token" in tokens:
            return self._refresh_token(tokens["refresh_token"])
        
        return None
    
    def _refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Reddit refresh token
            
        Returns:
            New access token or None if refresh failed
        """
        try:
            import os
            from .reddit_oauth_helper import RedditOAuthHelper
            
            client_id = os.getenv("REDDIT_CLIENT_ID")
            client_secret = os.getenv("REDDIT_CLIENT_SECRET")
            redirect_uri = os.getenv("REDDIT_REDIRECT_URI", "http://localhost:8888/callback")
            
            if not client_id or not client_secret:
                return None
            
            oauth_helper = RedditOAuthHelper(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri
            )
            
            # Refresh token (this needs to be implemented)
            import asyncio
            new_tokens = asyncio.run(oauth_helper.refresh_access_token(refresh_token))
            
            if new_tokens and "access_token" in new_tokens:
                self.save_tokens(new_tokens)
                return new_tokens["access_token"]
                
        except Exception as e:
            print(f"Failed to refresh Reddit token: {e}")
        
        return None
    
    def clear_tokens(self) -> None:
        """Clear stored tokens."""
        if self.token_file.exists():
            self.token_file.unlink()
    
    def get_token_status(self) -> Dict[str, Any]:
        """
        Get current token status.
        
        Returns:
            Token status information
        """
        tokens = self.load_tokens()
        if not tokens:
            return {
                "has_tokens": False,
                "message": "No tokens found"
            }
        
        expires_at = tokens.get("expires_at", 0)
        current_time = time.time()
        
        if current_time >= expires_at:
            status = "expired"
        elif current_time >= (expires_at - 300):  # Within 5 minutes of expiry
            status = "expiring_soon"
        else:
            status = "valid"
        
        return {
            "has_tokens": True,
            "status": status,
            "expires_at": expires_at,
            "expires_in_seconds": max(0, int(expires_at - current_time)),
            "has_refresh_token": "refresh_token" in tokens,
            "refreshed_at": tokens.get("refreshed_at")
        }
