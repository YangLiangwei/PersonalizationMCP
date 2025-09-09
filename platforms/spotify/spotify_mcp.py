"""
Spotify MCP Server Module
Provides Spotify API integration for personalized music consumption data.
"""

import os
import httpx
import base64
from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from .spotify_oauth_helper import SpotifyOAuthHelper
from .spotify_token_manager import SpotifyTokenManager

# Spotify API configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def _get_valid_oauth_token(access_token: str = None) -> str:
    """
    Get valid OAuth token with unified logic
    Priority:
    1. Explicitly passed access_token (if not None and not empty)
    2. Automatically obtained valid token from token manager (preferred, auto-refresh)
    3. Token from environment variables (as backup)
    """
    # 1. If explicitly passed valid access_token, use it directly
    if access_token and access_token.strip() and access_token != "null":
        return access_token
    
    # 2. Try to use token manager to get valid token (auto-refresh)
    try:
        token_manager = SpotifyTokenManager()
        managed_token = token_manager.get_valid_access_token()
        if managed_token:
            return managed_token
    except Exception as e:
        print(f"⚠️ Token manager failed: {e}")
    
    # 3. Backup: try to get from environment variables
    env_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if env_token and env_token.strip():
        return env_token
    
    return None

def _ensure_valid_oauth_token(access_token: str = None) -> tuple[str, dict]:
    """
    Ensure valid OAuth token, auto-refresh if needed
    Returns: (token, status_info)
    """
    # First try to get token
    token = _get_valid_oauth_token(access_token)
    
    if not token:
        return None, {
            "status": "error",
            "message": "No valid OAuth token available. Please complete OAuth authentication first."
        }
    
    return token, {"status": "success", "message": "Valid token obtained"}

