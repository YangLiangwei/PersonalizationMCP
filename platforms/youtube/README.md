# YouTube Platform Integration

This module provides YouTube API integration for the PersonalHub server.

## Features

- 🔍 Search YouTube videos and get detailed video information
- 📺 Get channel information and trending videos
- 👤 Access personal data with OAuth2 (subscriptions, watch history, playlists, liked videos)
- 🎯 Get personalized recommendations based on your viewing history
- 🔄 **自动令牌刷新** - 智能检测并自动刷新过期的OAuth2令牌
- 🛡️ **智能令牌管理** - 优先使用令牌文件，无需手动维护MCP配置

## Configuration

### Required Environment Variables
- `YOUTUBE_API_KEY`: Your YouTube Data API v3 key

### OAuth2 Configuration (for personal data access)
**推荐方式**: 使用令牌文件自动管理
- 令牌文件: `youtube_tokens.json` (自动生成和维护)
- 系统会自动检测令牌过期并刷新

**备用方式**: 环境变量
- `YOUTUBE_ACCESS_TOKEN`: OAuth2 access token (可选，作为备用)

### 智能令牌优先级
1. 显式传入的 access_token 参数
2. **令牌文件中的自动刷新令牌** (推荐)
3. 环境变量中的令牌 (备用)

## Files

- `youtube_mcp.py`: Main YouTube MCP integration module
- `youtube_oauth_helper.py`: OAuth2 authentication helper
- `youtube_token_manager.py`: Token management utilities
- `auto_refresh_youtube_token.py`: Automatic token refresh script
- `youtube_tokens.json`: Token storage (auto-generated)
- `README.md`: This documentation file

## API Setup

### Step 1: Create Google Cloud Project and Get API Key

1. **Access Google Cloud Console**
   - Open [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create New Project**
   - Click the project selector at the top
   - Click "New Project"
   - Project name: Enter `PersonalHub` or any name you prefer
   - Click "Create"

3. **Enable YouTube Data API v3**
   - In the left menu, click "APIs & Services" → "Library"
   - Search for `YouTube Data API v3`
   - Click on "YouTube Data API v3" in the search results
   - Click the "Enable" button

4. **Create API Key**
   - In the left menu, click "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "API key"
   - Copy the generated API key (like: `AIzaSyBOROoarHUQW4gVblNUprxFeovH25qUfuw`)
   - (Optional) Click "Restrict key" to set usage restrictions

### Step 2: Setup OAuth2 (For Personal Data Access)

**Why OAuth2 is needed:**
- API Key only accesses public data (search videos, video info, etc.)
- Personal data (liked videos, subscriptions, playlists) requires OAuth2 authentication

**Detailed Setup Steps:**

#### 1. Configure OAuth Consent Screen
- Go to "APIs & Services" → "Credentials" page
- Click "Configure Consent Screen"
- User type: Select "External" (for personal use)
- Click "CREATE"

#### 2. Fill App Information
- App name: `PersonalHub`
- User support email: Select your email
- Developer contact information: Enter your email
- Click "SAVE AND CONTINUE"

#### 3. Add Scopes (Optional but Recommended)
- Click "ADD OR REMOVE SCOPES"
- Search and add: `https://www.googleapis.com/auth/youtube.readonly`
- Click "UPDATE" → "SAVE AND CONTINUE"

#### 4. Add Test Users
- Click "+ ADD USERS"
- Enter your Google email address
- Click "SAVE AND CONTINUE"

#### 5. Create OAuth Client ID
- Go back to "Credentials" page
- Click "+ CREATE CREDENTIALS" → "OAuth client ID"
- Application type: Select "TV and Limited Input device"
- Name: `PersonalHub Server`
- Click "CREATE"

#### 6. Get Credentials Information
- After creation, a popup will show containing:
  - **Client ID**: `402070639637-xxxxxx.apps.googleusercontent.com`
  - **Client Secret**: `GOCSPX-xxxxxx`
- Click "DOWNLOAD JSON" to save credentials file
- Or manually copy Client ID and Client Secret

### Step 3: OAuth Authentication

**Method A: Using MCP Tools (Recommended)**

After PersonalHub is running, use the built-in MCP tools:

1. **Start OAuth Setup**
   ```
   setup_youtube_oauth(client_id, client_secret)
   ```

2. **Complete Authorization**
   - Tool will provide verification URL and code
   - Visit URL on any device and enter the code
   - Complete Google authorization

3. **Finish Setup**
   ```
   complete_youtube_oauth(client_id, client_secret, device_code)
   ```

**Method B: Using Python Script (Alternative)**
```bash
python youtube_oauth_helper.py
```

### Authentication Flow
1. System displays device code and verification URL
2. Open browser on any device and visit the URL
3. Enter the device code
4. Sign in with Google account and authorize PersonalHub
5. Tokens are automatically saved and managed

### Important Notes
- OAuth2 tokens are automatically managed after first authentication
- System automatically handles token refresh
- If tokens expire, you'll be prompted to re-authenticate
- Keep credentials file secure, don't share publicly

### Troubleshooting
- If you encounter "OAuth app not verified" warning, click "Advanced" → "Go to PersonalHub (unsafe)"
- Make sure your email is added as a test user in OAuth consent screen
- Ensure YouTube Data API v3 is enabled in your Google Cloud project
