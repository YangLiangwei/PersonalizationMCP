# 🎯 PersonalHub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

A unified personal data hub built on MCP (Model Context Protocol) that allows AI assistants to access your digital life from multiple platforms, providing truly personalized and contextual interactions.

> 📖 **中文文档**: [README_zh.md](README_zh.md)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PersonalHub.git
   cd PersonalHub
   ```

2. **Install dependencies**
   
   > 📖 **See detailed installation instructions: [Installation and Setup](#-installation-and-setup)**

3. **Configure your API keys**
   ```bash
   cp config.example config
   # Edit config file with your actual API keys
   ```

4. **Add to Cursor settings**
   
   > 📖 **See detailed MCP configuration: [Cursor Configuration](#-cursor-configuration)**

## 🌟 Features

### 🎮 Steam Integration
- Get your game library with detailed statistics and playtime
- View recent gaming activity and currently playing games
- Get detailed game information and achievements
- Compare games with friends and get recommendations
- Analyze gaming habits and preferences

### 🎥 YouTube Integration
- Search YouTube videos and get detailed video information
- Get channel information and trending videos
- Access personal data with OAuth2 (subscriptions, playlists, liked videos)
- Get personalized recommendations based on your viewing history
- 🔄 **Smart Token Management** - Automatically detect and refresh expired OAuth2 tokens
- 🛡️ **Maintenance-Free Configuration** - Prioritize token files, no need to manually update MCP configuration

### 📺 Bilibili Integration
- Get user profile information and statistics
- Search videos and get detailed video information
- Access personal data (watch history, favorites, liked videos, coin history)
- Get following list and user-uploaded videos
- Browse "to view later" list and personal collections

### 🎵 Spotify Integration
- Complete OAuth2 authentication with automatic token management
- Get user profile and music library data
- Access top artists, tracks, and recently played music
- Social features: follow/unfollow artists and playlists
- Library management: saved tracks, albums, shows, episodes, audiobooks
- Playlist operations: view and manage personal playlists

## 📦 Installation and Setup

### 1. Install Dependencies

Due to the complexity of bilibili-api dependencies (especially lxml compilation issues), installation requires specific steps. Choose one of the methods below:

#### **Option A: Using conda (Recommended)**
```bash
# 1. Create conda environment
conda create -n personalhub python=3.12
conda activate personalhub

# 2. Install lxml via conda (avoids compilation issues)
conda install lxml

# 3. Install remaining packages
pip install bilibili-api --no-deps
pip install -r requirements.txt
```

#### **Option B: Using uv**
```bash
# 1. Install uv if not already installed
# Visit: https://docs.astral.sh/uv/getting-started/installation/

# 2. Create environment and install core dependencies
uv venv
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install bilibili-api and its dependencies separately (due to version conflicts)
uv pip install lxml  # Install lxml first (uses precompiled wheel)
uv pip install bilibili-api --no-deps  # Install bilibili-api without dependencies
uv pip install aiohttp beautifulsoup4 colorama PyYAML brotli urllib3  # Install required dependencies
```

#### **Option C: Using pip (Manual Multi-Step Installation)**
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install packages in specific order to avoid compilation issues
pip install lxml  # Install lxml first (uses precompiled wheel)
pip install bilibili-api --no-deps  # Install bilibili-api without dependencies
pip install -r requirements.txt  # Install all other dependencies
```

> **⚠️ Important**: The bilibili-api package has complex dependency requirements that can cause compilation failures on some systems. The multi-step installation approach ensures compatibility by installing lxml first, then bilibili-api without its conflicting dependencies, and finally all other required packages.

### 2. Configuration Setup

Copy the example configuration file and fill in your credentials:
```bash
cp config.example config
```

Then edit the `config` file with your actual API keys and tokens.

## 🔧 Platform Configuration

### 🎮 Steam API Setup

> 📖 **Detailed setup guide**: [platforms/steam/README.md](platforms/steam/README.md) | [中文指南](platforms/steam/README_zh.md)

