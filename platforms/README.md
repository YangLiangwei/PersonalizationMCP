# Platform Integrations

This directory contains all platform-specific integrations for the PersonalizationMCP server.

## Structure

```
platforms/
├── __init__.py
├── README.md (this file)
├── common/              # Shared utilities and configurations
│   ├── __init__.py
│   ├── platforms_config.py
│   └── README.md
├── steam/               # Steam platform integration
│   ├── __init__.py
│   ├── steam_mcp.py
│   └── README.md
├── youtube/             # YouTube platform integration
│   ├── __init__.py
│   ├── youtube_mcp.py
│   ├── youtube_oauth_helper.py
│   ├── youtube_token_manager.py
│   ├── auto_refresh_youtube_token.py
│   ├── youtube_tokens.json
│   └── README.md
└── bilibili/            # Bilibili platform integration
    ├── __init__.py
    ├── bilibili_mcp.py
    └── README.md
```

## Available Platforms

### ✅ Implemented Platforms

| Platform | Status | Features |
|----------|--------|----------|
| 🎮 **Steam** | ✅ Active | Game library, achievements, friends, recommendations |
| 🎥 **YouTube** | ✅ Active | Video search, subscriptions, watch history, liked videos |
| 📺 **Bilibili** | ✅ Active | Video search, watch history, favorites, following list |

### 🚧 Future Platforms

| Platform | Status | Planned Features |
|----------|--------|------------------|
| 🎵 **Spotify** | 📋 Planned | Music library, playlists, listening history |
| 🐦 **Twitter/X** | 📋 Planned | Tweets, followers, timeline |
| 🐙 **GitHub** | 📋 Planned | Repositories, commits, issues |

## Adding a New Platform

To add a new platform integration:

1. **Create platform directory**:
   ```bash
   mkdir platforms/newplatform
   touch platforms/newplatform/__init__.py
   ```

2. **Create main integration file**:
   ```python
   # platforms/newplatform/newplatform_mcp.py
   from mcp.server.fastmcp import FastMCP
   
   def setup_newplatform_mcp(mcp: FastMCP):
       @mcp.tool()
       def get_newplatform_data():
           # Implementation here
           pass
   ```

3. **Add to platforms_config.py**:
   ```python
   "newplatform": PlatformConfig(
       name="New Platform",
       enabled=True,
       required_env_vars=["NEWPLATFORM_API_KEY"],
       optional_env_vars=[]
   )
   ```

4. **Update server.py**:
   ```python
   from platforms.newplatform.newplatform_mcp import setup_newplatform_mcp
   
   # In setup_all_platforms():
   setup_newplatform_mcp(mcp)
   ```

5. **Create documentation**:
   - Add `platforms/newplatform/README.md`
   - Update main README.md

## Configuration

Each platform has its own configuration requirements. See individual platform README files for detailed setup instructions:

- [Steam Configuration](steam/README.md)
- [YouTube Configuration](youtube/README.md)
- [Bilibili Configuration](bilibili/README.md)
- [Common Utilities](common/README.md)
