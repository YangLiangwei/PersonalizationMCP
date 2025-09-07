#!/usr/bin/env python3
"""
YouTube Token Auto Refresh Script
自动刷新YouTube访问令牌的脚本
"""

import json
import os
import time
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import datetime, timedelta

def load_tokens():
    """加载令牌文件"""
    try:
        with open('youtube_tokens.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载令牌文件失败: {e}")
        return None

def save_tokens(tokens):
    """保存令牌到文件"""
    try:
        with open('youtube_tokens.json', 'w') as f:
            json.dump(tokens, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存令牌文件失败: {e}")
        return False

def refresh_access_token(client_id, client_secret, refresh_token):
    """使用refresh token获取新的access token"""
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    post_data = urlencode(data).encode('utf-8')
    request = Request('https://oauth2.googleapis.com/token', data=post_data)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"❌ 刷新令牌时出错: {e}")
        return None

def get_fresh_access_token():
    """获取有效的访问令牌（如果需要则自动刷新）"""
    tokens = load_tokens()
    if not tokens:
        return None
    
    # 检查是否需要刷新（提前5分钟刷新）
    expires_in = tokens.get('expires_in', 0)
    if expires_in > 300:  # 还有5分钟以上有效期
        print(f"✅ 当前令牌仍有效，剩余 {expires_in} 秒")
        return tokens['access_token']
    
    print("🔄 访问令牌即将过期，正在刷新...")
    
    # 刷新令牌
    new_tokens = refresh_access_token(
        tokens['client_id'],
        tokens['client_secret'],
        tokens['refresh_token']
    )
    
    if new_tokens and 'access_token' in new_tokens:
        # 更新令牌文件
        tokens.update(new_tokens)
        if save_tokens(tokens):
            print(f"✅ 成功刷新访问令牌: {new_tokens['access_token'][:30]}...")
            return new_tokens['access_token']
    
    print("❌ 刷新访问令牌失败")
    return None

def set_environment_variable(access_token):
    """设置环境变量（仅在当前进程中有效）"""
    os.environ['YOUTUBE_ACCESS_TOKEN'] = access_token
    print(f"✅ 已设置环境变量 YOUTUBE_ACCESS_TOKEN")

def main():
    print("🎥 YouTube 令牌自动刷新工具")
    print("=" * 50)
    
    while True:
        print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取有效的访问令牌
        access_token = get_fresh_access_token()
        
        if access_token:
            # 设置环境变量
            set_environment_variable(access_token)
            
            print("📋 使用方法:")
            print(f"   在代码中使用: os.getenv('YOUTUBE_ACCESS_TOKEN')")
            print(f"   或直接使用令牌: {access_token[:30]}...")
            
            # 显示下次刷新时间
            tokens = load_tokens()
            if tokens:
                expires_in = tokens.get('expires_in', 3600)
                next_refresh = datetime.now() + timedelta(seconds=max(expires_in - 300, 60))
                print(f"   下次刷新时间: {next_refresh.strftime('%H:%M:%S')}")
        
        print("\n选择操作:")
        print("1. 立即刷新令牌")
        print("2. 查看当前令牌状态") 
        print("3. 导出环境变量命令")
        print("4. 退出")
        
        try:
            choice = input("\n请选择 (1-4，或直接按Enter等待自动刷新): ").strip()
            
            if choice == "1":
                print("🔄 手动刷新令牌...")
                tokens = load_tokens()
                if tokens:
                    tokens['expires_in'] = 0  # 强制刷新
                    save_tokens(tokens)
                continue
                
            elif choice == "2":
                tokens = load_tokens()
                if tokens:
                    print(f"\n📊 当前令牌状态:")
                    print(f"   Access Token: {tokens['access_token'][:30]}...")
                    print(f"   剩余时间: {tokens.get('expires_in', 0)} 秒")
                    print(f"   Refresh Token: 存在 ✅")
                continue
                
            elif choice == "3":
                access_token = get_fresh_access_token()
                if access_token:
                    print(f"\n📋 环境变量设置命令:")
                    print(f"export YOUTUBE_ACCESS_TOKEN='{access_token}'")
                    print(f"\n或在 .bashrc/.zshrc 中添加:")
                    print(f"export YOUTUBE_ACCESS_TOKEN='{access_token}'")
                continue
                
            elif choice == "4":
                print("👋 再见！")
                break
                
            elif choice == "":
                # 等待并自动刷新
                tokens = load_tokens()
                if tokens:
                    wait_time = max(tokens.get('expires_in', 3600) - 300, 60)
                    print(f"⏳ 等待 {wait_time} 秒后自动刷新...")
                    time.sleep(min(wait_time, 300))  # 最多等待5分钟
                continue
                
            else:
                print("❌ 无效选择")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出")
            break
        except Exception as e:
            print(f"❌ 出错: {e}")

if __name__ == "__main__":
    main()
