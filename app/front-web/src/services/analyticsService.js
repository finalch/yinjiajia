import request from '@/api/request'

/**
 * 分析服务
 * 封装所有分析相关的API调用
 */
class AnalyticsService {
  /**
   * 获取仪表板数据
   */
  async getDashboardData() {
    try {
      const response = await request.get('/api/web/analytics/dashboard')
      return response.data
    } catch (error) {
      console.error('获取仪表板数据失败:', error)
      throw error
    }
  }

  /**
   * 获取趋势分析数据
   * @param {string} period - 时间周期：7d, 30d, 90d
   */
  async getTrendsData(period = '7d') {
    try {
      const response = await request.get('/api/web/analytics/trends', {
        params: { period }
      })
      return response.data
    } catch (error) {
      console.error('获取趋势数据失败:', error)
      throw error
    }
  }

  /**
   * 获取趋势对比数据
   */
  async getTrendsComparison() {
    try {
      const response = await request.get('/api/web/analytics/trends/compare')
      return response.data
    } catch (error) {
      console.error('获取趋势对比数据失败:', error)
      throw error
    }
  }

  /**
   * 获取销售分析数据
   * @param {string} period - 时间周期：7d, 30d, 90d
   */
  async getSalesAnalytics(period = '7d') {
    try {
      const response = await request.get('/api/web/analytics/sales', {
        params: { period }
      })
      return response.data
    } catch (error) {
      console.error('获取销售分析数据失败:', error)
      throw error
    }
  }

  /**
   * 获取商品分析数据
   * @param {number} limit - 限制数量
   */
  async getProductAnalytics(limit = 10) {
    try {
      const response = await request.get('/api/web/analytics/products', {
        params: { limit }
      })
      return response.data
    } catch (error) {
      console.error('获取商品分析数据失败:', error)
      throw error
    }
  }

  /**
   * 获取收入分析数据
   */
  async getRevenueAnalytics() {
    try {
      const response = await request.get('/api/web/analytics/revenue')
      return response.data
    } catch (error) {
      console.error('获取收入分析数据失败:', error)
      throw error
    }
  }
}

// 创建单例实例
const analyticsService = new AnalyticsService()

export default analyticsService
