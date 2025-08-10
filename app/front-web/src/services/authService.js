import { ElMessage } from 'element-plus'
import { api } from '../api/request'

class AuthService {
  constructor() {
    this.tokenKey = 'merchant_token'
    this.userInfoKey = 'merchant_info'
  }

  // 获取token
  getToken() {
    return localStorage.getItem(this.tokenKey)
  }

  // 获取用户信息
  getUserInfo() {
    const userInfo = localStorage.getItem(this.userInfoKey)
    if (userInfo) {
      try {
        return JSON.parse(userInfo)
      } catch (e) {
        console.error('解析用户信息失败:', e)
        return null
      }
    }
    return null
  }

  // 设置token和用户信息
  setAuth(token, userInfo) {
    localStorage.setItem(this.tokenKey, token)
    localStorage.setItem(this.userInfoKey, JSON.stringify(userInfo))
  }

  // 清除认证信息
  clearAuth() {
    localStorage.removeItem(this.tokenKey)
    localStorage.removeItem(this.userInfoKey)
  }

  // 检查是否已登录
  isLoggedIn() {
    const token = this.getToken()
    const userInfo = this.getUserInfo()
    
    console.log('🔍 检查登录状态:', { 
      hasToken: !!token, 
      hasUserInfo: !!userInfo,
      token: token ? token.substring(0, 20) + '...' : null,
      userInfo: userInfo ? Object.keys(userInfo) : null
    })
    
    if (!token || !userInfo) {
      console.log('❌ 缺少Token或用户信息')
      return false
    }

    // 检查token是否过期
    if (userInfo.expires_at) {
      const expiresAt = new Date(userInfo.expires_at)
      const now = new Date()
      console.log('⏰ 检查Token过期时间:', { 
        expiresAt: expiresAt.toISOString(), 
        now: now.toISOString(),
        isExpired: now > expiresAt
      })
      if (now > expiresAt) {
        console.log('❌ Token已过期，清除认证信息')
        this.clearAuth()
        return false
      }
    }

    console.log('✅ 登录状态检查通过')
    return true
  }

  // 登录
  async login(phone, password) {
    try {
      const response = await api.post('/api/web/auth/login', {
        phone,
        password
      })

      if (response.code === 200) {
        const { token, ...userInfo } = response.data
        // 确保用户信息包含必要的字段
        const authInfo = {
          ...userInfo,
          expires_at: userInfo.expires_at || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        }
        this.setAuth(token, authInfo)
        return { success: true, data: response.data }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, message: '登录失败，请重试' }
    }
  }

  // 注册
  async register(phone, password) {
    try {
      const response = await api.post('/api/web/auth/register', {
        phone,
        password
      })

      if (response.code === 200) {
        return { success: true, data: response.data }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, message: '注册失败，请重试' }
    }
  }

  // 验证token
  async validateToken() {
    const token = this.getToken()
    if (!token) {
      console.log('❌ 没有Token，验证失败')
      return false
    }

    try {
      console.log('🔍 开始验证Token...')
      // 修复：正确传递token作为查询参数
      const response = await api.get('/api/web/auth/validate', { token })
      
      console.log('📡 Token验证响应:', response)
      
      if (response.code === 200 && response.data.valid) {
        console.log('✅ Token验证成功')
        return true
      } else {
        console.log('❌ Token验证失败:', response.message)
        this.clearAuth()
        return false
      }
    } catch (error) {
      console.error('❌ Token验证请求失败:', error)
      // 如果是网络错误或API不可用，暂时不清除认证信息
      // 只有在明确知道token无效时才清除
      if (error.response && error.response.status === 401) {
        console.log('🔒 收到401未授权响应，清除认证信息')
        this.clearAuth()
      }
      return false
    }
  }

  // 获取用户资料
  async getProfile() {
    try {
      const token = this.getToken()
      if (!token) {
        return { success: false, message: '未登录' }
      }
      
      const response = await api.get('/api/web/auth/profile', { token })
      
      if (response.code === 200) {
        // 更新本地存储的用户信息
        const currentInfo = this.getUserInfo()
        const updatedInfo = { ...currentInfo, ...response.data }
        localStorage.setItem(this.userInfoKey, JSON.stringify(updatedInfo))
        
        return { success: true, data: response.data }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('获取用户资料失败:', error)
      return { success: false, message: '获取用户资料失败' }
    }
  }

  // 退出登录
  logout() {
    this.clearAuth()
    ElMessage.success('已退出登录')
  }

  // 检查token是否需要刷新
  shouldRefreshToken() {
    const userInfo = this.getUserInfo()
    if (!userInfo || !userInfo.expires_at) {
      return false
    }

    const expiresAt = new Date(userInfo.expires_at)
    const now = new Date()
    const timeUntilExpiry = expiresAt.getTime() - now.getTime()
    
    // 如果token将在1小时内过期，需要刷新
    return timeUntilExpiry < 60 * 60 * 1000
  }

  // 刷新token（如果支持的话）
  async refreshToken() {
    // 这里可以实现token刷新逻辑
    // 目前简单返回true
    return true
  }

  // 自动刷新token
  async autoRefreshToken() {
    if (this.shouldRefreshToken()) {
      const success = await this.refreshToken()
      if (!success) {
        ElMessage.warning('登录状态即将过期，请重新登录')
        return false
      }
    }
    return true
  }
}

// 创建单例实例
const authService = new AuthService()

export default authService
export { AuthService }
