# 🎯 PersonalizationMCP

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

一个基于 MCP（模型上下文协议）构建的统一个人数据中心，让 AI 助手能够访问你在多个平台的数字生活，提供真正个性化和有上下文的交互体验。

## 🚀 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/YangLiangwei/PersonalizationMCP.git
   cd PersonalizationMCP
   ```

2. **安装依赖**
   
   **方式 A：使用 conda（推荐）**
   ```bash
   conda create -n personalhub python=3.12
   conda activate personalhub
   pip install "mcp[cli]" httpx python-dotenv
   ```
   
   **方式 B：使用 uv**
   ```bash
   uv venv
   uv add "mcp[cli]" httpx python-dotenv
   ```

3. **配置你的 API 密钥**
   ```bash
   cp config.example config
   # 编辑 config 文件，填入你的实际 API 密钥
   ```

4. **添加到 Cursor 设置**
   
   **如果使用 conda：**
   ```json
   {
     "mcpServers": {
       "personalization-mcp": {
         "command": "/path/to/your/conda/envs/personalhub/bin/python",
         "args": ["/path/to/PersonalizationMCP/server.py"]
       }
     }
   }
   ```
   
   > 💡 **提示**：要查找你的 conda 环境路径，运行：`conda info --envs`
   
   **如果使用 uv：**
   ```json
   {
     "mcpServers": {
       "personalhub": {
         "command": "uv",
         "args": ["run", "python", "/path/to/PersonalizationMCP/server.py"]
       }
     }
   }
   ```

## 🌟 功能特性

### 🎮 Steam 集成
- 获取你的游戏库和详细统计信息及游戏时长
- 查看最近的游戏活动和当前正在玩的游戏
- 获取详细的游戏信息和成就
- 与朋友比较游戏库并获得推荐
- 分析游戏习惯和偏好

### 🎥 YouTube 集成
- 搜索 YouTube 视频并获取详细视频信息
- 获取频道信息和热门视频
- 通过 OAuth2 访问个人数据（订阅、观看历史、播放列表、喜欢的视频）
- 基于你的观看历史获得个性化推荐
- 🔄 **智能令牌管理** - 自动检测并刷新过期的 OAuth2 令牌
- 🛡️ **免维护配置** - 优先使用令牌文件，无需手动更新 MCP 配置

### 📺 Bilibili 集成
- 获取用户资料信息和统计数据
- 搜索视频并获取详细视频信息
- 访问个人数据（观看历史、收藏、点赞视频、投币历史）
- 获取关注列表和用户上传的视频
- 浏览"稍后再看"列表和个人收藏

### 🎵 Spotify 集成
- 完整的 OAuth2 认证和自动令牌管理
- 获取用户档案和音乐库数据
- 访问热门艺术家、曲目和最近播放的音乐
- 社交功能：关注/取消关注艺术家和播放列表
- 音乐库管理：保存的曲目、专辑、节目、单集、有声读物
- 播放列表操作：查看和管理个人播放列表

### 💬 Reddit 集成
- 完整的 OAuth2 认证和自动令牌管理
- 访问用户账户信息、karma分解和偏好设置
- 获取发布的帖子、评论和用户活动概览
- 查看保存的内容、隐藏的帖子和投票历史
- 探索订阅的社区和版主权限
- 消息系统访问（收件箱、未读、已发送消息）

## 📦 安装和设置

### 1. 安装依赖

**方式 A：使用 conda（推荐）**
```bash
conda create -n personalhub python=3.12
conda activate personalhub
pip install "mcp[cli]" httpx python-dotenv
```

**方式 B：使用 uv**
```bash
uv venv
uv add "mcp[cli]" httpx python-dotenv
```

**方式 C：使用 pip 和虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows 系统：venv\Scripts\activate
pip install "mcp[cli]" httpx python-dotenv
```

### 2. 配置设置

复制示例配置文件并填入你的凭据：
```bash
cp config.example config
```

然后编辑 `config` 文件，填入你的实际 API 密钥和令牌。

## 🔧 平台配置

### 🎮 Steam API 设置

