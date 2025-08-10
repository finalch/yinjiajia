import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import authService from '../services/authService'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('merchant_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('merchant_info') || 'null'))
  const isAuthenticated = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => {
    return isAuthenticated.value && !!token.value && !!userInfo.value
  })

  const merchantName = computed(() => {
    return userInfo.value?.merchant_number || '商家管理员'
  })

  const merchantId = computed(() => {
    return userInfo.value?.merchant_id || null
  })

  // 动作
  const setAuth = (newToken, newUserInfo) => {
    token.value = newToken
    userInfo.value = newUserInfo
    isAuthenticated.value = true
    
    // 保存到本地存储
    localStorage.setItem('merchant_token', newToken)
    localStorage.setItem('merchant_info', JSON.stringify(newUserInfo))
  }

  const clearAuth = () => {
    token.value = ''
    userInfo.value = null
    isAuthenticated.value = false
    
    // 清除本地存储
    localStorage.removeItem('merchant_token')
    localStorage.removeItem('merchant_info')
  }

  const login = async (phone, password) => {
    try {
      const result = await authService.login(phone, password)
      
      if (result.success) {
        const { token: newToken, ...userData } = result.data
        setAuth(newToken, userData)
        return { success: true }
      } else {
        return { success: false, message: result.message }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, message: '登录失败，请重试' }
    }
  }

  const logout = () => {
    clearAuth()
    authService.logout()
  }

  const validateToken = async () => {
    try {
      const isValid = await authService.validateToken()
      if (!isValid) {
        clearAuth()
      }
      return isValid
    } catch (error) {
      console.error('Token验证失败:', error)
      return false
    }
  }

  const refreshToken = async () => {
    try {
      return await authService.autoRefreshToken()
    } catch (error) {
      console.error('Token刷新失败:', error)
      return false
    }
  }

  const updateUserInfo = async () => {
    try {
      const result = await authService.getProfile()
      if (result.success) {
        userInfo.value = { ...userInfo.value, ...result.data }
        localStorage.setItem('merchant_info', JSON.stringify(userInfo.value))
      }
      return result
    } catch (error) {
      console.error('更新用户信息失败:', error)
      return { success: false, message: '更新用户信息失败' }
    }
  }

  // 初始化认证状态
  const initAuth = () => {
    const storedToken = localStorage.getItem('merchant_token')
    const storedUserInfo = localStorage.getItem('merchant_info')
    
    if (storedToken && storedUserInfo) {
      try {
        const parsedUserInfo = JSON.parse(storedUserInfo)
        
        // 检查token是否过期
        if (parsedUserInfo.expires_at) {
          const expiresAt = new Date(parsedUserInfo.expires_at)
          if (new Date() > expiresAt) {
            clearAuth()
            return
          }
        }
        
        token.value = storedToken
        userInfo.value = parsedUserInfo
        isAuthenticated.value = true
      } catch (error) {
        console.error('初始化认证状态失败:', error)
        clearAuth()
      }
    }
  }

  // 初始化
  initAuth()

  return {
    // 状态
    token,
    userInfo,
    isAuthenticated,
    
    // 计算属性
    isLoggedIn,
    merchantName,
    merchantId,
    
    // 动作
    setAuth,
    clearAuth,
    login,
    logout,
    validateToken,
    refreshToken,
    updateUserInfo,
    initAuth
  }
})