def setup_spotify_mcp(mcp: FastMCP):
    """Setup Spotify-related MCP tools and resources."""
    
    # Tools - All Spotify functions as callable tools
    @mcp.tool()
    def test_spotify_credentials() -> str:
        """Test Spotify API credentials."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return "❌ Spotify API credentials not found in environment variables"
        
        return f"✅ Spotify API credentials found: Client ID={client_id[:8]}..."

    @mcp.tool()
    def get_spotify_config() -> str:
        """Get Spotify API configuration status."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        
        config_status = {
            "client_id": "✅ Set" if client_id else "❌ Not set",
            "client_secret": "✅ Set" if client_secret else "❌ Not set",
            "access_token": "✅ Set" if access_token else "❌ Not set"
        }
        
        status_text = "Spotify API Configuration Status:\n"
        for key, value in config_status.items():
            status_text += f"- {key}: {value}\n"
        
        return status_text

    @mcp.tool()
    def setup_spotify_oauth(client_id: str, client_secret: str, redirect_uri: str = None) -> dict:
        """
        Setup Spotify OAuth2 authentication (initial authentication)
        
        Args:
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
            redirect_uri: Optional redirect URI (defaults to environment variable or http://localhost:8888/callback)
            
        Returns:
            Dictionary containing authentication status and next steps
        """
        try:
            oauth_helper = SpotifyOAuthHelper(client_id, client_secret, redirect_uri)
            auth_url = oauth_helper.get_authorization_url()
            
            return {
                "status": "success",
                "message": "Please visit the following URL to authorize the application:",
                "authorization_url": auth_url,
                "redirect_uri": oauth_helper.redirect_uri,
                "next_step": "After authorization, you'll be redirected to a URL with a 'code' parameter. Copy that code and use complete_spotify_oauth function."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to setup OAuth: {str(e)}"
            }

    @mcp.tool()
    def complete_spotify_oauth(client_id: str, client_secret: str, authorization_code: str, redirect_uri: str = None) -> dict:
        """
        Complete Spotify OAuth2 authentication (get tokens)
        
        Args:
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
            authorization_code: Authorization code from Spotify callback
            redirect_uri: Optional redirect URI (should match the one used in setup_spotify_oauth)
            
        Returns:
            Authentication completion status
        """
        try:
            oauth_helper = SpotifyOAuthHelper(client_id, client_secret, redirect_uri)
            tokens = oauth_helper.exchange_code_for_tokens(authorization_code)
            
            # Save tokens using token manager
            token_manager = SpotifyTokenManager()
            token_manager.save_tokens(tokens)
            
            return {
                "status": "success",
                "message": "✅ Spotify OAuth authentication completed successfully!",
                "tokens_saved": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to complete OAuth: {str(e)}"
            }

    @mcp.tool()
    def refresh_spotify_token() -> dict:
        """Manually refresh Spotify access token"""
        try:
            token_manager = SpotifyTokenManager()
            new_token = token_manager.refresh_access_token()
            
            if new_token:
                return {
                    "status": "success", 
                    "message": "✅ Spotify access token refreshed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to refresh token. Please re-authenticate."
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Token refresh failed: {str(e)}"
            }

    @mcp.tool()
    def auto_refresh_spotify_token_if_needed() -> dict:
        """Auto check and refresh Spotify access token if needed"""
        try:
            token_manager = SpotifyTokenManager()
            result = token_manager.ensure_valid_token()
            
            return {
                "status": "success",
                "message": f"✅ Token status: {result['message']}",
                "token_refreshed": result.get('refreshed', False)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Auto refresh failed: {str(e)}"
            }

    @mcp.tool()
    def get_spotify_token_status() -> dict:
        """Get Spotify token status information"""
        try:
            token_manager = SpotifyTokenManager()
            status = token_manager.get_token_status()
            
            return {
                "status": "success",
                "token_info": status
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get token status: {str(e)}"
            }

    # User Profile APIs
    @mcp.tool()
    def get_current_user_profile(access_token: str = None) -> dict:
        """Get current user's Spotify profile information."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me", headers=headers)
                response.raise_for_status()
                user_data = response.json()
                
                return {
                    "status": "success",
                    "user_profile": {
                        "id": user_data.get("id"),
                        "display_name": user_data.get("display_name"),
                        "email": user_data.get("email"),
                        "country": user_data.get("country"),
                        "followers": user_data.get("followers", {}).get("total", 0),
                        "product": user_data.get("product"),
                        "images": user_data.get("images", []),
                        "external_urls": user_data.get("external_urls", {})
                    }
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get user profile: {e}"}

    @mcp.tool()
    def get_user_profile(user_id: str, access_token: str = None) -> dict:
        """Get a specific user's public Spotify profile information."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            with httpx.Client() as client:
                response = client.get(f"https://api.spotify.com/v1/users/{user_id}", headers=headers)
                response.raise_for_status()
                user_data = response.json()
                
                return {
                    "status": "success",
                    "user_profile": {
                        "id": user_data.get("id"),
                        "display_name": user_data.get("display_name"),
                        "followers": user_data.get("followers", {}).get("total", 0),
                        "images": user_data.get("images", []),
                        "external_urls": user_data.get("external_urls", {})
                    }
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get user profile: {e}"}

    @mcp.tool()
    def get_user_top_items(item_type: str = "tracks", time_range: str = "medium_term", limit: int = 50, access_token: str = None) -> dict:
        """Get user's top artists or tracks.
        
        Args:
            item_type: "artists" or "tracks"
            time_range: "short_term" (4 weeks), "medium_term" (6 months), "long_term" (years)
            limit: Number of items to return (1-50, default 50)
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        if item_type not in ["artists", "tracks"]:
            return {"status": "error", "message": "item_type must be 'artists' or 'tracks'"}
        
        if time_range not in ["short_term", "medium_term", "long_term"]:
            return {"status": "error", "message": "time_range must be 'short_term', 'medium_term', or 'long_term'"}
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"time_range": time_range, "limit": min(limit, 50)}
            
            with httpx.Client() as client:
                response = client.get(f"https://api.spotify.com/v1/me/top/{item_type}", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "item_type": item_type,
                    "time_range": time_range,
                    "total": data.get("total"),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get top {item_type}: {e}"}

    # Follow/Unfollow APIs
    @mcp.tool()
    def get_followed_artists(limit: int = 50, access_token: str = None) -> dict:
        """Get user's followed artists."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"type": "artist", "limit": min(limit, 50)}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/following", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("artists", {}).get("total", 0),
                    "artists": data.get("artists", {}).get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get followed artists: {e}"}

    @mcp.tool()
    def follow_artists_or_users(ids: str, follow_type: str = "artist", access_token: str = None) -> dict:
        """Follow artists or users.
        
        Args:
            ids: Comma-separated list of artist or user IDs
            follow_type: "artist" or "user"
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        if follow_type not in ["artist", "user"]:
            return {"status": "error", "message": "follow_type must be 'artist' or 'user'"}
        
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            params = {"type": follow_type, "ids": ids}
            
            with httpx.Client() as client:
                response = client.put("https://api.spotify.com/v1/me/following", headers=headers, params=params)
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": f"Successfully followed {follow_type}s: {ids}"
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to follow {follow_type}s: {e}"}

    @mcp.tool()
    def unfollow_artists_or_users(ids: str, follow_type: str = "artist", access_token: str = None) -> dict:
        """Unfollow artists or users.
        
        Args:
            ids: Comma-separated list of artist or user IDs
            follow_type: "artist" or "user"
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        if follow_type not in ["artist", "user"]:
            return {"status": "error", "message": "follow_type must be 'artist' or 'user'"}
        
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            params = {"type": follow_type, "ids": ids}
            
            with httpx.Client() as client:
                response = client.delete("https://api.spotify.com/v1/me/following", headers=headers, params=params)
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": f"Successfully unfollowed {follow_type}s: {ids}"
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to unfollow {follow_type}s: {e}"}

    @mcp.tool()
    def follow_playlist(playlist_id: str, public: bool = True, access_token: str = None) -> dict:
        """Follow a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
            public: Whether the playlist will be included in user's public playlists
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            data = {"public": public}
            
            with httpx.Client() as client:
                response = client.put(f"https://api.spotify.com/v1/playlists/{playlist_id}/followers", 
                                    headers=headers, json=data)
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": f"Successfully followed playlist: {playlist_id}"
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to follow playlist: {e}"}

    @mcp.tool()
    def unfollow_playlist(playlist_id: str, access_token: str = None) -> dict:
        """Unfollow a playlist.
        
        Args:
            playlist_id: Spotify playlist ID
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            with httpx.Client() as client:
                response = client.delete(f"https://api.spotify.com/v1/playlists/{playlist_id}/followers", headers=headers)
                response.raise_for_status()
                
                return {
                    "status": "success",
                    "message": f"Successfully unfollowed playlist: {playlist_id}"
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to unfollow playlist: {e}"}

    # User's Saved Content APIs
    @mcp.tool()
    def get_user_saved_tracks(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get user's saved tracks."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/tracks", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get saved tracks: {e}"}

    @mcp.tool()
    def get_user_saved_albums(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get user's saved albums."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/albums", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get saved albums: {e}"}

    @mcp.tool()
    def get_user_saved_shows(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get user's saved podcast shows."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/shows", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get saved shows: {e}"}

    @mcp.tool()
    def get_user_saved_episodes(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get user's saved podcast episodes."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/episodes", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get saved episodes: {e}"}

    @mcp.tool()
    def get_user_saved_audiobooks(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get user's saved audiobooks."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/audiobooks", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get saved audiobooks: {e}"}

    # Playlist APIs
    @mcp.tool()
    def get_current_user_playlists(limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get current user's playlists."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/playlists", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get user playlists: {e}"}

    @mcp.tool()
    def get_user_playlists(user_id: str, limit: int = 50, offset: int = 0, access_token: str = None) -> dict:
        """Get a user's public playlists."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "user_id": user_id,
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get user playlists: {e}"}

    @mcp.tool()
    def get_playlist_items(playlist_id: str, limit: int = 100, offset: int = 0, access_token: str = None) -> dict:
        """Get items (tracks/episodes) in a playlist."""
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50), "offset": offset}
            
            with httpx.Client() as client:
                response = client.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "playlist_id": playlist_id,
                    "total": data.get("total", 0),
                    "items": data.get("items", [])
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get playlist items: {e}"}

    # Recently Played API
    @mcp.tool()
    def get_user_recently_played(limit: int = 50, access_token: str = None) -> dict:
        """Get user's recently played tracks.
        
        Args:
            limit: Number of tracks to return (1-50, default 50)
        """
        token, status = _ensure_valid_oauth_token(access_token)
        if not token:
            return status
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50)}
            
            with httpx.Client() as client:
                response = client.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Format the response for better readability
                items = data.get("items", [])
                formatted_tracks = []
                
                for item in items:
                    track = item.get("track", {})
                    artists = ", ".join([artist.get("name", "") for artist in track.get("artists", [])])
                    
                    formatted_track = {
                        "track_name": track.get("name", "Unknown"),
                        "artists": artists,
                        "album": track.get("album", {}).get("name", "Unknown"),
                        "played_at": item.get("played_at", ""),
                        "duration_ms": track.get("duration_ms", 0),
                        "external_urls": track.get("external_urls", {}),
                        "track_id": track.get("id", "")
                    }
                    formatted_tracks.append(formatted_track)
                
                return {
                    "status": "success",
                    "total_tracks": len(formatted_tracks),
                    "tracks": formatted_tracks,
                    "next": data.get("next"),
                    "cursors": data.get("cursors", {})
                }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get recently played tracks: {e}"}

    print("✅ Spotify MCP tools registered successfully")