**Quick summary**: Get Steam API key and User ID, then configure:
```bash
STEAM_API_KEY=your_steam_api_key_here
STEAM_USER_ID=your_steam_user_id_here
```

### 🎥 YouTube API Setup

> 📖 **Detailed setup guide**: [platforms/youtube/README.md](platforms/youtube/README.md) | [中文指南](platforms/youtube/README_zh.md)

**Quick summary**: 
1. Get YouTube API key from Google Cloud Console
2. For personal data access, set up OAuth2 with "TV and Limited Input device" type
3. Use MCP tools for easy authentication

**Configuration:**
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
# OAuth2 tokens are managed automatically after setup
```

### 📺 Bilibili Setup

> 📖 **Detailed setup guide**: [platforms/bilibili/README.md](platforms/bilibili/README.md) | [中文指南](platforms/bilibili/README_zh.md)

**Quick summary**: Extract cookies from your browser after logging into Bilibili

**Configuration:**
```bash
BILIBILI_SESSDATA=your_bilibili_sessdata_cookie
BILIBILI_BILI_JCT=your_bilibili_bili_jct_cookie
BILIBILI_BUVID3=your_bilibili_buvid3_cookie
```

### 🎵 Spotify API Setup

> 📖 **Detailed setup guide**: [platforms/spotify/README.md](platforms/spotify/README.md) | [中文指南](platforms/spotify/README_zh.md)

**Quick summary**: 
1. Create a Spotify app in [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Configure redirect URIs in your app settings
3. Use MCP tools for OAuth2 authentication with automatic token management

**Configuration:**
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=https://example.com/callback
# OAuth2 tokens are managed automatically after authentication
```

## 🖥️ Cursor Configuration

Add the MCP server to your Cursor settings:

**If using conda:**
```json
{
  "mcpServers": {
    "personalhub": {
      "command": "/path/to/your/conda/envs/personalhub/bin/python",
      "args": ["/absolute/path/to/your/project/server.py"],
      "env": {
        "STEAM_API_KEY": "your_steam_api_key",
        "STEAM_USER_ID": "your_steam_user_id",
        "YOUTUBE_API_KEY": "your_youtube_api_key",
        "BILIBILI_SESSDATA": "your_bilibili_sessdata",
        "BILIBILI_BILI_JCT": "your_bilibili_bili_jct",
        "BILIBILI_BUVID3": "your_bilibili_buvid3"
      }
    }
  }
}
```

**If using uv:**
```json
{
  "mcpServers": {
    "personalhub": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/your/project/server.py"],
      "env": {
        "STEAM_API_KEY": "your_steam_api_key",
        "STEAM_USER_ID": "your_steam_user_id",
        "YOUTUBE_API_KEY": "your_youtube_api_key",
        "BILIBILI_SESSDATA": "your_bilibili_sessdata",
        "BILIBILI_BILI_JCT": "your_bilibili_bili_jct",
        "BILIBILI_BUVID3": "your_bilibili_buvid3"
      }
    }
  }
}
```

**If using pip with virtual environment:**
```json
{
  "mcpServers": {
    "personalhub": {
      "command": "/absolute/path/to/your/project/venv/bin/python",
      "args": ["/absolute/path/to/your/project/server.py"],
      "env": {
        "STEAM_API_KEY": "your_steam_api_key",
        "STEAM_USER_ID": "your_steam_user_id",
        "YOUTUBE_API_KEY": "your_youtube_api_key",
        "BILIBILI_SESSDATA": "your_bilibili_sessdata",
        "BILIBILI_BILI_JCT": "your_bilibili_bili_jct",
        "BILIBILI_BUVID3": "your_bilibili_buvid3"
      }
    }
  }
}
```

**Note**: For YouTube OAuth2 tokens, we recommend using automatic token management. No need to add `YOUTUBE_ACCESS_TOKEN` in the above configuration. The system will automatically read and refresh tokens from the `youtube_tokens.json` file.

