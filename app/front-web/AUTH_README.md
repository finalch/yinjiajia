# 商家端登录状态拦截系统说明

## 概述

本系统实现了完整的商家端登录状态拦截功能，包括：

- 路由守卫：自动拦截未登录用户访问受保护页面
- Token验证：定期验证登录状态的有效性
- 自动跳转：未登录用户自动跳转到登录页
- 状态管理：统一的认证状态管理

## 核心组件

### 1. 路由守卫 (`src/router/auth.js`)

- **setupRouteGuard()**: 设置全局路由守卫
- **isAuthenticated()**: 检查是否已登录
- **getMerchantInfo()**: 获取商家信息
- **clearAuth()**: 清除认证信息

### 2. 认证服务 (`src/services/authService.js`)

- **login()**: 商家登录
- **register()**: 商家注册
- **validateToken()**: 验证Token有效性
- **getProfile()**: 获取商家资料
- **logout()**: 退出登录

### 3. API请求拦截 (`src/api/request.js`)

- 自动添加Authorization头
- 401状态码自动跳转登录页
- 统一的错误处理

## 使用方法

### 1. 登录流程

```javascript
import authService from '../services/authService'

// 登录
const result = await authService.login(phone, password)
if (result.success) {
  // 登录成功，自动跳转到Dashboard
  router.push('/dashboard')
}
```

### 2. 检查登录状态

```javascript
import { isAuthenticated } from '../router/auth'

if (isAuthenticated()) {
  // 用户已登录
} else {
  // 用户未登录
}
```

### 3. 获取商家信息

```javascript
import { getMerchantInfo } from '../router/auth'

const merchantInfo = getMerchantInfo()
console.log(merchantInfo.merchant_number)
```

### 4. 退出登录

```javascript
import { clearAuth } from '../router/auth'

clearAuth() // 清除本地存储的认证信息
router.push('/login') // 跳转到登录页
```

## 受保护的路由

以下路由需要登录才能访问：

- `/dashboard` - 数据概览
- `/products` - 商品管理
- `/orders` - 订单管理
- `/analytics` - 数据分析
- `/finance` - 财务管理
- `/settings` - 系统设置

## 公开路由

以下路由无需登录即可访问：

- `/login` - 登录页
- `/register` - 注册页
- `/test-auth` - 认证测试页

## 测试功能

访问 `/test-auth` 页面可以测试各种认证功能：

- 检查当前认证状态
- 验证Token有效性
- 获取用户资料
- 清除认证信息
- 测试路由跳转

## 后端接口

### 认证接口

- `POST /api/web/auth/login` - 商家登录
- `POST /api/web/auth/register` - 商家注册
- `GET /api/web/auth/validate` - 验证Token
- `GET /api/web/auth/profile` - 获取商家资料

### 健康检查

- `GET /api/web/health/ping` - 连接测试
- `GET /api/web/health/status` - 系统状态

## 安全特性

1. **Token过期检查**: 自动检查Token是否过期
2. **自动跳转**: 未登录用户自动跳转到登录页
3. **状态同步**: 前端状态与后端Token保持同步
4. **错误处理**: 统一的错误处理和用户提示

## 注意事项

1. Token有效期为7天
2. 登录状态存储在localStorage中
3. 页面刷新后会自动验证Token有效性
4. 网络错误时会自动清除认证状态

## 故障排除

### 常见问题

1. **登录后无法跳转**: 检查路由守卫是否正确设置
2. **Token验证失败**: 检查后端接口是否正常
3. **页面无限跳转**: 检查认证状态判断逻辑

### 调试方法

1. 打开浏览器开发者工具
2. 查看Console日志
3. 访问 `/test-auth` 页面进行功能测试
4. 检查Network面板中的API请求
