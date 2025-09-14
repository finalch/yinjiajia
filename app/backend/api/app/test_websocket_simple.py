#!/usr/bin/env python3
"""
简单的WebSocket测试脚本
"""
import asyncio
import websockets
import json

async def test_websocket():
    """测试WebSocket连接"""
    uri = "ws://localhost:8003?authorization=Bearer%20test_token"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket连接成功!")
            
            # 发送测试消息
            test_message = {
                "type": "user_join",
                "data": {
                    "user_id": 1
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print("发送测试消息:", test_message)
            
            # 接收响应
            response = await websocket.recv()
            print("收到响应:", response)
            
    except Exception as e:
        print(f"WebSocket连接失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
