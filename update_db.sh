#!/bin/bash

# 数据库更新脚本
echo "开始更新数据库结构..."

# 读取数据库配置
DB_HOST="localhost"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="123456"
DB_NAME="ecommerce_db"

# 执行数据库更新脚本
mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PASSWORD < scripts/sql/update_database_structure.sql

echo "数据库结构更新完成！" 