// 创建axios实例
import axios from 'axios'
import { getToken } from './auth.js'

// 创建axios实例
const request = axios.create({
  baseURL: '', // 使用空字符串，让proxy处理
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    const token = getToken()
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    console.log('Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('Request Error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    console.log('Response:', response.status, response.data)
    return response
  },
  error => {
    console.error('Response Error:', error)
    return Promise.reject(error)
  }
)

export default request 