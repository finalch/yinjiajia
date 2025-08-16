# 电商平台API文档

## 概述

本文档描述了电商平台的后端API接口，包括商家端Web API和用户端App API。

## 基础信息

- **基础URL**: `http://localhost:5000`
- **API版本**: v1.0
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

## 商家端Web API

### 1. 商品分类管理

#### 1.1 获取分类列表
```http
GET /api/web/groups?merchant_id=1&status=active&page=1&per_page=10
```

**参数说明:**
- `merchant_id`: 商家ID（必填）
- `status`: 状态筛选（active/inactive）
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认10）

**响应示例:**
```json
{
  "code": 200,
  "message": "获取分类列表成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "手机数码",
        "description": "智能手机、平板电脑、数码配件等",
        "icon_url": "https://example.com/icon.jpg",
        "sort_order": 1,
        "status": "active",
        "merchant_id": 1,
        "product_count": 2,
        "created_at": "2024-01-01 10:00:00",
        "updated_at": "2024-01-01 10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 8,
      "pages": 1
    }
  }
}
```

#### 1.2 创建分类
```http
POST /api/web/groups
Content-Type: application/json

{
  "name": "新分类",
  "description": "分类描述",
  "icon_url": "https://example.com/icon.jpg",
  "sort_order": 1,
  "status": "active",
  "merchant_id": 1
}
```

#### 1.3 更新分类
```http
PUT /api/web/groups/{id}
Content-Type: application/json

{
  "name": "更新后的分类名",
  "description": "更新后的描述",
  "sort_order": 2,
  "status": "inactive"
}
```

#### 1.4 删除分类
```http
DELETE /api/web/groups/{id}
```

### 2. 商品管理

#### 2.1 获取商品列表
```http
GET /api/web/product/?merchant_id=1&status=on_sale&page=1&per_page=10
```

#### 2.2 获取商品详情
```http
GET /api/web/product/{product_id}
```

#### 2.3 创建商品
```http
POST /api/web/product/
Content-Type: application/json

{
  "name": "商品名称",
  "description": "商品描述",
  "price": 999.00,
  "stock": 100,
  "group_id": 1,
  "merchant_id": 1,
  "image_url": "https://example.com/image.jpg"
}
```

### 3. 订单管理

#### 3.1 获取订单列表
```http
GET /api/web/order/?merchant_id=1&status=paid&page=1&per_page=10
```

**参数说明:**
- `merchant_id`: 商家ID（必填）
- `status`: 订单状态（pending/paid/shipped/delivered/cancelled/refunded）
- `page`: 页码
- `per_page`: 每页数量

**响应示例:**
```json
{
  "code": 200,
  "message": "获取订单列表成功",
  "data": {
    "list": [
      {
        "id": 1,
        "user_id": 1,
        "user_name": "张三",
        "user_phone": "13800138001",
        "total_amount": 7999.00,
        "status": "paid",
        "status_text": "已付款",
        "created_at": "2024-01-15 10:30:00",
        "logistics": {
          "company": "顺丰速运",
          "tracking_number": "SF1234567890",
          "status": "运输中"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 10,
      "pages": 1
    }
  }
}
```

#### 3.2 获取订单详情
```http
GET /api/web/order/{order_id}
```

#### 3.3 更新订单状态
```http
PUT /api/web/order/{order_id}/status
Content-Type: application/json

{
  "status": "shipped"
}
```

#### 3.4 添加物流信息
```http
POST /api/web/order/{order_id}/logistics
Content-Type: application/json

{
  "company": "顺丰速运",
  "tracking_number": "SF1234567890",
  "status": "已发货"
}
```

#### 3.5 获取订单统计
```http
GET /api/web/order/statistics?merchant_id=1
```

### 4. 评价管理

#### 4.1 获取评价列表
```http
GET /api/web/review/?merchant_id=1&rating=5&page=1&per_page=10
```

**参数说明:**
- `merchant_id`: 商家ID（必填）
- `product_id`: 商品ID（可选）
- `rating`: 评分筛选（1-5）
- `page`: 页码
- `per_page`: 每页数量

#### 4.2 获取评价详情
```http
GET /api/web/review/{review_id}
```

#### 4.3 回复评价
```http
POST /api/web/review/{review_id}/reply
Content-Type: application/json

{
  "reply_content": "感谢您的评价，我们会继续努力提供更好的服务！"
}
```

#### 4.4 获取评价统计
```http
GET /api/web/review/statistics?merchant_id=1
```

#### 4.5 获取商品评价
```http
GET /api/web/review/products/{product_id}?page=1&per_page=10
```

### 5. 数据分析

#### 5.1 获取仪表板数据
```http
GET /api/web/analytics/dashboard?merchant_id=1
```

**响应示例:**
```json
{
  "code": 200,
  "message": "获取仪表板数据成功",
  "data": {
    "today": {
      "orders": 15,
      "sales": 125000.00,
      "products": 3
    },
    "yesterday": {
      "orders": 12,
      "sales": 98000.00
    },
    "this_month": {
      "orders": 450,
      "sales": 3800000.00
    },
    "total": {
      "products": 150,
      "orders": 1200,
      "sales": 10000000.00,
      "avg_rating": 4.8
    }
  }
}
```

