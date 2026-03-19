"""Steam service layer used by CLI and MCP adapter."""

from __future__ import annotations

import datetime
import os
from typing import Dict, Any

import httpx


class SteamService:
    @staticmethod
    def credentials_status() -> str:
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")

        if not steam_key or not steam_id:
            return "❌ Steam API credentials not found in environment variables"
        return f"✅ Steam API credentials found: Key={steam_key[:8]}..., ID={steam_id}"

    @staticmethod
    def get_library(steamid: str | None = None) -> str:
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"

        target_steamid = steamid or user_steam_id
        try:
            url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": steam_key,
                "steamid": target_steamid,
                "format": "json",
                "include_appinfo": 1,
                "include_played_free_games": 1,
            }
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            games = data.get("response", {}).get("games", [])
            if not games:
                return "No games found or profile is private"

            games_sorted = sorted(games, key=lambda x: x.get("playtime_forever", 0), reverse=True)
            total_games = len(games_sorted)
            total_playtime = sum(game.get("playtime_forever", 0) for game in games_sorted)
            recent_games = [g for g in games_sorted if g.get("playtime_2weeks", 0) > 0]

            library_info = f"""Steam Game Library (Detailed):
Total Games: {total_games}
Total Playtime: {round(total_playtime / 60, 1)} hours
Average Hours per Game: {round((total_playtime / 60) / max(total_games, 1), 1)}

Top 10 Most Played Games:
"""
            for i, game in enumerate(games_sorted[:10], 1):
                hours = round(game.get("playtime_forever", 0) / 60, 1)
                library_info += f"{i}. {game.get('name')} - {hours} hours\n"

            if recent_games:
                library_info += f"\nRecently Active Games ({len(recent_games)}):\n"
                for game in recent_games[:5]:
                    recent_hours = round(game.get("playtime_2weeks", 0) / 60, 1)
                    total_hours = round(game.get("playtime_forever", 0) / 60, 1)
                    library_info += f"- {game.get('name')} - {recent_hours}h (2 weeks), {total_hours}h (total)\n"

            return library_info
        except Exception as e:
            return f"Error fetching Steam library: {str(e)}"

    @staticmethod
    def get_profile(steamid: str | None = None) -> str:
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"

        target_steamid = steamid or user_steam_id
        try:
            url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            params = {"key": steam_key, "steamids": target_steamid, "format": "json"}
            response = httpx.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            players = data.get("response", {}).get("players", [])
            if not players:
                return "Profile information not available"

            player = players[0]
            persona_states = {
                0: "Offline", 1: "Online", 2: "Busy", 3: "Away",
                4: "Snooze", 5: "Looking to trade", 6: "Looking to play"
            }
            return f"""Steam Profile Information:
Name: {player.get('personaname')}
Status: {persona_states.get(player.get('personastate', 0), 'Unknown')}
Profile: {player.get('profileurl')}
Real Name: {player.get('realname', 'Not set')}
Country: {player.get('loccountrycode', 'Not set')}
Currently Playing: {player.get('gameextrainfo', 'Nothing')}
Profile Visibility: {'Public' if player.get('communityvisibilitystate') == 3 else 'Private'}
"""
        except Exception as e:
            return f"Error fetching profile: {str(e)}"

    @staticmethod
    def get_recent_activity(steamid: str | None = None) -> Dict[str, Any]:
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        if not steam_key or not user_steam_id:
            return {"error": "Steam API credentials not configured"}

        target_steamid = steamid or user_steam_id
        url = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {"key": steam_key, "steamid": target_steamid, "format": "json"}
        response = httpx.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if "response" in data and "games" in data["response"]:
            return {
                "steamid": target_steamid,
                "recent_games": data["response"]["games"],
                "total_recent_games": data["response"]["total_count"],
            }
        return {"steamid": target_steamid, "message": "No recent activity found"}
