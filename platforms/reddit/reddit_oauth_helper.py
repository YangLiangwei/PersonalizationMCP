"""
Reddit OAuth2 authentication helper.

This module handles Reddit OAuth2 authentication flow for PersonalizationMCP.
Reddit uses OAuth2 with Authorization Code flow for third-party applications.
"""

import httpx
import secrets
from urllib.parse import urlencode
from typing import Dict, Any, Optional


class RedditOAuthHelper:
    """Helper class for Reddit OAuth2 authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize Reddit OAuth helper.
        
        Args:
            client_id: Reddit OAuth client ID
            client_secret: Reddit OAuth client secret  
            redirect_uri: Redirect URI configured in Reddit app
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_base_url = "https://www.reddit.com/api/v1/authorize"
        self.token_url = "https://www.reddit.com/api/v1/access_token"
        
        # Reddit API requires specific scopes for different data access
        self.scope = " ".join([
            "identity",      # Access basic account information
            "read",          # Read access to posts and comments
            "mysubreddits",  # Access to user's subscribed subreddits
            "history",       # Access to user's post/comment history
            "save",          # Access to saved posts
            "subscribe",     # Manage subscriptions
        ])
    
    def generate_auth_url(self, state: Optional[str] = None) -> Dict[str, str]:
        """
        Generate Reddit authorization URL for OAuth flow.
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Dictionary containing auth URL and state
        """
        if not state:
            state = secrets.token_urlsafe(32)
            
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": state,
            "duration": "permanent"  # Request permanent access
        }
        
        auth_url = f"{self.auth_base_url}?{urlencode(params)}"
        
        return {
            "auth_url": auth_url,
            "state": state,
            "redirect_uri": self.redirect_uri
        }
    
    async def exchange_code_for_tokens(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            authorization_code: Authorization code from Reddit callback
            
        Returns:
            Token response from Reddit
        """
        headers = {
            "User-Agent": "PersonalizationMCP/1.0.0 (Personal data aggregator)"
        }
        
        # Reddit requires Basic auth with client credentials
        auth = (self.client_id, self.client_secret)
        
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                auth=auth,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Reddit refresh token
            
        Returns:
            New token response
        """
        headers = {
            "User-Agent": "PersonalizationMCP/1.0.0 (Personal data aggregator)"
        }
        
        auth = (self.client_id, self.client_secret)
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                auth=auth,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            return response.json()