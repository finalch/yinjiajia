import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://127.0.0.1:5000', // 后端API基础地址，可根据需要修改
  timeout: 10000 // 超时时间10秒
})

// 可在此添加请求/响应拦截器
// instance.interceptors.request.use(...)
// instance.interceptors.response.use(...)

export default instance 