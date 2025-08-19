// 使用uni-app的request API
import { getToken, clearToken, clearUser } from './auth.js'
import apiConfig from '../config/api.js'

// 基础配置
const baseURL = apiConfig.baseURL
const timeout = apiConfig.timeout

// 全局拦截器配置
const interceptors = {
  request: [],
  response: []
}

// 添加请求拦截器
export function addRequestInterceptor(onFulfilled, onRejected) {
  interceptors.request.push({ onFulfilled, onRejected })
}

// 添加响应拦截器
export function addResponseInterceptor(onFulfilled, onRejected) {
  interceptors.response.push({ onFulfilled, onRejected })
}

// 执行请求拦截器
function executeRequestInterceptors(config) {
  let result = config
  for (const interceptor of interceptors.request) {
    try {
      if (interceptor.onFulfilled) {
        result = interceptor.onFulfilled(result) || result
      }
    } catch (error) {
      if (interceptor.onRejected) {
        interceptor.onRejected(error)
      }
    }
  }
  return result
}

// 执行响应拦截器
function executeResponseInterceptors(response) {
  let result = response
  for (const interceptor of interceptors.response) {
    try {
      if (interceptor.onFulfilled) {
        result = interceptor.onFulfilled(result) || result
      }
    } catch (error) {
      if (interceptor.onRejected) {
        interceptor.onRejected(error)
      }
    }
  }
  return result
}

// 请求方法封装
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = getToken()
    
    // 构建请求配置
    let config = {
      url: baseURL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header
      },
      timeout: timeout,
      success: (res) => {
        console.log('Response:', res.statusCode, res.data)
        
        // 执行响应拦截器
        const processedResponse = executeResponseInterceptors({
          data: res.data,
          status: res.statusCode,
          headers: res.header,
          config: options
        })
        
        resolve(processedResponse)
      },
      fail: (err) => {
        console.error('Request Error:', err)
        
        // 执行响应拦截器（错误情况）
        const processedError = executeResponseInterceptors({
          error: err,
          config: options
        })
        
        reject(processedError)
      }
    }
    
    // 添加token
	console.log('-----token:', token)
    if (token) {
      config.header['Authorization'] = `Bearer ${token}`
    }
    
    // 执行请求拦截器
    config = executeRequestInterceptors(config)
    
    console.log('Request:', config.method?.toUpperCase(), config)
    
    // 发送请求
    uni.request(config)
  })
}

// 便捷方法
const get = (url, params = {}, config = {}) => {
  let queryString = ''
  if (Object.keys(params).length > 0) {
    queryString = '?' + Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&')
  }
  return request({
    url: url + queryString,
    method: 'GET',
    ...config
  })
}

const post = (url, data = {}, config = {}) => {
  return request({
    url,
    method: 'POST',
    data,
    ...config
  })
}

const put = (url, data = {}, config = {}) => {
  return request({
    url,
    method: 'PUT',
    data,
    ...config
  })
}

const del = (url, config = {}) => {
  return request({
    url,
    method: 'DELETE',
    ...config
  })
}

// 设置默认拦截器
// 请求拦截器：自动添加token
addRequestInterceptor((config) => {
  const token = getToken()
  if (token) {
    config.header = config.header || {}
    config.header['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理token过期、自动跳转登录
addResponseInterceptor((response) => {
  // 检查是否需要重新登录
  if (response.data && response.data.code === 401) {
    // token过期或无效
    clearToken()
    clearUser()
    
    // 跳转到登录页
    uni.showToast({
      title: '登录已过期，请重新登录',
      icon: 'none',
      duration: 2000
    })
    
    setTimeout(() => {
      uni.reLaunch({
        url: '/pages/login/login'
      })
    }, 2000)
    
    return Promise.reject(new Error('登录已过期'))
  }
  
  // 检查其他错误状态
  if (response.data && response.data.code !== 200) {
    // 显示错误信息
    uni.showToast({
      title: response.data.message || '请求失败',
      icon: 'none'
    })
  }
  
  return response
})

export default {
  request,
  get,
  post,
  put,
  delete: del,
  addRequestInterceptor,
  addResponseInterceptor
} 