#### 5.2 获取销售分析
```http
GET /api/web/analytics/sales?merchant_id=1&period=7d
```

**参数说明:**
- `period`: 时间周期（7d/30d/90d）

#### 5.3 获取商品分析
```http
GET /api/web/analytics/products?merchant_id=1&limit=10
```

#### 5.4 获取收入分析
```http
GET /api/web/analytics/revenue?merchant_id=1
```

### 6. 资金管理

#### 6.1 获取账户信息
```http
GET /api/web/finance/account?merchant_id=1
```

**响应示例:**
```json
{
  "code": 200,
  "message": "获取账户信息成功",
  "data": {
    "id": 1,
    "merchant_id": 1,
    "balance": 5000.00,
    "available_balance": 25000.00,
    "total_income": 30000.00,
    "bank_account": "6222021234567890123",
    "created_at": "2024-01-01 10:00:00",
    "updated_at": "2024-01-15 10:00:00"
  }
}
```

#### 6.2 更新账户信息
```http
PUT /api/web/finance/account?merchant_id=1
Content-Type: application/json

{
  "bank_account": "6222021234567890123"
}
```

#### 6.3 申请提现
```http
POST /api/web/finance/withdraw?merchant_id=1
Content-Type: application/json

{
  "amount": 5000.00
}
```

#### 6.4 获取交易记录
```http
GET /api/web/finance/transactions?merchant_id=1&type=income&page=1&per_page=10
```

#### 6.5 获取财务统计
```http
GET /api/web/finance/statistics?merchant_id=1
```

#### 6.6 获取账单明细
```http
GET /api/web/finance/bills?merchant_id=1&start_date=2024-01-01&end_date=2024-01-31&page=1&per_page=10
```

### 7. 客服管理

#### 7.1 获取客服消息
```http
GET /api/web/customer_service/messages?merchant_id=1&status=pending&page=1&per_page=10
```

#### 7.2 获取消息详情
```http
GET /api/web/customer_service/messages/{message_id}
```

#### 7.3 回复消息
```http
POST /api/web/customer_service/messages/{message_id}/reply
Content-Type: application/json

{
  "reply_content": "您好，我们会尽快为您处理这个问题。"
}
```

#### 7.4 获取快捷回复
```http
GET /api/web/customer_service/quick-replies?group=greeting
```

#### 7.5 添加快捷回复
```http
POST /api/web/customer_service/quick-replies
Content-Type: application/json

{
  "content": "感谢您的咨询",
  "group": "thanks"
}
```

#### 7.6 获取自动回复设置
```http
GET /api/web/customer_service/auto-reply
```

#### 7.7 更新自动回复设置
```http
PUT /api/web/customer_service/auto-reply
Content-Type: application/json

{
  "enabled": true,
  "greeting_message": "您好，欢迎咨询我们的客服",
  "offline_message": "抱歉，客服暂时不在线",
  "working_hours": {
    "start": "09:00",
    "end": "18:00"
  }
}
```

#### 7.8 获取客服统计
```http
GET /api/web/customer_service/statistics?merchant_id=1
```

#### 7.9 获取常见问题
```http
GET /api/web/customer_service/common-questions
```

#### 7.10 添加常见问题
```http
POST /api/web/customer_service/common-questions
Content-Type: application/json

{
  "question": "如何查询订单物流？",
  "answer": "您可以在订单详情页面查看物流信息",
  "group": "order"
}
```

## 用户端App API

### 1. 商品相关

#### 1.1 获取商品列表
```http
GET /api/app/product/?group_id=1&page=1&per_page=10
```

#### 1.2 获取商品详情
```http
GET /api/app/product/{product_id}
```

### 2. 订单相关

#### 2.1 获取用户订单
```http
GET /api/app/order/?user_id=1&status=paid&page=1&per_page=10
```

### 3. 评价相关

#### 3.1 获取商品评价
```http
GET /api/app/review/?product_id=1&page=1&per_page=10
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 数据库表结构

### 主要表结构

1. **users** - 用户表
2. **merchants** - 商家表
3. **groups** - 分类表
4. **products** - 商品表
5. **orders** - 订单表
6. **reviews** - 评价表
7. **accounts** - 账户表
8. **logistics** - 物流表

## 部署说明

### 环境要求
- Python 3.12+
- MySQL 8.0+
- Flask 2.0+

### 安装依赖
```bash
pip install -r requirements.txt
```

### 数据库初始化
```sql
source scripts/sql/init_complete_database.sql
```

### 启动服务
```bash
cd app/backend
python app.py
```

## 测试数据

系统已预置测试数据，包括：
- 5个测试用户
- 5个测试商家
- 8个商品分类
- 15个测试商品
- 10个测试订单
- 10个测试评价
- 5个商家账户

## 注意事项

1. 所有API都需要在请求头中包含商家ID或用户ID
2. 图片和视频URL需要配置CDN
3. 物流信息需要对接第三方物流API
4. 支付功能需要对接第三方支付平台
5. 文件上传需要配置OSS存储

## 更新日志

### v1.0.0 (2024-01-15)
- ✅ 完成商品分类管理功能
- ✅ 完成订单管理功能
- ✅ 完成评价管理功能
- ✅ 完成数据分析功能
- ✅ 完成资金管理功能
- ✅ 完成客服管理功能
- ✅ 完成基础商品管理功能 