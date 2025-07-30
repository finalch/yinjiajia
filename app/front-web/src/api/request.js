import axios from 'axios'

const instance = axios.create({
  baseURL: '', // 使用相对路径，让 vite 代理生效
  timeout: 10000
})

export default instance 