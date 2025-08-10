#!/usr/bin/env python3
"""
测试商家认证功能
"""

import requests
import json
import base64

# 配置
BASE_URL = "http://localhost:5000"
REGISTER_URL = f"{BASE_URL}/api/web/auth/register"
LOGIN_URL = f"{BASE_URL}/api/web/auth/login"
VALIDATE_URL = f"{BASE_URL}/api/web/auth/validate"
PROFILE_URL = f"{BASE_URL}/api/web/auth/profile"

def test_merchant_register():
    """测试商家注册"""
    print("=== 测试商家注册 ===")
    
    # 测试数据
    test_phone = "13800138000"
    test_password = "123456"
    
    data = {
        "phone": test_phone,
        "password": test_password
    }
    
    try:
        response = requests.post(REGISTER_URL, json=data)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 200:
            print("✅ 注册成功")
            return result['data']
        else:
            print(f"❌ 注册失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_merchant_login(phone, password):
    """测试商家登录"""
    print("\n=== 测试商家登录 ===")
    
    data = {
        "phone": phone,
        "password": password
    }
    
    try:
        response = requests.post(LOGIN_URL, json=data)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 200:
            print("✅ 登录成功")
            return result['data']
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_token_validation(token):
    """测试token验证"""
    print("\n=== 测试Token验证 ===")
    
    try:
        response = requests.get(f"{VALIDATE_URL}?token={token}")
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 200 and result.get('data', {}).get('valid'):
            print("✅ Token验证成功")
            return True
        else:
            print("❌ Token验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_profile(token):
    """测试获取商家信息"""
    print("\n=== 测试获取商家信息 ===")
    
    try:
        response = requests.get(f"{PROFILE_URL}?token={token}")
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('code') == 200:
            print("✅ 获取商家信息成功")
            return result['data']
        else:
            print(f"❌ 获取商家信息失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def main():
    """主测试流程"""
    print("开始测试商家认证功能...")
    
    # 1. 测试注册
    register_result = test_merchant_register()
    if not register_result:
        print("注册失败，跳过后续测试")
        return
    
    # 2. 测试登录
    login_result = test_merchant_login("13800138000", "123456")
    if not login_result:
        print("登录失败，跳过后续测试")
        return
    
    token = login_result.get('token')
    if not token:
        print("未获取到token，跳过后续测试")
        return
    
    # 3. 测试token验证
    test_token_validation(token)
    
    # 4. 测试获取商家信息
    test_get_profile(token)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
