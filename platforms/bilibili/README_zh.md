# Bilibili 平台集成

本模块为 PersonalizationMCP 服务器提供 Bilibili API 集成。

## 功能特性

- 👤 获取用户个人资料信息和统计数据
- 🔍 搜索视频并获取详细视频信息
- 📺 访问个人数据（观看历史、收藏、点赞视频、投币历史）
- 👥 获取关注列表和用户上传的视频
- 📚 浏览"稍后再看"列表和个人收藏

## 配置

必需的环境变量：
- `BILIBILI_SESSDATA`: 会话数据 Cookie
- `BILIBILI_BILI_JCT`: CSRF 令牌 Cookie

可选：
- `BILIBILI_BUVID3`: 浏览器唯一标识符

## 文件

- `bilibili_mcp.py`: 主要的 Bilibili MCP 集成模块
- `README.md`: 英文文档
- `README_zh.md`: 本中文文档

## Cookie 设置

要访问 Bilibili 数据，你需要从浏览器中提取 Cookie：

1. **登录 Bilibili**: 访问 [bilibili.com](https://www.bilibili.com) 并登录
2. **打开开发者工具**: 按 `F12` 或右键选择"检查"
3. **查找 Cookie**:
   - 点击 `Application` 标签（Chrome）或 `Storage` 标签（Firefox）
   - 导航到 `Cookies` > `https://www.bilibili.com`
   - 找到这些 Cookie 值：

| Cookie 名称 | 描述 | 必需性 |
|-------------|------|--------|
| `SESSDATA` | 会话数据，最重要的认证信息 | ✅ 必需 |
| `bili_jct` | CSRF 令牌，用于保护 | ✅ 必需 |
| `buvid3` | 浏览器唯一标识符 | 🔶 推荐 |

## 重要提示

- ⚠️ Bilibili Cookie 会定期过期，需要更新
- 🔒 保护这些 Cookie 的安全，因为它们提供对你个人 Bilibili 数据的访问
- 🚫 不要公开分享这些 Cookie
