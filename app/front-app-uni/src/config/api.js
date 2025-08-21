// API配置文件
const config = {
  // 开发环境
  development: {
    baseURL: 'http://192.168.1.17:6000',
    timeout: 10000
  },
  // 生产环境
  production: {
    baseURL: 'https://your-production-domain.com',
    timeout: 10000
  },
  // 测试环境
  test: {
    baseURL: 'https://your-test-domain.com',
    timeout: 10000
  }
}

// 获取当前环境
function getCurrentEnv() {
  // #ifdef H5
  if (process.env.NODE_ENV === 'development') {
    return 'development'
  }
  // #endif
  
  // #ifdef MP-WEIXIN
  return 'development' // 小程序开发环境
  // #endif
  
  // #ifdef APP-PLUS
  return 'development' // App开发环境
  // #endif
  
  return 'production'
}

// 导出当前环境的配置
export const apiConfig = config[getCurrentEnv()] || config.development

export default apiConfig
