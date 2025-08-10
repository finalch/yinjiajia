#!/bin/bash

echo "=== 启动商家认证系统 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "app/backend/app.py" ]; then
    echo "❌ 请在项目根目录执行此脚本"
    exit 1
fi

echo "✅ 环境检查通过"

# 检查依赖
echo "检查Python依赖..."
cd app/backend
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 文件不存在"
    exit 1
fi

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 启动后端服务
echo "启动后端服务..."
echo "后端服务将在 http://localhost:5000 启动"
echo "按 Ctrl+C 停止服务"

python3 app.py
