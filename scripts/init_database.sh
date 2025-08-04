#!/bin/bash

# 数据库初始化脚本
echo "开始初始化数据库..."

# 设置数据库连接参数
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD=""
DB_NAME="ecommerce_db"

# 检查MySQL是否运行
if ! mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" --silent; then
    echo "错误: MySQL服务未运行或连接失败"
    exit 1
fi

# 执行初始化脚本
echo "执行数据库初始化脚本..."
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" < scripts/sql/init_complete_database.sql

if [ $? -eq 0 ]; then
    echo "✅ 数据库初始化成功！"
    echo "数据库名称: $DB_NAME"
    echo "地址表已创建并包含测试数据"
else
    echo "❌ 数据库初始化失败！"
    exit 1
fi 