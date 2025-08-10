// 路由守卫中间件
import { ElMessage } from 'element-plus'
import authService from '../services/authService'

// 需要登录才能访问的路由
const protectedRoutes = [
  '/dashboard',
  '/products',
  '/categories',
  '/orders',
  '/logistics',
  '/analytics',
  '/finance',
  '/customer-service',
  '/reviews',
  '/settings'
]

// 不需要登录就能访问的路由
const publicRoutes = [
  '/login',
  '/register',
  '/test-auth'
]

// 检查是否已登录
export function isAuthenticated() {
  return authService.isLoggedIn()
}

// 获取商家信息
export function getMerchantInfo() {
  return authService.getUserInfo()
}

// 清除登录信息
export function clearAuth() {
  authService.clearAuth()
}

// 路由守卫
export function setupRouteGuard(router) {
  router.beforeEach(async (to, from, next) => {
    console.log('🚦 路由守卫触发:', { from: from.path, to: to.path })
    
    try {
      // 检查是否是受保护的路由（更精确的匹配）
      const isProtectedRoute = protectedRoutes.some(route => {
        if (route === '/products') {
          // 特殊处理products相关路由
          return to.path.startsWith('/products')
        }
        return to.path.startsWith(route)
      })
      
      const isPublicRoute = publicRoutes.some(route => 
        to.path === route
      )

      // 特殊处理根路径
      if (to.path === '/') {
        console.log('🏠 访问根路径，重定向到登录页')
        next('/login')
        return
      }
      
      console.log('🔒 路由类型:', { 
        isProtectedRoute, 
        isPublicRoute, 
        isAuthenticated: isAuthenticated(),
        path: to.path
      })
      
      // 如果是受保护的路由
      if (isProtectedRoute) {
        console.log('🛡️ 访问受保护路由，检查认证状态')
        if (!isAuthenticated()) {
          console.log('❌ 未登录，跳转到登录页')
          ElMessage.warning('请先登录')
          next('/login')
          return
        }
        
        console.log('✅ 已登录，验证Token有效性')
        // 验证token有效性
        try {
          const isValid = await authService.validateToken()
          if (!isValid) {
            console.log('❌ Token无效，跳转到登录页')
            ElMessage.error('登录已过期，请重新登录')
            clearAuth()
            next('/login')
            return
          }
          
          console.log('✅ Token有效，检查是否需要刷新')
          // 检查是否需要刷新token
          await authService.autoRefreshToken()
        } catch (error) {
          console.error('Token验证过程中出错:', error)
          ElMessage.error('登录验证失败，请重新登录')
          clearAuth()
          next('/login')
          return
        }
      }
      
      // 如果已登录用户访问登录/注册页面，重定向到首页
      if (isPublicRoute && isAuthenticated()) {
        console.log('🔄 已登录用户访问公开页面，重定向到Dashboard')
        next('/dashboard')
        return
      }
      
      console.log('✅ 路由守卫通过，继续导航')
      next()
    } catch (error) {
      console.error('❌ 路由守卫错误:', error)
      // 发生错误时，清除认证信息并跳转到登录页
      clearAuth()
      ElMessage.error('系统错误，请重新登录')
      next('/login')
    }
  })
}

// 验证token有效性
export async function validateToken() {
  return await authService.validateToken()
}

// 刷新token（如果支持的话）
export async function refreshToken() {
  return await authService.refreshToken()
}

// 检查并自动刷新token
export async function checkAndRefreshToken() {
  return await authService.autoRefreshToken()
}
