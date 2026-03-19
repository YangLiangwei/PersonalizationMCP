"""Spotify service layer used by CLI and MCP adapter."""

from __future__ import annotations

import httpx
import os
from typing import Any, Dict

from platforms.spotify.spotify_token_manager import SpotifyTokenManager


def _get_valid_oauth_token(access_token: str | None = None) -> str | None:
    if access_token and access_token.strip() and access_token != "null":
        return access_token

    try:
        token_manager = SpotifyTokenManager()
        managed_token = token_manager.get_valid_access_token()
        if managed_token:
            return managed_token
    except Exception:
        pass

    env_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
    if env_token and env_token.strip():
        return env_token
    return None


class SpotifyService:
    @staticmethod
    def credentials_status() -> str:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        if not client_id or not client_secret:
            return "❌ Spotify API credentials not found in environment variables"
        return f"✅ Spotify API credentials found: Client ID={client_id[:8]}..."

    @staticmethod
    def get_config() -> str:
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        access_token = os.getenv("SPOTIFY_ACCESS_TOKEN")
        return (
            "Spotify API Configuration Status:\n"
            f"- client_id: {'✅ Set' if client_id else '❌ Not set'}\n"
            f"- client_secret: {'✅ Set' if client_secret else '❌ Not set'}\n"
            f"- access_token: {'✅ Set' if access_token else '❌ Not set'}\n"
        )

    @staticmethod
    def refresh_token() -> Dict[str, Any]:
        try:
            token_manager = SpotifyTokenManager()
            new_token = token_manager.refresh_access_token()
            if new_token:
                return {"status": "success", "message": "✅ Spotify access token refreshed successfully"}
            return {"status": "error", "message": "❌ Failed to refresh token. Please re-authenticate."}
        except Exception as e:
            return {"status": "error", "message": f"Token refresh failed: {str(e)}"}

    @staticmethod
    def auto_refresh_if_needed() -> Dict[str, Any]:
        try:
            token_manager = SpotifyTokenManager()
            result = token_manager.ensure_valid_token()
            return {
                "status": "success",
                "message": f"✅ Token status: {result['message']}",
                "token_refreshed": result.get("refreshed", False),
            }
        except Exception as e:
            return {"status": "error", "message": f"Auto refresh failed: {str(e)}"}

    @staticmethod
    def token_status() -> Dict[str, Any]:
        try:
            token_manager = SpotifyTokenManager()
            status = token_manager.get_token_status()
            return {"status": "success", "token_info": status}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get token status: {str(e)}"}

    @staticmethod
    def get_current_user_profile(access_token: str | None = None) -> Dict[str, Any]:
        token = _get_valid_oauth_token(access_token)
        if not token:
            return {
                "status": "error",
                "message": "No valid OAuth token available. Please complete OAuth authentication first.",
            }
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
                    "external_urls": user_data.get("external_urls", {}),
                },
            }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get user profile: {e}"}

    @staticmethod
    def get_recently_played(limit: int = 50, access_token: str | None = None) -> Dict[str, Any]:
        token = _get_valid_oauth_token(access_token)
        if not token:
            return {
                "status": "error",
                "message": "No valid OAuth token available. Please complete OAuth authentication first.",
            }
        try:
            headers = {"Authorization": f"Bearer {token}"}
            params = {"limit": min(limit, 50)}
            with httpx.Client() as client:
                response = client.get(
                    "https://api.spotify.com/v1/me/player/recently-played",
                    headers=headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

            items = data.get("items", [])
            formatted_tracks = []
            for item in items:
                track = item.get("track", {})
                artists = ", ".join([artist.get("name", "") for artist in track.get("artists", [])])
                formatted_tracks.append(
                    {
                        "track_name": track.get("name", "Unknown"),
                        "artists": artists,
                        "album": track.get("album", {}).get("name", "Unknown"),
                        "played_at": item.get("played_at", ""),
                        "duration_ms": track.get("duration_ms", 0),
                        "external_urls": track.get("external_urls", {}),
                        "track_id": track.get("id", ""),
                    }
                )

            return {
                "status": "success",
                "total_tracks": len(formatted_tracks),
                "tracks": formatted_tracks,
                "next": data.get("next"),
                "cursors": data.get("cursors", {}),
            }
        except httpx.HTTPError as e:
            return {"status": "error", "message": f"Failed to get recently played tracks: {e}"}
