# 银家家前端应用

这是一个基于 Vue 3 + Vite 的前端应用，支持打包成 Android 和 iOS 原生应用。

## 开发环境运行

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173 查看应用。

## 构建 Web 版本

```bash
# 构建生产版本
npm run build
```

构建后的文件在 `dist` 目录中。

## 打包成移动应用

### 1. 构建 Web 版本
```bash
npm run build:mobile
```

### 2. 添加平台支持

#### Android
```bash
# 安装 Android 平台
npx cap add android

# 同步代码到 Android 项目
npx cap sync android

# 用 Android Studio 打开项目
npx cap open android
```

#### iOS
```bash
# 安装 iOS 平台
npx cap add ios

# 同步代码到 iOS 项目
npx cap sync ios

# 用 Xcode 打开项目
npx cap open ios
```

## 项目结构

```
src/
├── views/           # 页面组件
│   ├── shop.vue              # 商城页面
│   ├── purchase.vue          # 购买页面
│   ├── cartList.vue          # 购物车
│   ├── product-detail.vue    # 商品详情
│   ├── payment.vue           # 支付页面
│   ├── pay-result.vue        # 支付结果
│   ├── myorder.vue           # 我的订单
│   └── customer-service.vue  # 客服页面
├── components/      # 通用组件
├── router/         # 路由配置
│   └── index.js
├── App.vue         # 根组件
└── main.js         # 入口文件
```

## 技术栈

- Vue 3
- Vue Router 4
- Vite
- Capacitor (移动端打包)

## 注意事项

1. 确保已安装 Node.js 和 npm
2. Android 开发需要安装 Android Studio 和 Android SDK
3. iOS 开发需要 macOS 系统和 Xcode
4. 首次运行移动端项目前，需要先执行 `npm run build:mobile`
