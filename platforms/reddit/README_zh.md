# Reddit API 集成

Reddit平台集成模块，支持OAuth2认证和完整的Reddit API访问功能。

## 🔧 认证配置

### 1. 获取Reddit API凭据

1. 访问 [Reddit Apps](https://www.reddit.com/prefs/apps)
2. 点击 "Create App" 或 "Create Another App"
3. 填写应用信息：
   - **Name**: 应用名称（如：PersonalHub）
   - **App type**: 选择 "web app"
   - **Description**: 应用描述（可选）
   - **About URL**: 关于页面URL（可选）
   - **Redirect URI**: `http://localhost:8888/callback`
4. 创建成功后，记录以下信息：
   - **Client ID**: 应用ID（在应用名称下方）
   - **Client Secret**: 客户端密钥

### 2. 配置认证信息

在项目根目录的 `config` 文件中添加Reddit配置：

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_REDIRECT_URI=http://localhost:8888/callback
```

### 3. OAuth2认证流程

#### 方法一：使用MCP函数进行认证

```python
# 1. 设置OAuth2认证
setup_result = mcp_personalhub_setup_reddit_oauth(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# 2. 访问返回的认证URL进行授权
# 用户需要在浏览器中访问认证URL并授权

# 3. 完成认证（获取授权码后）
complete_result = mcp_personalhub_complete_reddit_oauth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    authorization_code="从回调中获取的授权码"
)
```

#### 方法二：手动配置

如果已有有效的访问令牌，可以直接配置：

```bash
REDDIT_ACCESS_TOKEN=your_access_token
REDDIT_REFRESH_TOKEN=your_refresh_token
```

## 🚀 功能特性

### 📊 账户信息
- **用户概览**: 获取帖子和评论的混合时间线
- **Karma分解**: 查看各个subreddit的karma分布
- **用户偏好**: 获取账户设置和偏好
- **奖杯成就**: 查看Reddit奖杯和成就

### 📝 内容管理
- **发布的帖子**: 获取用户发布的所有帖子
- **评论历史**: 查看用户的评论记录
- **保存的内容**: 获取保存的帖子和评论
- **隐藏的帖子**: 查看隐藏的内容
- **投票记录**: 获取点赞/点踩的内容

### 👥 社区互动
- **订阅的subreddit**: 查看关注的社区
- **管理的社区**: 获取作为版主的subreddit
- **贡献者权限**: 查看有贡献权限的社区

### 💬 消息系统
- **收件箱**: 获取所有消息
- **未读消息**: 查看未读消息
- **已发送**: 查看发送的消息历史

## 🛠️ API函数列表

### 认证管理
```python
# 配置状态检查
get_reddit_config()
test_reddit_credentials()

# OAuth2认证流程
setup_reddit_oauth(client_id, client_secret, redirect_uri?)
complete_reddit_oauth(client_id, client_secret, authorization_code, redirect_uri?)

# 令牌管理
get_reddit_token_status()
refresh_reddit_token()
auto_refresh_reddit_token_if_needed()
```

### 用户信息
```python
# 基本信息
get_user_subreddits(access_token?, limit=100)
get_user_trophies(access_token?)
get_user_preferences(access_token?)
get_user_karma_breakdown(access_token?)

# 社区权限
get_moderated_subreddits(access_token?, limit=100)
get_contributor_subreddits(access_token?, limit=100)
```

### 内容获取
```python
# 帖子和评论
get_user_submitted_posts(username?, access_token?, limit=100, sort="new")
get_user_comments(username?, access_token?, limit=100, sort="new")
get_user_overview(username?, access_token?, limit=100, sort="new")

# 保存和互动
get_saved_content(username?, access_token?, limit=100)
get_hidden_posts(username?, access_token?, limit=100)
get_upvoted_content(username?, access_token?, limit=100)
get_downvoted_content(username?, access_token?, limit=100)
```

### 消息系统
```python
# 消息管理（需要privatemessages权限）
get_inbox_messages(access_token?, limit=100)
get_unread_messages(access_token?, limit=100)
get_sent_messages(access_token?, limit=100)
```

## 📋 使用示例

### 获取用户活动概览
```python
# 获取最近的帖子和评论
overview = get_user_overview(limit=20, sort="new")

# 获取订阅的社区
subreddits = get_user_subreddits(limit=50)

# 获取karma分布
karma = get_user_karma_breakdown()
```

### 查看内容历史
```python
# 获取发布的帖子
posts = get_user_submitted_posts(limit=10, sort="top")

# 获取评论历史
comments = get_user_comments(limit=10, sort="new")

# 获取保存的内容
saved = get_saved_content(limit=20)
```

### 检查消息
```python
# 获取收件箱消息
inbox = get_inbox_messages(limit=10)

# 获取未读消息
unread = get_unread_messages(limit=5)
```

## 🔒 权限范围

Reddit API使用以下OAuth2权限范围：

- `identity`: 访问用户基本信息
- `read`: 读取用户内容和订阅
- `history`: 访问投票和隐藏内容历史
- `privatemessages`: 访问私信（可选，需要特殊权限）

## ⚠️ 注意事项

### API限制
- **请求频率**: Reddit API有严格的频率限制
- **权限要求**: 某些功能需要特定的OAuth权限
- **数据访问**: 只能访问当前认证用户的数据

### 隐私设置
- 用户的隐私设置可能影响数据获取
- 某些内容可能因为用户设置而无法访问
- 私信功能需要额外的权限申请

### 令牌管理
- 访问令牌有效期为1小时
- 刷新令牌可用于自动更新访问令牌
- 建议使用 `auto_refresh_reddit_token_if_needed()` 自动管理令牌

## 🔍 故障排除

### 常见问题

1. **403 Forbidden 错误**
   - 检查OAuth权限范围
   - 确认令牌有效性
   - 验证用户隐私设置

2. **认证失败**
   - 确认Client ID和Secret正确
   - 检查重定向URI匹配
   - 验证授权码未过期

3. **空数据返回**
   - 可能是用户隐私设置限制
   - 检查查询参数（用户名、限制等）
   - 确认用户有相关内容

### 调试建议
- 使用 `get_reddit_config()` 检查配置状态
- 使用 `test_reddit_credentials()` 验证凭据
- 查看 `get_reddit_token_status()` 了解令牌状态

## 📚 相关资源

- [Reddit API文档](https://www.reddit.com/dev/api/)
- [Reddit OAuth2指南](https://github.com/reddit-archive/reddit/wiki/OAuth2)
- [Reddit应用管理](https://www.reddit.com/prefs/apps)
- [Reddit API最佳实践](https://www.reddit.com/wiki/api)