## 🔄 YouTube Smart Token Management

This system implements intelligent YouTube OAuth2 token management with the following features:

### ✨ Core Features
- **Automatic Expiration Detection**: System automatically detects tokens expiring within 5 minutes
- **Auto-Refresh**: No manual intervention needed, system automatically refreshes expired tokens
- **Smart Priority**: Prioritizes token files, with environment variables as backup
- **Maintenance-Free Configuration**: No need to manually update tokens in MCP configuration files

### 🔧 Token Priority
1. **Explicitly passed access_token parameter** (Highest priority)
2. **Auto-refresh tokens from token file** (Recommended method)
3. **Tokens from environment variables** (Backup method)


The system automatically handles all token management - no manual maintenance required!

## 🛠️ Available Tools

### 🎮 Steam Tools
- `get_steam_library()` - Get your game library with statistics
- `get_steam_recent_activity()` - Get recent gaming activity
- `get_steam_friends()` - Get your Steam friends list
- `get_steam_profile()` - Get Steam profile information
- `get_player_achievements(app_id)` - Get achievements for a specific game
- `get_user_game_stats(app_id)` - Get detailed game statistics
- `get_friends_current_games()` - See what games your friends are playing
- `compare_games_with_friend(friend_steamid)` - Compare game libraries
- `get_friend_game_recommendations(friend_steamid)` - Get game recommendations

### 🎥 YouTube Tools
- `search_youtube_videos(query)` - Search for videos
- `get_video_details(video_id)` - Get detailed video information
- `get_channel_info(channel_id)` - Get channel information
- `get_trending_videos()` - Get trending videos
- `get_youtube_subscriptions()` - Get your subscriptions (OAuth2 required)
- `get_youtube_playlists()` - Get your playlists (OAuth2 required)
- `get_youtube_liked_videos()` - Get your liked videos (OAuth2 required)
- `refresh_youtube_token()` - Manually refresh OAuth2 token
- `get_youtube_token_status()` - Check OAuth2 token status

### 📺 Bilibili Tools
- `get_bilibili_user_info(uid)` - Get user profile information
- `get_my_bilibili_profile()` - Get your own profile
- `search_bilibili_videos(keyword)` - Search for videos
- `get_bilibili_video_info(bvid)` - Get detailed video information
- `get_bilibili_user_videos(uid)` - Get videos uploaded by a user
- `get_bilibili_following_list()` - Get your following list
- `get_bilibili_watch_history()` - Get your watch history
- `get_bilibili_favorites()` - Get your favorite videos
- `get_bilibili_liked_videos()` - Get your liked videos
- `get_bilibili_coin_videos()` - Get videos you've given coins to
- `get_bilibili_toview_list()` - Get your "to view later" list

### 🎵 Spotify Tools (17 Total)

**Authentication & Configuration (7 tools):**
- `test_spotify_credentials()` - Test API credentials
- `setup_spotify_oauth()` - Initialize OAuth flow
- `complete_spotify_oauth()` - Complete OAuth authentication
- `get_spotify_token_status()` - Get token status
- `refresh_spotify_token()` - Manual token refresh

**Music Discovery & Social (9 tools):**
- `get_current_user_profile()` - Get your Spotify profile
- `get_user_top_items()` - Get top artists/tracks
- `get_user_recently_played()` - Get recently played music
- `get_followed_artists()` - Get followed artists
- `follow_artists_or_users()` / `unfollow_artists_or_users()` - Social features

**Library & Playlists (6 tools):**
- `get_user_saved_tracks()` / `get_user_saved_albums()` - Library management
- `get_user_saved_shows()` / `get_user_saved_episodes()` - Podcast content
- `get_current_user_playlists()` / `get_playlist_items()` - Playlist operations

### 🔧 System Tools
- `test_connection()` - Test if MCP server is working
- `get_personalization_status()` - Get overall platform status
- `test_steam_credentials()` - Test Steam API configuration
- `test_youtube_credentials()` - Test YouTube API configuration
- `test_bilibili_credentials()` - Test Bilibili configuration
- `test_spotify_credentials()` - Test Spotify API configuration

