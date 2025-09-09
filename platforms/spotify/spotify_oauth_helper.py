"""
Spotify OAuth Helper
Handles Spotify OAuth2 authentication flow.
"""

import os
import httpx
import base64
import urllib.parse
from typing import Dict, Optional

class SpotifyOAuthHelper:
    """Helper class for Spotify OAuth2 authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        # Use provided redirect_uri, or get from environment, or use default
        self.redirect_uri = redirect_uri or os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
        self.scope = "user-read-private user-read-email user-library-read user-read-recently-played user-top-read playlist-read-private playlist-read-collaborative user-read-playback-state user-read-currently-playing user-follow-read user-follow-modify playlist-modify-public playlist-modify-private"
        
    def get_authorization_url(self) -> str:
        """Generate Spotify authorization URL."""
        auth_url = "https://accounts.spotify.com/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "show_dialog": "true"
        }
        
        # Build URL with parameters
        param_string = "&".join([f"{key}={urllib.parse.quote(str(value))}" for key, value in params.items()])
        return f"{auth_url}?{param_string}"
    
    def exchange_code_for_tokens(self, authorization_code: str) -> Dict:
        """Exchange authorization code for access and refresh tokens."""
        token_url = "https://accounts.spotify.com/api/token"
        
        # Prepare authorization header
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(token_url, headers=headers, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Failed to exchange code for tokens: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token."""
        token_url = "https://accounts.spotify.com/api/token"
        
        # Prepare authorization header
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(token_url, headers=headers, data=data)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Failed to refresh access token: {e}")
