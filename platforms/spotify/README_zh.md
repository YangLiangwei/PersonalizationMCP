# Spotify 平台集成

此模块为 PersonalizationMCP 提供全面的 Spotify API 集成，允许访问个人音乐数据、偏好和用户交互功能。

## 功能特性

- ✅ **完整的 OAuth2 认证** 与自动令牌刷新
- ✅ **用户档案和音乐库管理**
- ✅ **音乐发现** - 热门艺术家、曲目和最近播放
- ✅ **社交功能** - 关注/取消关注艺术家和播放列表
- ✅ **音乐库管理** - 收藏的曲目、专辑、播客、单集、有声书
- ✅ **播放列表操作** - 查看和管理播放列表
- ✅ **无缝令牌管理** - 无需手动刷新

## 设置步骤

### 1. 创建 Spotify 应用

1. 前往 [Spotify 开发者控制台](https://developer.spotify.com/dashboard)
2. 创建新应用
3. 在应用设置中配置重定向 URI
4. 记录下你的 Client ID 和 Client Secret

### 2. 配置环境变量

在你的配置文件中添加以下内容：

```bash
# Spotify API 配置
SPOTIFY_CLIENT_ID=你的客户端ID
SPOTIFY_CLIENT_SECRET=你的客户端密钥
SPOTIFY_REDIRECT_URI=https://example.com/callback
```

### 3. 完成 OAuth 认证

使用 MCP 工具完成 OAuth 认证：

```bash
# 步骤 1：初始化 OAuth 流程
setup_spotify_oauth client_id="你的客户端ID" client_secret="你的客户端密钥"

# 步骤 2：访问提供的授权 URL 并授权应用
# 步骤 3：从回调 URL 中复制授权码

# 步骤 4：完成认证
complete_spotify_oauth client_id="你的客户端ID" client_secret="你的客户端密钥" authorization_code="你的授权码"
```

## 可用的 MCP 工具（共 17 个）

### 🔐 认证和配置（7 个工具）
- `test_spotify_credentials()` - 测试 API 凭据
- `get_spotify_config()` - 获取配置状态
- `setup_spotify_oauth(client_id, client_secret, redirect_uri?)` - 初始化 OAuth 流程
- `complete_spotify_oauth(client_id, client_secret, authorization_code, redirect_uri?)` - 完成 OAuth 认证
- `refresh_spotify_token()` - 手动刷新访问令牌
- `auto_refresh_spotify_token_if_needed()` - 根据需要自动刷新
- `get_spotify_token_status()` - 获取令牌状态信息

### 👤 用户档案（2 个工具）
- `get_current_user_profile(access_token?)` - 获取当前用户档案
- `get_user_profile(user_id, access_token?)` - 获取指定用户档案

### 🎵 音乐发现（2 个工具）
- `get_user_top_items(item_type="tracks", time_range="medium_term", limit=50, access_token?)` - 获取热门艺术家或曲目
- `get_user_recently_played(limit=50, access_token?)` - 获取最近播放的曲目

### 👥 社交功能（5 个工具）
- `get_followed_artists(limit=50, access_token?)` - 获取关注的艺术家
- `follow_artists_or_users(ids, follow_type="artist", access_token?)` - 关注艺术家/用户
- `unfollow_artists_or_users(ids, follow_type="artist", access_token?)` - 取消关注艺术家/用户
- `follow_playlist(playlist_id, public=true, access_token?)` - 关注播放列表
- `unfollow_playlist(playlist_id, access_token?)` - 取消关注播放列表

### 💾 音乐库管理（5 个工具）
- `get_user_saved_tracks(limit=50, offset=0, access_token?)` - 获取收藏的曲目
- `get_user_saved_albums(limit=50, offset=0, access_token?)` - 获取收藏的专辑
- `get_user_saved_shows(limit=50, offset=0, access_token?)` - 获取收藏的播客节目
- `get_user_saved_episodes(limit=50, offset=0, access_token?)` - 获取收藏的播客单集
- `get_user_saved_audiobooks(limit=50, offset=0, access_token?)` - 获取收藏的有声书

### 📋 播放列表操作（3 个工具）
- `get_current_user_playlists(limit=50, offset=0, access_token?)` - 获取当前用户的播放列表
- `get_user_playlists(user_id, limit=50, offset=0, access_token?)` - 获取用户的公开播放列表
- `get_playlist_items(playlist_id, limit=100, offset=0, access_token?)` - 获取播放列表内容

## OAuth 权限范围

认证期间自动请求以下权限范围：

**读取权限：**
- `user-read-private` - 访问用户档案信息
- `user-read-email` - 访问用户邮箱地址
- `user-library-read` - 访问用户收藏的内容
- `user-read-recently-played` - 访问最近播放的曲目
- `user-top-read` - 访问热门艺术家和曲目
- `playlist-read-private` - 访问私人播放列表
- `playlist-read-collaborative` - 访问协作播放列表
- `user-read-playback-state` - 访问当前播放状态
- `user-read-currently-playing` - 访问当前播放曲目

**关注权限：**
- `user-follow-read` - 访问关注的艺术家和用户
- `user-follow-modify` - 关注/取消关注艺术家和用户的能力

**播放列表权限：**
- `playlist-modify-public` - 修改公开播放列表的能力
- `playlist-modify-private` - 修改私人播放列表的能力

## 自动令牌管理

✅ **访问令牌在过期前自动刷新**（约每 55 分钟）
✅ **刷新令牌有效期 1 年** 并在每次使用时自动延长
✅ **无需手动干预** - 完全自动化
✅ **无缝后台操作** - 用户从不会遇到令牌过期

### 仅在以下情况需要重新认证：
- 刷新令牌过期（约 1 年未使用后）
- 用户手动撤销应用权限
- 应用权限/范围被修改

## 默认限制（为最大数据量优化）

所有工具默认使用**最大允许限制**：
- **大部分 API**：50 项（API 最大值）
- **播放列表内容**：100 项（API 最大值）
- **分页**：所有工具都支持 `offset` 参数获取更多数据

## 文件结构

```
spotify/
├── __init__.py                 # 模块初始化
├── spotify_mcp.py             # 主要 MCP 服务器（17 个工具）
├── spotify_oauth_helper.py    # OAuth 认证助手
├── spotify_token_manager.py   # 自动令牌管理
├── spotify_tokens.json        # 存储的 OAuth 令牌（自动生成）
├── README.md                  # 英文文档
└── README_zh.md              # 本文件
```

## 安全注意事项

- 🔒 令牌存储在本地的 `spotify_tokens.json` 文件中
- 🔄 访问令牌在需要时自动刷新
- 🚫 切勿将令牌或凭据提交到版本控制系统
- 🔐 保持你的 Client Secret 安全和私密
- 🌐 重定向 URI 必须在配置和 Spotify 应用设置中完全匹配

## 快速开始示例

```bash
# 1. 测试凭据
test_spotify_credentials()

# 2. 获取令牌状态
get_spotify_token_status()

# 3. 获取你的档案
get_current_user_profile()

# 4. 获取你的热门曲目
get_user_top_items(item_type="tracks", time_range="short_term")

# 5. 获取最近播放的音乐
get_user_recently_played()
```