## 💬 Usage Examples

### Gaming Analysis
- "What games have I been playing recently?"
- "Show me my most played Steam games"
- "What games do my friends recommend?"
- "Compare my game library with my friend's"

### Video Content Discovery
- "Find YouTube videos about machine learning"
- "What are the trending videos on YouTube today?"
- "Show me my YouTube liked videos"
- "Find popular Bilibili videos about programming"

### Personal Data Insights
- "Analyze my gaming habits and preferences"
- "What type of YouTube content do I watch most?"
- "Show me my Bilibili favorites and liked videos"

### Music & Audio Analysis
- "What artists have I been listening to most lately on Spotify?"
- "Show me my recently played music and find patterns"
- "What are my top tracks from the past month?"
- "Find new music recommendations based on my Spotify data"

## 🚀 Development

### Running the Server

**If using conda:**
```bash
conda activate personalhub
python server.py
```

**If using uv:**
```bash
uv run python server.py
```

**If using pip with virtual environment:**
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python server.py
```

### Testing Configuration
Use these tools to test your setup:
```python
# Test individual platforms
test_steam_credentials()
test_youtube_credentials()
test_bilibili_credentials()

# Check overall status
get_personalization_status()
```

### Adding New Platforms
1. Create a new `platform_mcp.py` file
2. Implement the platform-specific tools using `@mcp.tool()` decorator
3. Add setup function to `server.py`
4. Update configuration files and documentation

## 🔒 Privacy and Security

- **Local Storage**: All API keys and tokens are stored locally on your machine
- **No Data Transmission**: Your personal data is never transmitted to third parties
- **Direct API Calls**: All API calls are made directly from your machine to the respective platforms
- **Secure Configuration**: Use environment variables or local config files
- **Regular Updates**: Rotate API keys and tokens regularly for security

### Security Best Practices
1. **Don't commit sensitive files**: Ensure `config`, `.env`, `myinfo.json`, and `youtube_tokens.json` are in `.gitignore`
2. **Update cookies regularly**: Bilibili cookies expire and need periodic updates
3. **Use environment variables**: In production, use system environment variables
4. **File permissions**: Ensure config files are only readable by you
5. **YouTube token security**: The system automatically manages OAuth2 tokens securely in local files
6. **Gradual configuration**: You can configure platforms incrementally - missing credentials won't cause errors

## 🆘 Troubleshooting

### Common Issues

**Q: Bilibili cookies not working?**
A: Cookies expire regularly. Re-extract them from your browser and update your config.

**Q: Steam API rate limits?**
A: Steam API has rate limits. Avoid frequent calls and implement reasonable delays.

**Q: YouTube API quota exceeded?**
A: YouTube API has daily quotas. You can request quota increases or optimize your usage.

**Q: YouTube OAuth2 token expired?**
A: The system automatically refreshes expired tokens. If manual refresh is needed, use `refresh_youtube_token()`.

**Q: Can I use only some platforms?**
A: Yes! You can configure only the platforms you want to use. Missing credentials won't cause errors.

**Q: How to verify my configuration?**
A: Use the test tools or call `get_personalization_status()` to check all platforms.

### Getting Help
1. Check configuration file format
2. Verify API keys and cookies are valid
3. Review MCP server logs
4. Use test tools to validate each platform configuration

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests if applicable
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Adding New Platforms

Want to add support for a new platform? Follow these steps:

1. Create a new `platform_mcp.py` file (e.g., `spotify_mcp.py`)
2. Implement platform-specific tools using the `@mcp.tool()` decorator
3. Add a setup function and integrate it in `server.py`
4. Update configuration files and documentation
5. Add tests and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) for the amazing protocol
- [Anthropic](https://www.anthropic.com/) for Claude and MCP development
- All the platform APIs that make this integration possible

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for connecting your digital life with AI**