#### 获取 Steam API 密钥
1. 访问 [Steam Web API Key 页面](https://steamcommunity.com/dev/apikey)
2. 登录你的 Steam 账户
3. 输入域名（开发时可以使用 `localhost`）
4. 复制生成的 API 密钥

#### 获取 Steam 用户 ID
1. 前往你的 Steam 个人资料页面
2. 查看 URL，例如：`https://steamcommunity.com/profiles/76561198123456789/`
3. 数字 `76561198123456789` 就是你的 Steam ID

#### 配置：
```bash
STEAM_API_KEY=your_steam_api_key_here
STEAM_USER_ID=your_steam_user_id_here
```

### 🎥 YouTube API 设置

#### 获取 YouTube API 密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3：
   - 前往"API 和服务" > "库"
   - 搜索"YouTube Data API v3"
   - 点击"启用"
4. 创建凭据：
   - 前往"API 和服务" > "凭据"
   - 点击"创建凭据" > "API 密钥"
   - 复制生成的 API 密钥

#### 配置：
```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```

#### OAuth2 设置（可选 - 用于访问个人数据）
要访问个人 YouTube 数据（订阅、观看历史等），你需要 OAuth2：

1. 在 Google Cloud Console 中创建 OAuth2 凭据
2. 下载客户端密钥文件
3. 使用 OAuth2 流程获取访问令牌（参见 `platforms/youtube/youtube_oauth_helper.py`）
4. **推荐方式**：使用自动令牌管理
   - 令牌会自动保存到 `youtube_tokens.json` 文件
   - 系统会自动检测过期并刷新令牌
   - 无需在 MCP 配置中设置 `YOUTUBE_ACCESS_TOKEN`

5. **备用方式**：手动设置环境变量
```bash
YOUTUBE_ACCESS_TOKEN=your_oauth2_access_token  # 可选，作为备用
```

### 📺 Bilibili 设置

#### 获取 Bilibili Cookies
要访问 Bilibili 数据，你需要从浏览器中提取 cookies：

1. **登录 Bilibili**：访问 [bilibili.com](https://www.bilibili.com) 并登录
2. **打开开发者工具**：按 `F12` 或右键选择"检查"
3. **查找 Cookies**：
   - 点击 `Application` 标签（Chrome）或 `Storage` 标签（Firefox）
   - 导航到 `Cookies` > `https://www.bilibili.com`
   - 找到这三个 cookie 值：

| Cookie 名称 | 描述 | 是否必需 |
|-------------|-------------|----------|
| `SESSDATA` | 会话数据，最重要的认证信息 | ✅ 必需 |
| `bili_jct` | CSRF 令牌用于保护 | ✅ 必需 |
| `buvid3` | 浏览器唯一标识符 | 🔶 推荐 |

#### 配置：
```bash
BILIBILI_SESSDATA=your_bilibili_sessdata_cookie
BILIBILI_BILI_JCT=your_bilibili_bili_jct_cookie
BILIBILI_BUVID3=your_bilibili_buvid3_cookie
```

⚠️ **重要提示：**
- Bilibili cookies 会定期过期，需要更新
- 请保护好这些 cookies，因为它们提供对你个人 Bilibili 数据的访问权限
- 不要公开分享这些 cookies

### 🎵 Spotify API 设置

> 📖 **详细设置指南**：[platforms/spotify/README.md](platforms/spotify/README.md) | [中文指南](platforms/spotify/README_zh.md)

**快速总结**：
1. 在 [Spotify 开发者控制台](https://developer.spotify.com/dashboard) 创建 Spotify 应用
2. 在应用设置中配置重定向 URI
3. 使用 MCP 工具进行 OAuth2 认证和自动令牌管理

**配置：**
```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=https://example.com/callback
# OAuth2 令牌在认证后自动管理
```

### 💬 Reddit API 设置

> 📖 **详细设置指南**：[platforms/reddit/README.md](platforms/reddit/README.md) | [中文指南](platforms/reddit/README_zh.md)

**快速总结**：
1. 在 [Reddit Apps](https://www.reddit.com/prefs/apps) 创建 Reddit 应用
2. 配置为"web app"并设置重定向 URI
3. 使用 MCP 工具进行 OAuth2 认证和自动令牌管理

**配置：**
```bash
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_REDIRECT_URI=http://localhost:8888/callback
# OAuth2 令牌在认证后自动管理
```

## 🖥️ Cursor 配置

将 MCP 服务器添加到你的 Cursor 设置中：

**如果使用 conda：**
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
        "BILIBILI_BUVID3": "your_bilibili_buvid3",
        "REDDIT_CLIENT_ID": "your_reddit_client_id",
        "REDDIT_CLIENT_SECRET": "your_reddit_client_secret"
      }
    }
  }
}
```

**如果使用 uv：**
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
        "BILIBILI_BUVID3": "your_bilibili_buvid3",
        "REDDIT_CLIENT_ID": "your_reddit_client_id",
        "REDDIT_CLIENT_SECRET": "your_reddit_client_secret"
      }
    }
  }
}
```

