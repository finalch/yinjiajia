import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import { checkAndRefreshToken } from './router/auth'
import authService from './services/authService'

const app = createApp(App)

app.use(router)
app.use(ElementPlus)

// 应用启动时检查并清理认证状态
console.log('🚀 应用启动，检查认证状态')
if (authService.isLoggedIn()) {
  console.log('✅ 检测到登录状态，验证Token')
  checkAndRefreshToken()
} else {
  console.log('❌ 未检测到登录状态')
}

app.mount('#app')
