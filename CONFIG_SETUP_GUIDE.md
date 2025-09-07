# 🔧 PersonalHub 配置设置指南

本指南将帮助你正确配置所有平台的API密钥和认证信息。

## 📋 快速开始

1. 复制 `config.example` 文件为 `config` 或 `.env`
2. 按照下面的指南填入你的实际配置值
3. 确保配置文件在项目根目录

```bash
cp config.example config
# 或者
cp config.example .env
```

## 🎮 Steam API 配置

### 获取 Steam API Key
1. 访问 [Steam Web API Key 页面](https://steamcommunity.com/dev/apikey)
2. 登录你的Steam账户
3. 填写域名（可以填 `localhost` 用于开发）
4. 复制生成的API Key

### 获取 Steam User ID
1. 访问你的Steam个人资料页面
2. 查看URL，例如：`https://steamcommunity.com/profiles/76561198123456789/`
3. 数字部分 `76561198123456789` 就是你的Steam ID

### 配置示例：
```bash
STEAM_API_KEY=ABCD1234567890EFGH
STEAM_USER_ID=76561198123456789
```

## 🎥 YouTube API 配置

### 获取 YouTube API Key
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 YouTube Data API v3：
   - 进入 "APIs & Services" > "Library"
   - 搜索 "YouTube Data API v3"
   - 点击启用
4. 创建凭据：
   - 进入 "APIs & Services" > "Credentials"
   - 点击 "Create Credentials" > "API Key"
   - 复制生成的API Key

### 配置示例：
```bash
YOUTUBE_API_KEY=AIzaSyABC123DEF456GHI789JKL
```

### 获取 OAuth2 访问令牌（可选，用于个人数据）
如果需要访问个人YouTube数据（订阅、观看历史等），需要OAuth2令牌：

1. 在Google Cloud Console中创建OAuth2凭据
2. 下载客户端密钥文件
3. 使用OAuth2流程获取访问令牌
4. 设置环境变量：
```bash
YOUTUBE_ACCESS_TOKEN=ya29.a0ABC123...
```

## 📺 Bilibili API 配置

### 获取 Bilibili Cookie 信息

#### 方法1：通过浏览器开发者工具
1. **登录Bilibili**：在浏览器中访问 [bilibili.com](https://www.bilibili.com) 并登录
2. **打开开发者工具**：按 `F12` 或右键选择"检查"
3. **查找Cookie**：
   - 点击 `Application` 标签页（Chrome）或 `Storage` 标签页（Firefox）
   - 在左侧找到 `Cookies` > `https://www.bilibili.com`
   - 找到以下三个Cookie值：

| Cookie名称 | 说明 | 必需性 |
|-----------|------|--------|
| `SESSDATA` | 会话数据，最重要的认证信息 | ✅ 必需 |
| `bili_jct` | CSRF令牌，用于防护 | ✅ 必需 |
| `buvid3` | 浏览器唯一标识 | 🔶 推荐 |

#### 方法2：通过网络请求查看
1. 登录Bilibili后，按 `F12` 打开开发者工具
2. 切换到 `Network` 标签页
3. 刷新页面或进行任何操作
4. 查看任意请求的 `Request Headers` 中的 `Cookie` 字段
5. 从中提取需要的Cookie值

### 配置示例：
```bash
BILIBILI_SESSDATA=abc123def456ghi789jkl
BILIBILI_BILI_JCT=xyz789uvw456rst123
BILIBILI_BUVID3=ABCD-EFGH-IJKL-MNOP-123456789
```

### ⚠️ 重要注意事项
- **Cookie有效期**：Bilibili的Cookie会过期，通常需要定期更新
- **安全性**：不要在公共场所或不安全的环境中暴露这些Cookie
- **隐私**：这些Cookie可以访问你的个人Bilibili数据，请妥善保管

## 📁 配置文件格式

### 选项1：使用 `config` 文件（推荐）
创建名为 `config` 的文件（无扩展名）：
```bash
# Steam配置
STEAM_API_KEY=你的Steam_API_Key
STEAM_USER_ID=你的Steam用户ID

# YouTube配置  
YOUTUBE_API_KEY=你的YouTube_API_Key
YOUTUBE_ACCESS_TOKEN=你的OAuth2访问令牌（可选）

# Bilibili配置
BILIBILI_SESSDATA=你的SESSDATA值
BILIBILI_BILI_JCT=你的bili_jct值
BILIBILI_BUVID3=你的buvid3值
```

### 选项2：使用 `.env` 文件
创建名为 `.env` 的文件：
```bash
STEAM_API_KEY=你的Steam_API_Key
STEAM_USER_ID=你的Steam用户ID
YOUTUBE_API_KEY=你的YouTube_API_Key
BILIBILI_SESSDATA=你的SESSDATA值
BILIBILI_BILI_JCT=你的bili_jct值
BILIBILI_BUVID3=你的buvid3值
```

### 选项3：系统环境变量
在你的shell配置文件中（如 `.bashrc`, `.zshrc`）添加：
```bash
export STEAM_API_KEY="你的Steam_API_Key"
export STEAM_USER_ID="你的Steam用户ID"
export YOUTUBE_API_KEY="你的YouTube_API_Key"
export BILIBILI_SESSDATA="你的SESSDATA值"
export BILIBILI_BILI_JCT="你的bili_jct值"
export BILIBILI_BUVID3="你的buvid3值"
```

## 🧪 测试配置

配置完成后，可以使用以下MCP工具测试：

```python
# 测试Steam配置
test_steam_credentials()

# 测试YouTube配置  
test_youtube_credentials()

# 测试Bilibili配置
test_bilibili_credentials()

# 查看整体状态
get_personalization_status()
```

## 🔒 安全建议

1. **不要提交配置文件到Git**：确保 `config` 和 `.env` 文件在 `.gitignore` 中
2. **定期更新Cookie**：Bilibili的Cookie会过期，建议定期检查和更新
3. **使用环境变量**：在生产环境中使用系统环境变量而不是文件
4. **权限控制**：确保配置文件只有你有读取权限

## 🆘 常见问题

### Q: Bilibili Cookie多久过期？
A: 通常几个月到一年，具体取决于Bilibili的策略。如果API调用失败，首先检查Cookie是否过期。

### Q: Steam API有调用限制吗？
A: 是的，Steam API有速率限制。建议不要频繁调用，合理使用缓存。

### Q: YouTube API配额不够用怎么办？
A: YouTube API有每日配额限制。可以申请增加配额或优化API调用频率。

### Q: 如何知道配置是否正确？
A: 运行测试工具，或者调用 `get_personalization_status()` 查看各平台状态。

## 📞 获取帮助

如果遇到配置问题：
1. 检查配置文件格式是否正确
2. 确认API密钥和Cookie是否有效
3. 查看MCP服务器日志输出
4. 使用测试工具验证每个平台的配置