**如果使用 pip 和虚拟环境：**
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
        "BILIBILI_BUVID3": "your_bilibili_buvid3",
        "REDDIT_CLIENT_ID": "your_reddit_client_id",
        "REDDIT_CLIENT_SECRET": "your_reddit_client_secret"
      }
    }
  }
}
```

**注意**：对于 YouTube OAuth2 令牌，我们推荐使用自动令牌管理。无需在上述配置中添加 `YOUTUBE_ACCESS_TOKEN`。系统会自动从 `youtube_tokens.json` 文件读取和刷新令牌。

## 🔄 YouTube 智能令牌管理

本系统实现了智能的 YouTube OAuth2 令牌管理，具有以下特性：

### ✨ 核心功能
- **自动过期检测**：系统会自动检测在 5 分钟内过期的令牌
- **自动刷新**：无需手动干预，系统自动刷新过期令牌
- **智能优先级**：优先使用令牌文件，环境变量作为备用
- **免维护配置**：无需手动更新 MCP 配置文件中的令牌

### 🔧 令牌优先级
1. **显式传入的 access_token 参数**（最高优先级）
2. **令牌文件中的自动刷新令牌**（推荐方式）
3. **环境变量中的令牌**（备用方式）

### 📁 文件说明
- `youtube_tokens.json` - 自动生成和维护的令牌文件
- `youtube_oauth_helper.py` - OAuth2 认证助手脚本
- `auto_refresh_youtube_token.py` - 手动令牌刷新工具

### 🛠️ 使用方法
```bash
# 初次 OAuth2 令牌设置
cd platforms/youtube
python3 youtube_oauth_helper.py

