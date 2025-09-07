#!/usr/bin/env python3
"""
YouTube OAuth2 Helper Script
帮助获取 YouTube API 的 OAuth2 access token
"""

import json
import os
import webbrowser
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen, Request
import http.server
import socketserver
import threading
from urllib.parse import urlparse

# YouTube API OAuth2 配置
YOUTUBE_OAUTH_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"

def get_device_code(client_id: str) -> dict:
    """获取设备代码和用户代码"""
    data = {
        'client_id': client_id,
        'scope': YOUTUBE_OAUTH_SCOPE
    }
    
    post_data = urlencode(data).encode('utf-8')
    request = Request(DEVICE_CODE_URL, data=post_data)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"❌ 获取设备代码时出错: {e}")
        return {}

def poll_for_token(client_id: str, client_secret: str, device_code: str, interval: int = 5) -> dict:
    """轮询获取 access token"""
    import time
    
    data = {
        'client_id': client_id,
        'device_code': device_code,
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
    }
    
    # 只有在有 client_secret 时才添加
    if client_secret:
        data['client_secret'] = client_secret
    
    post_data = urlencode(data).encode('utf-8')
    
    print("⏳ 等待用户授权...")
    print("💡 请在浏览器中完成授权，然后回到这里等待...")
    
    max_attempts = 60  # 最多等待 5 分钟
    attempts = 0
    
    while attempts < max_attempts:
        try:
            request = Request(TOKEN_URL, data=post_data)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            with urlopen(request) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'access_token' in result:
                    return result
                elif result.get('error') == 'authorization_pending':
                    print("⏳ 仍在等待授权...")
                    time.sleep(interval)
                    attempts += 1
                elif result.get('error') == 'slow_down':
                    print("⏳ 请求过于频繁，增加等待时间...")
                    interval += 1
                    time.sleep(interval)
                    attempts += 1
                else:
                    print(f"❌ 授权失败: {result}")
                    return {}
                    
        except Exception as e:
            print(f"❌ 轮询时出错: {e}")
            time.sleep(interval)
            attempts += 1
    
    print("❌ 授权超时，请重试")
    return {}

def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """使用 refresh token 获取新的 access token"""
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    post_data = urlencode(data).encode('utf-8')
    request = Request(TOKEN_URL, data=post_data)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        with urlopen(request) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        print(f"❌ 刷新 token 时出错: {e}")
        return {}

def save_tokens(tokens: dict):
    """保存 tokens 到文件"""
    tokens_file = "youtube_tokens.json"
    with open(tokens_file, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"✅ Tokens 已保存到 {tokens_file}")

def load_tokens() -> dict:
    """从文件加载 tokens"""
    tokens_file = "youtube_tokens.json"
    if os.path.exists(tokens_file):
        with open(tokens_file, 'r') as f:
            return json.load(f)
    return {}

def main():
    print("🎥 YouTube OAuth2 助手")
    print("=" * 50)
    
    while True:
        print("\n请选择操作：")
        print("1. 获取新的 access token")
        print("2. 刷新现有的 access token")
        print("3. 查看保存的 tokens")
        print("4. 退出")
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            # 获取新的 access token (设备授权流程)
            print("\n📝 获取新的 Access Token (设备授权流程)")
            print("-" * 50)
            
            client_id = input("请输入你的 Client ID: ").strip()
            if not client_id:
                print("❌ Client ID 不能为空")
                continue
                
            client_secret = input("请输入你的 Client Secret (如果是设备类型可能为空，直接按 Enter): ").strip()
            if not client_secret:
                print("⚠️  Client Secret 为空，将尝试设备授权流程...")
                client_secret = None
            
            # 获取设备代码
            print("\n🔄 正在获取设备代码...")
            device_info = get_device_code(client_id)
            
            if not device_info or 'device_code' not in device_info:
                print("❌ 获取设备代码失败")
                if device_info:
                    print(f"错误信息: {device_info}")
                continue
            
            # 显示用户代码和验证 URL
            print(f"\n🔗 请在浏览器中打开以下 URL：")
            print(f"📱 {device_info['verification_url']}")
            print(f"\n🔑 然后输入以下代码：")
            print(f"📋 {device_info['user_code']}")
            print(f"\n⏰ 代码有效期：{device_info.get('expires_in', 1800)} 秒")
            
            # 尝试自动打开浏览器
            try:
                webbrowser.open(device_info['verification_url'])
                print("✅ 已尝试自动打开浏览器")
            except:
                print("⚠️  无法自动打开浏览器，请手动复制上面的 URL")
            
            input("\n按 Enter 键开始等待授权...")
            
            # 轮询获取 token
            tokens = poll_for_token(
                client_id, 
                client_secret, 
                device_info['device_code'], 
                device_info.get('interval', 5)
            )
            
            if tokens and 'access_token' in tokens:
                print("✅ 成功获取 access token!")
                print(f"Access Token: {tokens['access_token']}")
                if 'refresh_token' in tokens:
                    print(f"Refresh Token: {tokens['refresh_token']}")
                
                # 保存 client 信息和 tokens
                full_tokens = {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    **tokens
                }
                save_tokens(full_tokens)
                
                print(f"\n🔧 请将以下内容添加到你的环境变量或 Cursor 配置中：")
                print(f"YOUTUBE_ACCESS_TOKEN={tokens['access_token']}")
                
            else:
                print("❌ 获取 access token 失败")
                if tokens:
                    print(f"错误信息: {tokens}")
        
        elif choice == "2":
            # 刷新 access token
            print("\n🔄 刷新 Access Token")
            print("-" * 30)
            
            tokens = load_tokens()
            if not tokens:
                print("❌ 没有找到保存的 tokens，请先获取新的 access token")
                continue
            
            if 'refresh_token' not in tokens:
                print("❌ 没有找到 refresh token，请重新获取 access token")
                continue
            
            client_id = tokens.get('client_id')
            client_secret = tokens.get('client_secret')
            refresh_token = tokens.get('refresh_token')
            
            if not all([client_id, client_secret, refresh_token]):
                print("❌ 缺少必要的认证信息，请重新获取 access token")
                continue
            
            print("🔄 正在刷新 access token...")
            new_tokens = refresh_access_token(client_id, client_secret, refresh_token)
            
            if new_tokens and 'access_token' in new_tokens:
                print("✅ 成功刷新 access token!")
                print(f"新的 Access Token: {new_tokens['access_token']}")
                
                # 更新保存的 tokens
                tokens.update(new_tokens)
                save_tokens(tokens)
                
                print(f"\n🔧 请更新你的环境变量：")
                print(f"YOUTUBE_ACCESS_TOKEN={new_tokens['access_token']}")
            else:
                print("❌ 刷新 access token 失败")
                if new_tokens:
                    print(f"错误信息: {new_tokens}")
        
        elif choice == "3":
            # 查看保存的 tokens
            print("\n👀 保存的 Tokens")
            print("-" * 30)
            
            tokens = load_tokens()
            if tokens:
                print(f"Client ID: {tokens.get('client_id', 'N/A')}")
                print(f"Access Token: {tokens.get('access_token', 'N/A')}")
                print(f"Refresh Token: {'存在' if tokens.get('refresh_token') else '不存在'}")
                print(f"Token Type: {tokens.get('token_type', 'N/A')}")
                if 'expires_in' in tokens:
                    print(f"过期时间: {tokens['expires_in']} 秒")
            else:
                print("❌ 没有找到保存的 tokens")
        
        elif choice == "4":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效的选择，请输入 1-4")

if __name__ == "__main__":
    main()