# YouTube 平台集成

本模块为 PersonalHub 服务器提供 YouTube API 集成。

## 功能特性

- 🔍 搜索 YouTube 视频并获取详细视频信息
- 📺 获取频道信息和热门视频
- 👤 通过 OAuth2 访问个人数据（订阅、观看历史、播放列表、点赞视频）
- 🎯 基于观看历史获取个性化推荐
- 🔄 **自动令牌刷新** - 智能检测并自动刷新过期的 OAuth2 令牌
- 🛡️ **智能令牌管理** - 优先使用令牌文件，无需手动维护 MCP 配置

## 配置

### 必需的环境变量
- `YOUTUBE_API_KEY`: 你的 YouTube Data API v3 密钥

### OAuth2 配置（用于访问个人数据）
**推荐方式**: 使用令牌文件自动管理
- 令牌文件: `youtube_tokens.json` (自动生成和维护)
- 系统会自动检测令牌过期并刷新

**备用方式**: 环境变量
- `YOUTUBE_ACCESS_TOKEN`: OAuth2 访问令牌 (可选，作为备用)

### 智能令牌优先级
1. 显式传入的 access_token 参数
2. **令牌文件中的自动刷新令牌** (推荐)
3. 环境变量中的令牌 (备用)

## 文件

- `youtube_mcp.py`: 主要的 YouTube MCP 集成模块
- `youtube_oauth_helper.py`: OAuth2 认证助手
- `youtube_token_manager.py`: 令牌管理工具
- `auto_refresh_youtube_token.py`: 自动令牌刷新脚本
- `youtube_tokens.json`: 令牌存储 (自动生成)
- `README.md`: 英文文档
- `README_zh.md`: 本中文文档

## API 设置

### 步骤 1: 创建 Google Cloud 项目并获取 API 密钥

1. **访问 Google Cloud Console**
   - 打开 [Google Cloud Console](https://console.cloud.google.com/)
   - 使用你的 Google 账户登录

2. **创建新项目**
   - 点击顶部的项目选择器
   - 点击"新建项目"
   - 项目名称：输入 `PersonalHub` 或其他你喜欢的名称
   - 点击"创建"

3. **启用 YouTube Data API v3**
   - 在左侧菜单中，点击"API和服务" → "库"
   - 搜索 `YouTube Data API v3`
   - 点击搜索结果中的"YouTube Data API v3"
   - 点击"启用"按钮

4. **创建 API 密钥**
   - 在左侧菜单中，点击"API和服务" → "凭据"
   - 点击"+ 创建凭据" → "API密钥"
   - 复制生成的 API 密钥（类似：`AIzaSyBOROoarHUQW4gVblNUprxFeovH25qUfuw`）
   - （可选）点击"限制密钥"来设置使用限制

### 步骤 2: 设置 OAuth2（用于访问个人数据）

**为什么需要 OAuth2？**
- API 密钥只能访问公开数据（搜索视频、获取视频信息等）
- 访问个人数据（点赞视频、订阅列表、播放列表）需要 OAuth2 认证

**详细设置步骤：**

#### 1. 配置 OAuth 同意屏幕
- 在"API和服务" → "凭据"页面
- 点击"配置同意屏幕"
- 用户类型选择"外部"（个人使用）
- 点击"创建"

#### 2. 填写应用信息
- 应用名称：`PersonalHub`
- 用户支持电子邮件：选择你的邮箱
- 开发者联系信息：输入你的邮箱
- 点击"保存并继续"

#### 3. 添加范围（可选但推荐）
- 点击"添加或移除范围"
- 搜索并添加：`https://www.googleapis.com/auth/youtube.readonly`
- 点击"更新" → "保存并继续"

#### 4. 添加测试用户
- 点击"+ 添加用户"
- 输入你的 Google 邮箱地址
- 点击"保存并继续"

#### 5. 创建 OAuth 客户端 ID
- 回到"凭据"页面
- 点击"+ 创建凭据" → "OAuth客户端ID"
- 应用类型选择："TV and Limited Input device"
- 名称：`PersonalHub Server`
- 点击"创建"

#### 6. 获取凭据信息
- 创建完成后会显示弹窗，包含：
  - **客户端ID**：`402070639637-xxxxxx.apps.googleusercontent.com`
  - **客户端密钥**：`GOCSPX-xxxxxx`
- 点击"下载JSON"保存凭据文件
- 或者手动复制 Client ID 和 Client Secret

### 步骤 3: OAuth 认证

**方法A: 使用 MCP 工具（推荐）**

在 PersonalHub 运行后，使用内置的 MCP 工具：

1. **开始 OAuth 设置**
   ```
   setup_youtube_oauth(client_id, client_secret)
   ```

2. **完成授权**
   - 工具会提供验证 URL 和代码
   - 在任何设备上访问 URL 并输入代码
   - 完成 Google 授权

3. **完成设置**
   ```
   complete_youtube_oauth(client_id, client_secret, device_code)
   ```

**方法B: 使用 Python 脚本（备选）**
```bash
python youtube_oauth_helper.py
```

### 认证流程
1. 系统显示设备代码和验证 URL
2. 在任何设备上打开浏览器访问 URL
3. 输入设备代码
4. 使用 Google 账户登录并授权 PersonalHub
5. 令牌自动保存并管理

### 重要提示
- OAuth2 令牌自动管理，首次认证后无需手动操作
- 系统自动处理令牌刷新
- 如果令牌过期，会提示重新认证
- 保持凭据文件安全，不要公开分享

### 故障排除
- 如果遇到"OAuth app not verified"警告，点击"Advanced" → "Go to PersonalHub (unsafe)"
- 确保邮箱已添加为 OAuth 同意屏幕的测试用户
- 确保 YouTube Data API v3 已在 Google Cloud 项目中启用
