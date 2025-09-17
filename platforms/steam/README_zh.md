# Steam 平台集成

本模块为 PersonalizationMCP 服务器提供 Steam API 集成。

## 功能特性

- 🎮 获取你的游戏库，包含详细统计和游戏时长
- 📊 查看最近的游戏活动和当前正在玩的游戏
- 🏆 获取详细的游戏信息和成就
- 👥 与好友比较游戏并获取推荐
- 📈 分析游戏习惯和偏好

## 配置

必需的环境变量：
- `STEAM_API_KEY`: 你的 Steam Web API 密钥
- `STEAM_USER_ID`: 你的 Steam 用户 ID

## 文件

- `steam_mcp.py`: 主要的 Steam MCP 集成模块
- `README.md`: 英文文档
- `README_zh.md`: 本中文文档

## API 密钥设置

1. 访问 [Steam Web API Key 页面](https://steamcommunity.com/dev/apikey)
2. 登录你的 Steam 账户
3. 输入域名（开发用途可以使用 `localhost`）
4. 复制生成的 API 密钥

## Steam 用户 ID

1. 前往你的 Steam 个人资料页面
2. 查看 URL，例如：`https://steamcommunity.com/profiles/76561198123456789/`
3. 数字 `76561198123456789` 就是你的 Steam ID
