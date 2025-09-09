# Spotify Platform Integration

This module provides comprehensive Spotify API integration for PersonalHub, allowing access to personal music data, preferences, and user interactions.

## Features

- ✅ **Complete OAuth2 authentication** with automatic token refresh
- ✅ **User profile and library management** 
- ✅ **Music discovery** - top artists, tracks, and recently played
- ✅ **Social features** - follow/unfollow artists and playlists
- ✅ **Library management** - saved tracks, albums, shows, episodes, audiobooks
- ✅ **Playlist operations** - view and manage playlists
- ✅ **Seamless token management** - no manual refresh needed

## Setup

### 1. Create Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Configure redirect URIs in your app settings
4. Note down your Client ID and Client Secret

### 2. Configure Environment Variables

Add the following to your config file:

```bash
# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=https://example.com/callback
```

### 3. Complete OAuth Authentication

Use the MCP tools to complete OAuth authentication:

```bash
# Step 1: Initialize OAuth flow
setup_spotify_oauth client_id="your_client_id" client_secret="your_client_secret"

# Step 2: Visit the provided authorization URL and authorize the app
# Step 3: Copy the authorization code from the callback URL

# Step 4: Complete authentication
complete_spotify_oauth client_id="your_client_id" client_secret="your_client_secret" authorization_code="your_auth_code"
```

## Available MCP Tools (17 Total)

### 🔐 Authentication & Configuration (7 tools)
- `test_spotify_credentials()` - Test API credentials
- `get_spotify_config()` - Get configuration status
- `setup_spotify_oauth(client_id, client_secret, redirect_uri?)` - Initialize OAuth flow
- `complete_spotify_oauth(client_id, client_secret, authorization_code, redirect_uri?)` - Complete OAuth authentication
- `refresh_spotify_token()` - Manually refresh access token
- `auto_refresh_spotify_token_if_needed()` - Auto-refresh if needed
- `get_spotify_token_status()` - Get token status information

### 👤 User Profile (2 tools)
- `get_current_user_profile(access_token?)` - Get current user's profile
- `get_user_profile(user_id, access_token?)` - Get specific user's profile

### 🎵 Music Discovery (2 tools)
- `get_user_top_items(item_type="tracks", time_range="medium_term", limit=50, access_token?)` - Get top artists or tracks
- `get_user_recently_played(limit=50, access_token?)` - Get recently played tracks

### 👥 Social Features (5 tools)
- `get_followed_artists(limit=50, access_token?)` - Get followed artists
- `follow_artists_or_users(ids, follow_type="artist", access_token?)` - Follow artists/users
- `unfollow_artists_or_users(ids, follow_type="artist", access_token?)` - Unfollow artists/users
- `follow_playlist(playlist_id, public=true, access_token?)` - Follow a playlist
- `unfollow_playlist(playlist_id, access_token?)` - Unfollow a playlist

### 💾 Library Management (5 tools)
- `get_user_saved_tracks(limit=50, offset=0, access_token?)` - Get saved tracks
- `get_user_saved_albums(limit=50, offset=0, access_token?)` - Get saved albums
- `get_user_saved_shows(limit=50, offset=0, access_token?)` - Get saved podcast shows
- `get_user_saved_episodes(limit=50, offset=0, access_token?)` - Get saved podcast episodes
- `get_user_saved_audiobooks(limit=50, offset=0, access_token?)` - Get saved audiobooks

### 📋 Playlist Operations (3 tools)
- `get_current_user_playlists(limit=50, offset=0, access_token?)` - Get current user's playlists
- `get_user_playlists(user_id, limit=50, offset=0, access_token?)` - Get user's public playlists
- `get_playlist_items(playlist_id, limit=100, offset=0, access_token?)` - Get playlist contents

## OAuth Scopes

The following scopes are automatically requested during authentication:

**Read Permissions:**
- `user-read-private` - Access to user's profile information
- `user-read-email` - Access to user's email address
- `user-library-read` - Access to user's saved content
- `user-read-recently-played` - Access to recently played tracks
- `user-top-read` - Access to top artists and tracks
- `playlist-read-private` - Access to private playlists
- `playlist-read-collaborative` - Access to collaborative playlists
- `user-read-playback-state` - Access to current playback state
- `user-read-currently-playing` - Access to currently playing track

**Follow Permissions:**
- `user-follow-read` - Access to followed artists and users
- `user-follow-modify` - Ability to follow/unfollow artists and users

**Playlist Permissions:**
- `playlist-modify-public` - Ability to modify public playlists
- `playlist-modify-private` - Ability to modify private playlists

## Automatic Token Management

✅ **Access tokens automatically refresh** before expiration (every ~55 minutes)
✅ **Refresh tokens valid for 1 year** and auto-extend with each use
✅ **No manual intervention required** - completely automated
✅ **Seamless background operation** - users never see token expiration

### Only re-authentication needed when:
- Refresh token expires (after ~1 year of no use)
- User manually revokes app permissions
- App permissions/scopes are modified

## Default Limits (Optimized for Maximum Data)

All tools use **maximum allowed limits** by default:
- **Most APIs**: 50 items (API maximum)
- **Playlist contents**: 100 items (API maximum)
- **Pagination**: All tools support `offset` parameter for additional data

## File Structure

```
spotify/
├── __init__.py                 # Module initialization
├── spotify_mcp.py             # Main MCP server with 17 tools
├── spotify_oauth_helper.py    # OAuth authentication helper
├── spotify_token_manager.py   # Automatic token management
├── spotify_tokens.json        # Stored OAuth tokens (auto-generated)
├── README.md                  # This file
└── README_zh.md              # Chinese documentation
```

## Security Notes

- 🔒 Tokens stored locally in `spotify_tokens.json`
- 🔄 Access tokens automatically refresh when needed
- 🚫 Never commit tokens or credentials to version control
- 🔐 Keep your Client Secret secure and private
- 🌐 Redirect URI must match exactly between config and Spotify app settings

## Quick Start Example

```bash
# 1. Test credentials
test_spotify_credentials()

# 2. Get token status
get_spotify_token_status()

# 3. Get your profile
get_current_user_profile()

# 4. Get your top tracks
get_user_top_items(item_type="tracks", time_range="short_term")

# 5. Get recently played music
get_user_recently_played()
```