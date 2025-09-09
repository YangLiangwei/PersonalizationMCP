"""
Spotify Token Manager
Manages Spotify OAuth tokens with automatic refresh capabilities.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional
from .spotify_oauth_helper import SpotifyOAuthHelper

class SpotifyTokenManager:
    """Manages Spotify OAuth tokens with automatic refresh."""
    
    def __init__(self):
        self.token_file = Path(__file__).parent / "spotify_tokens.json"
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    
    def save_tokens(self, tokens: Dict) -> None:
        """Save tokens to file with expiration time."""
        # Add expiration timestamp
        if "expires_in" in tokens:
            tokens["expires_at"] = time.time() + tokens["expires_in"]
        
        try:
            with open(self.token_file, "w") as f:
                json.dump(tokens, f, indent=2)
            print(f"✅ Tokens saved to {self.token_file}")
        except Exception as e:
            print(f"❌ Failed to save tokens: {e}")
            raise
    
    def load_tokens(self) -> Optional[Dict]:
        """Load tokens from file."""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load tokens: {e}")
            return None
    
    def is_token_expired(self, tokens: Dict) -> bool:
        """Check if access token is expired."""
        if "expires_at" not in tokens:
            return True
        
        # Consider token expired if it expires within 5 minutes
        return time.time() >= (tokens["expires_at"] - 300)
    
    def refresh_access_token(self) -> Optional[str]:
        """Refresh access token using refresh token."""
        tokens = self.load_tokens()
        if not tokens or "refresh_token" not in tokens:
            print("❌ No refresh token available")
            return None
        
        if not self.client_id or not self.client_secret:
            print("❌ Spotify client credentials not configured")
            return None
        
        try:
            oauth_helper = SpotifyOAuthHelper(self.client_id, self.client_secret)
            new_tokens = oauth_helper.refresh_access_token(tokens["refresh_token"])
            
            # Update tokens (preserve refresh_token if not returned)
            if "refresh_token" not in new_tokens and "refresh_token" in tokens:
                new_tokens["refresh_token"] = tokens["refresh_token"]
            
            self.save_tokens(new_tokens)
            print("✅ Access token refreshed successfully")
            return new_tokens["access_token"]
        
        except Exception as e:
            print(f"❌ Failed to refresh access token: {e}")
            return None
    
    def get_valid_access_token(self) -> Optional[str]:
        """Get valid access token, refresh if necessary."""
        tokens = self.load_tokens()
        if not tokens:
            return None
        
        # Check if token is expired
        if self.is_token_expired(tokens):
            print("🔄 Access token expired, refreshing...")
            return self.refresh_access_token()
        
        return tokens.get("access_token")
    
    def ensure_valid_token(self) -> Dict:
        """Ensure we have a valid token, refresh if needed."""
        tokens = self.load_tokens()
        if not tokens:
            return {
                "status": "error",
                "message": "No tokens found. Please authenticate first."
            }
        
        if self.is_token_expired(tokens):
            new_token = self.refresh_access_token()
            if new_token:
                return {
                    "status": "success",
                    "message": "Token refreshed successfully",
                    "refreshed": True
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to refresh token. Please re-authenticate."
                }
        else:
            return {
                "status": "success",
                "message": "Token is still valid",
                "refreshed": False
            }
    
    def get_token_status(self) -> Dict:
        """Get current token status information."""
        tokens = self.load_tokens()
        if not tokens:
            return {
                "has_tokens": False,
                "message": "No tokens found"
            }
        
        has_access_token = "access_token" in tokens
        has_refresh_token = "refresh_token" in tokens
        is_expired = self.is_token_expired(tokens)
        
        status = {
            "has_tokens": True,
            "has_access_token": has_access_token,
            "has_refresh_token": has_refresh_token,
            "is_expired": is_expired
        }
        
        if "expires_at" in tokens:
            remaining_time = tokens["expires_at"] - time.time()
            status["expires_in_seconds"] = max(0, int(remaining_time))
            status["expires_in_minutes"] = max(0, int(remaining_time / 60))
        
        return status
    
    def clear_tokens(self) -> None:
        """Clear saved tokens."""
        if self.token_file.exists():
            self.token_file.unlink()
            print("✅ Tokens cleared")
