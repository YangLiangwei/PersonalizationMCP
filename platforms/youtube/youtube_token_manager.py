"""
YouTube Token Manager
自动管理YouTube OAuth2令牌的刷新和更新
"""

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import datetime, timedelta
from typing import Optional, Dict


class YouTubeTokenManager:
    """YouTube令牌管理器，自动处理令牌刷新"""
    
    def __init__(self, tokens_file: str = "youtube_tokens.json"):
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(tokens_file):
            # 获取当前模块所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.tokens_file = os.path.join(current_dir, tokens_file)
        else:
            self.tokens_file = tokens_file
        self._tokens = None
        self._last_refresh_time = 0
        
    def _load_tokens(self) -> Optional[Dict]:
        """从文件加载令牌"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r') as f:
                    tokens = json.load(f)
                    return tokens
        except Exception as e:
            print(f"❌ 加载令牌文件失败: {e}")
        return None
    
    def _save_tokens(self, tokens: Dict) -> bool:
        """保存令牌到文件"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ 保存令牌文件失败: {e}")
            return False
    
    def _refresh_access_token(self) -> Optional[Dict]:
        """使用refresh token获取新的access token"""
        tokens = self._load_tokens()
        if not tokens:
            return None
            
        required_fields = ['client_id', 'client_secret', 'refresh_token']
        if not all(field in tokens for field in required_fields):
            print("❌ 缺少必要的认证信息")
            return None
        
        data = {
            'client_id': tokens['client_id'],
            'client_secret': tokens['client_secret'],
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        post_data = urlencode(data).encode('utf-8')
        request = Request('https://oauth2.googleapis.com/token', data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        try:
            with urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'access_token' in result:
                    # 更新令牌文件
                    tokens.update(result)
                    # 添加刷新时间戳
                    tokens['refreshed_at'] = int(time.time())
                    
                    if self._save_tokens(tokens):
                        print(f"✅ 成功刷新YouTube访问令牌: {result['access_token'][:30]}...")
                        self._tokens = tokens
                        self._last_refresh_time = time.time()
                        
                        # 更新环境变量
                        os.environ['YOUTUBE_ACCESS_TOKEN'] = result['access_token']
                        
                        # 注意：不再需要同步到MCP配置文件，因为系统会自动从令牌文件读取
                        
                        return tokens
                    else:
                        print("❌ 保存新令牌失败")
                else:
                    print(f"❌ 刷新令牌失败: {result}")
                    
        except Exception as e:
            print(f"❌ 刷新令牌时出错: {e}")
            
        return None
    
    def get_valid_access_token(self) -> Optional[str]:
        """获取有效的访问令牌，如果需要则自动刷新"""
        # 加载当前令牌
        current_tokens = self._load_tokens()
        if not current_tokens:
            print("❌ 没有找到令牌文件，请检查 youtube_tokens.json 是否存在")
            return None
        
        # 检查必要字段
        if 'access_token' not in current_tokens:
            print("❌ 令牌文件中缺少 access_token 字段")
            return None
        
        # 检查令牌是否需要刷新
        expires_in = current_tokens.get('expires_in', 0)
        refreshed_at = current_tokens.get('refreshed_at', 0)
        current_time = int(time.time())
        
        # 如果令牌在5分钟内过期，或者已经过期，则刷新
        time_since_refresh = current_time - refreshed_at
        needs_refresh = (
            expires_in <= 300 or  # 5分钟内过期
            time_since_refresh >= expires_in or  # 已经过期
            time_since_refresh >= 3300 or  # 超过55分钟（保险起见）
            refreshed_at == 0  # 从未刷新过
        )
        
        if needs_refresh:
            print(f"🔄 访问令牌需要刷新 (已使用 {time_since_refresh} 秒，有效期 {expires_in} 秒)")
            refreshed_tokens = self._refresh_access_token()
            if refreshed_tokens:
                print("✅ 令牌刷新成功")
                return refreshed_tokens['access_token']
            else:
                print("❌ 自动刷新失败，尝试使用现有令牌")
                # 即使刷新失败，也尝试使用现有令牌
                access_token = current_tokens.get('access_token')
                if access_token:
                    os.environ['YOUTUBE_ACCESS_TOKEN'] = access_token
                return access_token
        else:
            remaining_time = expires_in - time_since_refresh
            print(f"✅ 当前令牌仍有效，剩余 {remaining_time} 秒")
            # 确保环境变量是最新的
            access_token = current_tokens['access_token']
            os.environ['YOUTUBE_ACCESS_TOKEN'] = access_token
            return access_token
    
    def force_refresh(self) -> Optional[str]:
        """强制刷新令牌"""
        print("🔄 强制刷新YouTube访问令牌...")
        refreshed_tokens = self._refresh_access_token()
        if refreshed_tokens:
            return refreshed_tokens['access_token']
        return None
    
    def get_token_status(self) -> Dict:
        """获取令牌状态信息"""
        tokens = self._load_tokens()
        if not tokens:
            return {"error": "没有找到令牌文件"}
        
        refreshed_at = tokens.get('refreshed_at', 0)
        expires_in = tokens.get('expires_in', 0)
        current_time = int(time.time())
        time_since_refresh = current_time - refreshed_at
        remaining_time = max(0, expires_in - time_since_refresh)
        
        return {
            "access_token": tokens.get('access_token', 'N/A')[:30] + "..." if tokens.get('access_token') else 'N/A',
            "has_refresh_token": bool(tokens.get('refresh_token')),
            "expires_in": expires_in,
            "refreshed_at": datetime.fromtimestamp(refreshed_at).strftime('%Y-%m-%d %H:%M:%S') if refreshed_at else 'N/A',
            "time_since_refresh": time_since_refresh,
            "remaining_time": remaining_time,
            "needs_refresh": remaining_time <= 300,
            "status": "🟢 有效" if remaining_time > 300 else "🟡 即将过期" if remaining_time > 0 else "🔴 已过期"
        }
    
    def _sync_to_mcp_config(self, access_token: str) -> bool:
        """同步新的access_token到MCP配置文件"""
        try:
            import json
            mcp_config_path = os.path.expanduser("~/.cursor/mcp.json")
            
            if not os.path.exists(mcp_config_path):
                print(f"⚠️ MCP配置文件不存在: {mcp_config_path}")
                return False
            
            # 读取现有配置
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            
            # 更新YouTube access token
            if 'mcpServers' in config and 'personalization-mcp' in config['mcpServers']:
                if 'env' in config['mcpServers']['personalization-mcp']:
                    config['mcpServers']['personalization-mcp']['env']['YOUTUBE_ACCESS_TOKEN'] = access_token
                    
                    # 保存更新后的配置
                    with open(mcp_config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    
                    print(f"✅ 已同步新令牌到MCP配置文件")
                    return True
            
            print("⚠️ MCP配置文件格式不符合预期")
            return False
            
        except Exception as e:
            print(f"⚠️ 同步到MCP配置文件失败: {e}")
            return False


# 全局令牌管理器实例
_token_manager = None

def get_token_manager() -> YouTubeTokenManager:
    """获取全局令牌管理器实例"""
    global _token_manager
    if _token_manager is None:
        _token_manager = YouTubeTokenManager()
    return _token_manager