# 手动令牌刷新（可选）
python3 auto_refresh_youtube_token.py
```

系统会自动处理所有令牌管理 - 无需手动维护！

## 🛠️ 可用工具

### 🎮 Steam 工具
- `get_steam_library()` - 获取你的游戏库和统计信息
- `get_steam_recent_activity()` - 获取最近的游戏活动
- `get_steam_friends()` - 获取你的 Steam 好友列表
- `get_steam_profile()` - 获取 Steam 个人资料信息
- `get_player_achievements(app_id)` - 获取特定游戏的成就
- `get_user_game_stats(app_id)` - 获取详细的游戏统计信息
- `get_friends_current_games()` - 查看朋友们正在玩的游戏
- `compare_games_with_friend(friend_steamid)` - 比较游戏库
- `get_friend_game_recommendations(friend_steamid)` - 获取游戏推荐

### 🎥 YouTube 工具
- `search_youtube_videos(query)` - 搜索视频
- `get_video_details(video_id)` - 获取详细视频信息
- `get_channel_info(channel_id)` - 获取频道信息
- `get_trending_videos()` - 获取热门视频
- `get_youtube_subscriptions()` - 获取你的订阅（需要 OAuth2）
- `get_youtube_watch_history()` - 获取你的观看历史（需要 OAuth2）
- `get_youtube_playlists()` - 获取你的播放列表（需要 OAuth2）
- `get_youtube_liked_videos()` - 获取你喜欢的视频（需要 OAuth2）
- `refresh_youtube_token()` - 手动刷新 OAuth2 令牌
- `get_youtube_token_status()` - 检查 OAuth2 令牌状态

### 📺 Bilibili 工具
- `get_bilibili_user_info(uid)` - 获取用户资料信息
- `get_my_bilibili_profile()` - 获取你自己的资料
- `search_bilibili_videos(keyword)` - 搜索视频
- `get_bilibili_video_info(bvid)` - 获取详细视频信息
- `get_bilibili_user_videos(uid)` - 获取用户上传的视频
- `get_bilibili_following_list()` - 获取你的关注列表
- `get_bilibili_watch_history()` - 获取你的观看历史
- `get_bilibili_favorites()` - 获取你的收藏视频
- `get_bilibili_liked_videos()` - 获取你点赞的视频
- `get_bilibili_coin_videos()` - 获取你投币的视频
- `get_bilibili_toview_list()` - 获取你的"稍后再看"列表

### 🎵 Spotify 工具（共 17 个）

**认证和配置工具（7 个）：**
- `test_spotify_credentials()` - 测试 API 凭据
- `setup_spotify_oauth()` - 初始化 OAuth 流程
- `complete_spotify_oauth()` - 完成 OAuth 认证
- `get_spotify_token_status()` - 获取令牌状态
- `refresh_spotify_token()` - 手动刷新令牌

**音乐发现和社交工具（9 个）：**
- `get_current_user_profile()` - 获取你的 Spotify 档案
- `get_user_top_items()` - 获取热门艺术家/曲目
- `get_user_recently_played()` - 获取最近播放的音乐
- `get_followed_artists()` - 获取关注的艺术家
- `follow_artists_or_users()` / `unfollow_artists_or_users()` - 社交功能

**音乐库和播放列表工具（6 个）：**
- `get_user_saved_tracks()` / `get_user_saved_albums()` - 音乐库管理
- `get_user_saved_shows()` / `get_user_saved_episodes()` - 播客内容
- `get_current_user_playlists()` / `get_playlist_items()` - 播放列表操作

### 💬 Reddit 工具（共 25 个）

**认证和配置工具（6 个）：**
- `test_reddit_credentials()` - 测试 API 凭据
- `setup_reddit_oauth()` - 初始化 OAuth 流程
- `complete_reddit_oauth()` - 完成 OAuth 认证
- `get_reddit_token_status()` - 获取令牌状态
- `refresh_reddit_token()` - 手动刷新令牌
- `auto_refresh_reddit_token_if_needed()` - 自动令牌管理

**账户信息工具（6 个）：**
- `get_user_subreddits()` - 获取订阅的社区
- `get_user_trophies()` - 获取 Reddit 奖杯和成就
- `get_user_preferences()` - 获取账户设置
- `get_user_karma_breakdown()` - 获取 karma 分布
- `get_moderated_subreddits()` - 获取管理的社区
- `get_contributor_subreddits()` - 获取贡献者权限

**内容和活动工具（10 个）：**
- `get_user_submitted_posts()` - 获取发布的帖子
- `get_user_comments()` - 获取评论历史
- `get_user_overview()` - 获取混合活动时间线
- `get_saved_content()` - 获取保存的帖子/评论
- `get_hidden_posts()` - 获取隐藏的内容
- `get_upvoted_content()` - 获取点赞的内容
- `get_downvoted_content()` - 获取点踩的内容

**消息工具（3 个）：**
- `get_inbox_messages()` - 获取收件箱消息
- `get_unread_messages()` - 获取未读消息
- `get_sent_messages()` - 获取已发送消息

### 🔧 系统工具
- `test_connection()` - 测试 MCP 服务器是否正常工作
- `get_personalization_status()` - 获取整体平台状态
- `test_steam_credentials()` - 测试 Steam API 配置
- `test_youtube_credentials()` - 测试 YouTube API 配置
- `test_bilibili_credentials()` - 测试 Bilibili 配置
- `test_spotify_credentials()` - 测试 Spotify API 配置
- `test_reddit_credentials()` - 测试 Reddit API 配置

## 💬 使用示例

### 游戏分析
- "我最近在玩什么游戏？"
- "显示我玩得最多的 Steam 游戏"
- "我的朋友推荐什么游戏？"
- "比较我和朋友的游戏库"

### 视频内容发现
- "找一些关于机器学习的 YouTube 视频"
- "今天 YouTube 上有什么热门视频？"
- "显示我的 YouTube 观看历史"
- "找一些关于编程的热门 Bilibili 视频"

### 个人数据洞察
- "分析我的游戏习惯和偏好"
- "我最常看什么类型的 YouTube 内容？"
- "显示我的 Bilibili 收藏和点赞视频"

### 音乐和音频分析
- "我最近在 Spotify 上最常听哪些艺术家？"
- "显示我的播放模式并发现音乐偏好"
- "我这个月的热门曲目是什么？"
- "基于我的 Spotify 数据寻找新的音乐推荐"

### Reddit 活动分析
- "我在 Reddit 上最活跃的社区是哪些？"
- "显示我最近的 Reddit 帖子和评论"
- "我在不同 subreddit 的 karma 分布是怎样的？"
- "找到我保存的 Reddit 内容并分析我的兴趣"

## 🧩 Skills（面向 CLI）

仓库已新增 `skills/` 目录，将 `personalhub` CLI 能力拆分为独立 skills：

- `personalhub-status`
- `personalhub-steam`
- `personalhub-youtube`
- `personalhub-bilibili`
- `personalhub-spotify`
- `personalhub-reddit`

每个 skill 独立触发，不做嵌套执行，输出风格保持简洁。

## 🚀 开发

### 运行服务器

**如果使用 conda：**
```bash
conda activate personalhub
python server.py
```

**如果使用 uv：**
```bash
uv run python server.py
```

**如果使用 pip 和虚拟环境：**
```bash
source venv/bin/activate  # Windows 系统：venv\Scripts\activate
python server.py
```

### 测试配置
使用这些工具来测试你的设置：
```python
# 测试各个平台
test_steam_credentials()
test_youtube_credentials()
test_bilibili_credentials()
test_reddit_credentials()

