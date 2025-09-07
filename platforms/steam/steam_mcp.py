"""
Steam MCP Server Module
Provides Steam API integration for personalized gaming data access.
"""

import os
import httpx
from typing import Dict
from mcp.server.fastmcp import FastMCP

# Steam API configuration
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USER_ID = os.getenv("STEAM_USER_ID")

def setup_steam_mcp(mcp: FastMCP):
    """Setup Steam-related MCP tools and resources."""
    
    # Tools - All Steam functions as callable tools
    @mcp.tool()
    def test_steam_credentials() -> str:
        """Test Steam API credentials."""
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not steam_id:
            return "❌ Steam API credentials not found in environment variables"
        
        return f"✅ Steam API credentials found: Key={steam_key[:8]}..., ID={steam_id}"

    @mcp.tool()
    def get_steam_library(steamid: str = None) -> str:
        """Get user's Steam game library with detailed statistics.
        
        Args:
            steamid: Optional Steam ID. If not provided, uses your own Steam ID.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        # Use provided steamid or default to user's own Steam ID
        target_steamid = steamid if steamid else user_steam_id
        
        try:
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            params = {
                "key": steam_key,
                "steamid": target_steamid,
                "format": "json",
                "include_appinfo": 1,
                "include_played_free_games": 1
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "response" in data and "games" in data["response"]:
                games = data["response"]["games"]
                
                # Sort by playtime
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
            else:
                return "No games found or profile is private"
                
        except Exception as e:
            return f"Error fetching Steam library: {str(e)}"

    @mcp.tool()
    def get_steam_friends(steamid: str = None) -> str:
        """Get user's Steam friends list.
        
        Args:
            steamid: Optional Steam ID. If not provided, uses your own Steam ID.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        # Use provided steamid or default to user's own Steam ID
        target_steamid = steamid if steamid else user_steam_id
        
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
            params = {
                "key": steam_key,
                "steamid": target_steamid,
                "relationship": "friend",
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "friendslist" in data and "friends" in data["friendslist"]:
                friends = data["friendslist"]["friends"]
                
                friends_info = f"""Steam Friends List:
Total Friends: {len(friends)}

Friend Steam IDs (first 10):
"""
                for i, friend in enumerate(friends[:10], 1):
                    friend_since = friend.get("friend_since", 0)
                    if friend_since > 0:
                        import datetime
                        date_added = datetime.datetime.fromtimestamp(friend_since).strftime("%Y-%m-%d")
                        friends_info += f"{i}. {friend.get('steamid')} (friends since {date_added})\n"
                    else:
                        friends_info += f"{i}. {friend.get('steamid')}\n"
                
                if len(friends) > 10:
                    friends_info += f"... and {len(friends) - 10} more friends"
                
                return friends_info
            else:
                return "Friends list is private or empty"
                
        except Exception as e:
            return f"Error fetching friends list: {str(e)}"

    @mcp.tool()
    def my_steam_recent_activity() -> str:
        """Get my recent Steam gaming activity."""
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not steam_id:
            return "Steam API credentials not configured"
        
        try:
            url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
            params = {
                "key": steam_key,
                "steamid": steam_id,
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "response" in data and "games" in data["response"]:
                games = data["response"]["games"]
                
                activity_info = f"""My Recent Steam Activity:
Total Games Played (last 2 weeks): {len(games)}

Games and Playtime:
"""
                for i, game in enumerate(games, 1):
                    recent_hours = round(game.get("playtime_2weeks", 0) / 60, 1)
                    total_hours = round(game.get("playtime_forever", 0) / 60, 1)
                    activity_info += f"{i}. {game.get('name')}\n"
                    activity_info += f"   - Recent: {recent_hours}h (2 weeks)\n"
                    activity_info += f"   - Total: {total_hours}h (all time)\n\n"
                
                return activity_info
            else:
                return "No recent gaming activity found"
                
        except Exception as e:
            return f"Error fetching recent activity: {str(e)}"

    @mcp.tool()
    def get_steam_profile(steamid: str = None) -> str:
        """Get Steam profile information.
        
        Args:
            steamid: Optional Steam ID. If not provided, uses your own Steam ID.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        # Use provided steamid or default to user's own Steam ID
        target_steamid = steamid if steamid else user_steam_id
        
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            params = {
                "key": steam_key,
                "steamids": target_steamid,
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "response" in data and "players" in data["response"] and data["response"]["players"]:
                player = data["response"]["players"][0]
                
                persona_states = {
                    0: "Offline", 1: "Online", 2: "Busy", 3: "Away", 
                    4: "Snooze", 5: "Looking to trade", 6: "Looking to play"
                }
                
                profile_info = f"""Steam Profile Information:
Name: {player.get('personaname')}
Status: {persona_states.get(player.get('personastate', 0), 'Unknown')}
Profile: {player.get('profileurl')}
Real Name: {player.get('realname', 'Not set')}
Country: {player.get('loccountrycode', 'Not set')}
Currently Playing: {player.get('gameextrainfo', 'Nothing')}
Profile Visibility: {'Public' if player.get('communityvisibilitystate') == 3 else 'Private'}
"""
                return profile_info
            else:
                return "Profile information not available"
                
        except Exception as e:
            return f"Error fetching profile: {str(e)}"

    @mcp.tool()
    def get_steam_config() -> str:
        """Get Steam API configuration status."""
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")
        
        config_info = f"""Steam API Configuration:
API Key: {'✅ Configured' if steam_key else '❌ Not configured'}
Steam ID: {'✅ Configured' if steam_id else '❌ Not configured'}
Status: {'🟢 Ready' if steam_key and steam_id else '🔴 Incomplete'}

API Key Preview: {steam_key[:8] + '...' if steam_key else 'Not set'}
Steam ID: {steam_id if steam_id else 'Not set'}
"""
        return config_info

    # Tools - Dynamic queries with parameters
    @mcp.tool()
    def get_steam_recent_activity(steamid: str = None) -> Dict:
        """Get user's recent Steam gaming activity.
        
        Args:
            steamid: Optional Steam ID. If not provided, uses your own Steam ID.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return {"error": "Steam API credentials not configured"}
        
        # Use provided steamid or default to user's own Steam ID
        target_steamid = steamid if steamid else user_steam_id
        
        url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
        params = {
            "key": steam_key,
            "steamid": target_steamid,
            "format": "json"
        }
        
        response = httpx.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if "response" in data and "games" in data["response"]:
            return {
                "steamid": target_steamid,
                "recent_games": data["response"]["games"],
                "total_recent_games": data["response"]["total_count"]
            }
        else:
            return {"steamid": target_steamid, "message": "No recent activity found"}

    @mcp.tool()
    def get_player_summary(steamids: str = None) -> Dict:
        """Get detailed player profile information including status, avatar, and location.
        
        Args:
            steamids: Optional comma-separated list of Steam IDs. If not provided, uses your own Steam ID.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return {"error": "Steam API credentials not configured"}
        
        # Use provided steamids or default to user's own Steam ID
        target_steamids = steamids if steamids else user_steam_id
        
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            params = {
                "key": steam_key,
                "steamids": target_steamids,
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "response" in data and "players" in data["response"] and data["response"]["players"]:
                players = data["response"]["players"]
                
                # Convert persona state to readable format
                persona_states = {
                    0: "Offline", 1: "Online", 2: "Busy", 3: "Away", 
                    4: "Snooze", 5: "Looking to trade", 6: "Looking to play"
                }
                
                results = []
                for player in players:
                    player_info = {
                        "steam_id": player.get("steamid"),
                        "persona_name": player.get("personaname"),
                        "profile_url": player.get("profileurl"),
                        "avatar": player.get("avatarfull"),
                        "status": persona_states.get(player.get("personastate", 0), "Unknown"),
                        "profile_visibility": "Public" if player.get("communityvisibilitystate") == 3 else "Private",
                        "real_name": player.get("realname"),
                        "country": player.get("loccountrycode"),
                        "state": player.get("locstatecode"),
                        "account_created": player.get("timecreated"),
                        "last_logoff": player.get("lastlogoff"),
                        "current_game": player.get("gameextrainfo"),
                        "game_id": player.get("gameid")
                    }
                    results.append(player_info)
                
                # If only one player requested, return single object; otherwise return list
                if len(results) == 1 and not steamids:
                    return results[0]
                else:
                    return {
                        "players": results,
                        "total_players": len(results)
                    }
            else:
                return {"error": "Player(s) not found"}
                
        except Exception as e:
            return {"error": f"Failed to fetch player summary: {str(e)}"}

    @mcp.tool()
    def get_player_achievements(app_id: int) -> Dict:
        """Get player achievements for a specific game."""
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not steam_id:
            return {"error": "Steam API credentials not configured"}
        
        try:
            url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
            params = {
                "key": steam_key,
                "steamid": steam_id,
                "appid": app_id,
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "playerstats" in data and "achievements" in data["playerstats"]:
                achievements = data["playerstats"]["achievements"]
                achieved_count = sum(1 for ach in achievements if ach.get("achieved") == 1)
                
                return {
                    "game_name": data["playerstats"].get("gameName"),
                    "total_achievements": len(achievements),
                    "achieved_count": achieved_count,
                    "completion_rate": round((achieved_count / len(achievements)) * 100, 1) if achievements else 0,
                    "recent_achievements": [ach for ach in achievements if ach.get("achieved") == 1][:5]
                }
            else:
                return {"error": "No achievement data found for this game"}
                
        except Exception as e:
            return {"error": f"Failed to fetch achievements: {str(e)}"}

    @mcp.tool()
    def get_user_game_stats(app_id: int) -> Dict:
        """Get detailed user statistics for a specific game."""
        steam_key = os.getenv("STEAM_API_KEY")
        steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not steam_id:
            return {"error": "Steam API credentials not configured"}
        
        try:
            url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/"
            params = {
                "key": steam_key,
                "steamid": steam_id,
                "appid": app_id,
                "format": "json"
            }
            
            response = httpx.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if "playerstats" in data:
                stats = data["playerstats"]
                return {
                    "game_name": stats.get("gameName"),
                    "achievements": stats.get("achievements", []),
                    "stats": stats.get("stats", []),
                    "summary": f"Game statistics for {stats.get('gameName', 'Unknown Game')}"
                }
            else:
                return {"error": "No statistics found for this game"}
                
        except Exception as e:
            return {"error": f"Failed to fetch game stats: {str(e)}"}

    @mcp.tool()
    def get_friends_current_games() -> str:
        """Get what games your Steam friends are currently playing."""
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        try:
            # First get friends list
            friends_url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
            friends_params = {
                "key": steam_key,
                "steamid": user_steam_id,
                "relationship": "friend",
                "format": "json"
            }
            
            friends_response = httpx.get(friends_url, params=friends_params)
            friends_response.raise_for_status()
            friends_data = friends_response.json()
            
            if "friendslist" not in friends_data or "friends" not in friends_data["friendslist"]:
                return "No friends found or friends list is private"
            
            friends = friends_data["friendslist"]["friends"]
            friend_ids = [friend["steamid"] for friend in friends[:20]]  # Limit to first 20 friends
            
            # Get player summaries for all friends
            summaries_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            summaries_params = {
                "key": steam_key,
                "steamids": ",".join(friend_ids),
                "format": "json"
            }
            
            summaries_response = httpx.get(summaries_url, params=summaries_params)
            summaries_response.raise_for_status()
            summaries_data = summaries_response.json()
            
            if "response" not in summaries_data or "players" not in summaries_data["response"]:
                return "Could not fetch friends' current status"
            
            players = summaries_data["response"]["players"]
            currently_playing = []
            online_friends = []
            
            persona_states = {
                0: "Offline", 1: "Online", 2: "Busy", 3: "Away", 
                4: "Snooze", 5: "Looking to trade", 6: "Looking to play"
            }
            
            for player in players:
                status = persona_states.get(player.get("personastate", 0), "Unknown")
                if player.get("gameextrainfo"):
                    currently_playing.append({
                        "name": player.get("personaname"),
                        "game": player.get("gameextrainfo"),
                        "status": status
                    })
                elif player.get("personastate", 0) > 0:  # Online but not playing
                    online_friends.append({
                        "name": player.get("personaname"),
                        "status": status
                    })
            
            result = f"Friends' Current Gaming Activity:\n\n"
            
            if currently_playing:
                result += f"🎮 Friends Currently Playing ({len(currently_playing)}):\n"
                for friend in currently_playing:
                    result += f"• {friend['name']} - {friend['game']} ({friend['status']})\n"
                result += "\n"
            
            if online_friends:
                result += f"🟢 Online Friends Not Gaming ({len(online_friends)}):\n"
                for friend in online_friends[:10]:  # Show first 10
                    result += f"• {friend['name']} ({friend['status']})\n"
                result += "\n"
            
            if not currently_playing and not online_friends:
                result += "No friends are currently online or playing games.\n"
            
            result += f"Total friends checked: {len(players)}"
            return result
            
        except Exception as e:
            return f"Error fetching friends' current games: {str(e)}"

    @mcp.tool()
    def compare_games_with_friend(friend_steamid: str) -> str:
        """Compare your game library with a friend's library to find common games.
        
        Args:
            friend_steamid: Steam ID of the friend to compare with.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        if not friend_steamid:
            return "Friend's Steam ID is required"
        
        try:
            # Get your games
            your_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            your_params = {
                "key": steam_key,
                "steamid": user_steam_id,
                "format": "json",
                "include_appinfo": 1
            }
            
            your_response = httpx.get(your_games_url, params=your_params)
            your_response.raise_for_status()
            your_data = your_response.json()
            
            # Get friend's games
            friend_params = {
                "key": steam_key,
                "steamid": friend_steamid,
                "format": "json",
                "include_appinfo": 1
            }
            
            friend_response = httpx.get(your_games_url, params=friend_params)
            friend_response.raise_for_status()
            friend_data = friend_response.json()
            
            # Get friend's name
            profile_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            profile_params = {
                "key": steam_key,
                "steamids": friend_steamid,
                "format": "json"
            }
            
            profile_response = httpx.get(profile_url, params=profile_params)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            friend_name = "Unknown"
            if ("response" in profile_data and "players" in profile_data["response"] 
                and profile_data["response"]["players"]):
                friend_name = profile_data["response"]["players"][0].get("personaname", "Unknown")
            
            # Process game data
            if ("response" not in your_data or "games" not in your_data["response"] or
                "response" not in friend_data or "games" not in friend_data["response"]):
                return "Could not access game libraries (profiles may be private)"
            
            your_games = {game["appid"]: game for game in your_data["response"]["games"]}
            friend_games = {game["appid"]: game for game in friend_data["response"]["games"]}
            
            # Find common games
            common_app_ids = set(your_games.keys()) & set(friend_games.keys())
            common_games = []
            
            for app_id in common_app_ids:
                your_game = your_games[app_id]
                friend_game = friend_games[app_id]
                common_games.append({
                    "name": your_game.get("name", "Unknown Game"),
                    "your_hours": round(your_game.get("playtime_forever", 0) / 60, 1),
                    "friend_hours": round(friend_game.get("playtime_forever", 0) / 60, 1)
                })
            
            # Sort by combined playtime
            common_games.sort(key=lambda x: x["your_hours"] + x["friend_hours"], reverse=True)
            
            result = f"Game Library Comparison with {friend_name}:\n\n"
            result += f"Your Games: {len(your_games)}\n"
            result += f"{friend_name}'s Games: {len(friend_games)}\n"
            result += f"Common Games: {len(common_games)}\n\n"
            
            if common_games:
                result += "Top Common Games (by combined playtime):\n"
                for i, game in enumerate(common_games[:15], 1):
                    result += f"{i}. {game['name']}\n"
                    result += f"   You: {game['your_hours']}h | {friend_name}: {game['friend_hours']}h\n"
            else:
                result += "No common games found.\n"
            
            return result
            
        except Exception as e:
            return f"Error comparing game libraries: {str(e)}"

    @mcp.tool()
    def get_friend_game_recommendations(friend_steamid: str) -> str:
        """Get game recommendations based on what a friend owns but you don't.
        
        Args:
            friend_steamid: Steam ID of the friend to get recommendations from.
        """
        steam_key = os.getenv("STEAM_API_KEY")
        user_steam_id = os.getenv("STEAM_USER_ID")
        
        if not steam_key or not user_steam_id:
            return "Steam API credentials not configured"
        
        if not friend_steamid:
            return "Friend's Steam ID is required"
        
        try:
            # Get your games
            your_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            your_params = {
                "key": steam_key,
                "steamid": user_steam_id,
                "format": "json",
                "include_appinfo": 1
            }
            
            your_response = httpx.get(your_games_url, params=your_params)
            your_response.raise_for_status()
            your_data = your_response.json()
            
            # Get friend's games
            friend_params = {
                "key": steam_key,
                "steamid": friend_steamid,
                "format": "json",
                "include_appinfo": 1
            }
            
            friend_response = httpx.get(your_games_url, params=friend_params)
            friend_response.raise_for_status()
            friend_data = friend_response.json()
            
            # Get friend's name
            profile_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            profile_params = {
                "key": steam_key,
                "steamids": friend_steamid,
                "format": "json"
            }
            
            profile_response = httpx.get(profile_url, params=profile_params)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            friend_name = "Unknown"
            if ("response" in profile_data and "players" in profile_data["response"] 
                and profile_data["response"]["players"]):
                friend_name = profile_data["response"]["players"][0].get("personaname", "Unknown")
            
            # Process game data
            if ("response" not in your_data or "games" not in your_data["response"] or
                "response" not in friend_data or "games" not in friend_data["response"]):
                return "Could not access game libraries (profiles may be private)"
            
            your_app_ids = {game["appid"] for game in your_data["response"]["games"]}
            friend_games = friend_data["response"]["games"]
            
            # Find games friend has but you don't
            recommendations = []
            for game in friend_games:
                if game["appid"] not in your_app_ids:
                    hours = round(game.get("playtime_forever", 0) / 60, 1)
                    if hours > 0:  # Only recommend games the friend actually played
                        recommendations.append({
                            "name": game.get("name", "Unknown Game"),
                            "friend_hours": hours
                        })
            
            # Sort by friend's playtime
            recommendations.sort(key=lambda x: x["friend_hours"], reverse=True)
            
            result = f"Game Recommendations from {friend_name}:\n\n"
            result += f"Games {friend_name} owns but you don't: {len(recommendations)}\n\n"
            
            if recommendations:
                result += f"Top Recommendations (games {friend_name} played most):\n"
                for i, game in enumerate(recommendations[:20], 1):
                    result += f"{i}. {game['name']} ({game['friend_hours']}h played by {friend_name})\n"
            else:
                result += f"No recommendations found - you might already own all of {friend_name}'s played games!\n"
            
            return result
            
        except Exception as e:
            return f"Error getting game recommendations: {str(e)}"
