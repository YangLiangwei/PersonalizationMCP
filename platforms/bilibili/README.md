# Bilibili Platform Integration

This module provides Bilibili API integration for the PersonalizationMCP server.

## Features

- 👤 Get user profile information and statistics
- 🔍 Search videos and get detailed video information
- 📺 Access personal data (watch history, favorites, liked videos, coin history)
- 👥 Get following list and user-uploaded videos
- 📚 Browse "to view later" list and personal collections

## Configuration

Required environment variables:
- `BILIBILI_SESSDATA`: Session data cookie
- `BILIBILI_BILI_JCT`: CSRF token cookie

Optional:
- `BILIBILI_BUVID3`: Browser unique identifier

## Files

- `bilibili_mcp.py`: Main Bilibili MCP integration module
- `README.md`: This documentation file

## Cookie Setup

To access Bilibili data, you need to extract cookies from your browser:

1. **Login to Bilibili**: Visit [bilibili.com](https://www.bilibili.com) and log in
2. **Open Developer Tools**: Press `F12` or right-click and select "Inspect"
3. **Find Cookies**:
   - Click the `Application` tab (Chrome) or `Storage` tab (Firefox)
   - Navigate to `Cookies` > `https://www.bilibili.com`
   - Find these cookie values:

| Cookie Name | Description | Required |
|-------------|-------------|----------|
| `SESSDATA` | Session data, most important auth info | ✅ Required |
| `bili_jct` | CSRF token for protection | ✅ Required |
| `buvid3` | Browser unique identifier | 🔶 Recommended |

## Important Notes

- ⚠️ Bilibili cookies expire periodically and need to be updated
- 🔒 Keep these cookies secure as they provide access to your personal Bilibili data
- 🚫 Don't share these cookies publicly