# 检查整体状态
get_personalization_status()
```

### 添加新平台
1. 创建新的 `platform_mcp.py` 文件
2. 使用 `@mcp.tool()` 装饰器实现平台特定的工具
3. 在 `server.py` 中添加设置函数
4. 更新配置文件和文档

## 🔒 隐私和安全

- **本地存储**：所有 API 密钥和令牌都存储在你的本地机器上
- **无数据传输**：你的个人数据永远不会传输给第三方
- **直接 API 调用**：所有 API 调用都是从你的机器直接发送到相应平台
- **安全配置**：使用环境变量或本地配置文件
- **定期更新**：定期轮换 API 密钥和令牌以确保安全

### 安全最佳实践
1. **不要提交敏感文件**：确保 `config`、`.env`、`myinfo.json` 和 `youtube_tokens.json` 在 `.gitignore` 中
2. **定期更新 cookies**：Bilibili cookies 会过期，需要定期更新
3. **使用环境变量**：在生产环境中使用系统环境变量
4. **文件权限**：确保配置文件只有你可以读取
5. **YouTube 令牌安全**：系统会在本地文件中安全地自动管理 OAuth2 令牌
6. **渐进式配置**：你可以逐步配置平台 - 缺少凭据不会导致错误

## 🆘 故障排除

### 常见问题

**问：Bilibili cookies 不工作？**
答：Cookies 会定期过期。请从浏览器重新提取并更新你的配置。

**问：Steam API 速率限制？**
答：Steam API 有速率限制。避免频繁调用并实施合理的延迟。

**问：YouTube API 配额超出？**
答：YouTube API 有每日配额。你可以请求增加配额或优化使用。

**问：YouTube OAuth2 令牌过期？**
答：系统会自动刷新过期令牌。如果需要手动刷新，请使用 `refresh_youtube_token()`。

**问：我可以只使用某些平台吗？**
答：可以！你可以只配置你想使用的平台。缺少凭据不会导致错误。

**问：如何验证我的配置？**
答：使用测试工具或调用 `get_personalization_status()` 来检查所有平台。

### 获取帮助
1. 检查配置文件格式
2. 验证 API 密钥和 cookies 是否有效
3. 查看 MCP 服务器日志
4. 使用测试工具验证每个平台配置

## 🤝 贡献

欢迎贡献！以下是你可以帮助的方式：

1. **Fork 仓库**
2. **创建功能分支**：`git checkout -b feature/amazing-feature`
3. **进行更改**并在适用时添加测试
4. **提交更改**：`git commit -m 'Add amazing feature'`
5. **推送到分支**：`git push origin feature/amazing-feature`
6. **打开 Pull Request**

### 添加新平台

想要添加对新平台的支持？请按照以下步骤：

1. 创建新的 `platform_mcp.py` 文件（例如 `spotify_mcp.py`）
2. 使用 `@mcp.tool()` 装饰器实现平台特定的工具
3. 添加设置函数并在 `server.py` 中集成
4. 更新配置文件和文档
5. 添加测试和示例

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [模型上下文协议 (MCP)](https://modelcontextprotocol.io/) 提供了出色的协议
- [Anthropic](https://www.anthropic.com/) 开发了 Claude 和 MCP
- 所有使这种集成成为可能的平台 API

## ⭐ Star 历史

如果你觉得这个项目有用，请考虑在 GitHub 上给它一个 star！

---

**用 ❤️ 为连接你的数字生活与 AI 而制作**
