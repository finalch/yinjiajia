#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试趋势分析接口
"""

import requests
import json
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:5000"
MERCHANT_ID = 1  # 假设的商家ID

def test_trends_api():
    """测试趋势分析接口"""
    
    print("=== 测试趋势分析接口 ===\n")
    
    # 测试不同周期的趋势数据
    periods = ['7d', '30d', '90d']
    
    for period in periods:
        print(f"测试 {period} 趋势数据:")
        
        url = f"{BASE_URL}/api/web/analytics/trends"
        params = {'period': period}
        
        try:
            response = requests.get(url, params=params)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"错误响应: {response.text}")
                
        except Exception as e:
            print(f"请求失败: {e}")
        
        print("-" * 50)
    
    # 测试趋势对比接口
    print("\n测试趋势对比接口:")
    url = f"{BASE_URL}/api/web/analytics/trends/compare"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

def test_with_auth():
    """测试需要认证的接口"""
    print("\n=== 测试需要认证的接口 ===\n")
    
    # 这里需要先登录获取token，然后设置认证头
    # 由于没有完整的认证流程，这里只是示例
    
    headers = {
        'Authorization': 'Bearer YOUR_TOKEN_HERE'  # 需要替换为实际的token
    }
    
    url = f"{BASE_URL}/api/web/analytics/trends"
    params = {'period': '7d'}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        print(f"认证请求状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    print("趋势分析接口测试")
    print("=" * 50)
    
    # 测试基础接口（可能返回认证错误）
    test_trends_api()
    
    # 测试需要认证的接口
    test_with_auth()
    
    print("\n测试完成！")
