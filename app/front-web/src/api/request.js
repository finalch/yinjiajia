import { ElMessage } from 'element-plus'
import { clearAuth } from '../router/auth'
import router from '../router'

// 创建API客户端
class ApiClient {
  constructor() {
    this.baseURL = '' // 相对路径，使用当前域名
    this.timeout = 10000
  }

  // 获取请求头
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    }
    
    const token = localStorage.getItem('merchant_token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    return headers
  }

  // 创建带超时的fetch请求
  async fetchWithTimeout(url, options, timeout = this.timeout) {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      if (error.name === 'AbortError') {
        throw new Error('请求超时')
      }
      throw error
    }
  }

  // 处理响应
  async handleResponse(response) {
    if (!response.ok) {
      if (response.status === 401) {
        // 认证失败，清除登录信息并跳转到登录页
        ElMessage.error('登录已过期，请重新登录')
        clearAuth()
        router.push('/login')
        throw new Error('认证失败')
      } else if (response.status === 403) {
        ElMessage.error('权限不足')
        throw new Error('权限不足')
      } else if (response.status >= 500) {
        ElMessage.error('服务器错误，请稍后重试')
        throw new Error('服务器错误')
      } else {
        ElMessage.error('请求失败')
        throw new Error('请求失败')
      }
    }
    
    try {
      return await response.json()
    } catch (error) {
      console.error('解析响应失败:', error)
      throw new Error('响应解析失败')
    }
  }

  // GET请求
  async get(url, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const fullUrl = queryString ? `${url}?${queryString}` : url
    
    try {
      console.log('📡 发送GET请求:', fullUrl, params)
      const response = await this.fetchWithTimeout(fullUrl, {
        method: 'GET',
        headers: this.getHeaders()
      })
      
      const result = await this.handleResponse(response)
      console.log('📡 GET请求响应:', result)
      return result
    } catch (error) {
      console.error('❌ GET请求失败:', error)
      throw error
    }
  }

  // POST请求
  async post(url, data = {}) {
    try {
      console.log('📡 发送POST请求:', url, data)
      const response = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(data)
      })
      
      const result = await this.handleResponse(response)
      console.log('📡 POST请求响应:', result)
      return result
    } catch (error) {
      console.error('❌ POST请求失败:', error)
      throw error
    }
  }

  // PUT请求
  async put(url, data = {}) {
    try {
      console.log('📡 发送PUT请求:', url, data)
      const response = await this.fetchWithTimeout(url, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(data)
      })
      
      const result = await this.handleResponse(response)
      console.log('📡 PUT请求响应:', result)
      return result
    } catch (error) {
      console.error('❌ PUT请求失败:', error)
      throw error
    }
  }

  // DELETE请求
  async delete(url) {
    try {
      console.log('📡 发送DELETE请求:', url)
      const response = await this.fetchWithTimeout(url, {
        method: 'DELETE',
        headers: this.getHeaders()
      })
      
      const result = await this.handleResponse(response)
      console.log('📡 DELETE请求响应:', result)
      return result
    } catch (error) {
      console.error('❌ DELETE请求失败:', error)
      throw error
    }
  }

  // 上传文件
  async upload(url, formData) {
    try {
      const headers = {}
      const token = localStorage.getItem('merchant_token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
      
      const response = await this.fetchWithTimeout(url, {
        method: 'POST',
        headers,
        body: formData
      })
      
      return await this.handleResponse(response)
    } catch (error) {
      console.error('❌ 文件上传失败:', error)
      throw error
    }
  }
}

// 创建实例
const apiClient = new ApiClient()

// 导出实例和类
export default apiClient
export { ApiClient }

// 便捷方法
export const api = {
  get: (url, params) => apiClient.get(url, params),
  post: (url, data) => apiClient.post(url, data),
  put: (url, data) => apiClient.put(url, data),
  delete: (url) => apiClient.delete(url),
  upload: (url, formData) => apiClient.upload(url, formData)
} 