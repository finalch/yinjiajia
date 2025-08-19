import request from '../utils/request'

class CategoryService {
  constructor() {
    this.baseUrl = '/api/g/category/'
  }

  // 获取品类列表
  async getCategories(params = {}) {
    try {
      const response = await request.get(this.baseUrl, params)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data.list || [],
          total: response.data.data.list?.length || 0
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取品类列表失败',
          data: []
        }
      }
    } catch (error) {
      console.error('获取品类列表失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: []
      }
    }
  }

  // 获取单个品类详情
  async getCategory(categoryId) {
    try {
      const response = await request.get(`${this.baseUrl}/${categoryId}`)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取品类详情失败'
        }
      }
    } catch (error) {
      console.error('获取品类详情失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 创建品类（如果需要的话）
  async createCategory(categoryData) {
    try {
      const response = await request.post(this.baseUrl, categoryData)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: '创建品类成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '创建品类失败'
        }
      }
    } catch (error) {
      console.error('创建品类失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 更新品类（如果需要的话）
  async updateCategory(categoryId, categoryData) {
    try {
      const response = await request.put(`${this.baseUrl}/${categoryId}`)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: '更新品类成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '更新品类失败'
        }
      }
    } catch (error) {
      console.error('更新品类失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 删除品类（如果需要的话）
  async deleteCategory(categoryId) {
    try {
      const response = await request.delete(`${this.baseUrl}/${categoryId}`)
      
      if (response.data.code === 200) {
        return {
          success: true,
          message: '删除品类成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '删除品类失败'
        }
      }
    } catch (error) {
      console.error('删除品类失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 根据名称搜索品类
  async searchCategories(keyword) {
    try {
      const response = await request.get(this.baseUrl, { name: keyword })
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data.list || []
        }
      } else {
        return {
          success: false,
          message: response.data.message || '搜索品类失败',
          data: []
        }
      }
    } catch (error) {
      console.error('搜索品类失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: []
      }
    }
  }

  // 获取热门品类（按排序权重）
  async getPopularCategories(limit = 10) {
    try {
      const response = await request.get(this.baseUrl, { sort: 'sort_order', limit })
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data.list || []
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取热门品类失败',
          data: []
        }
      }
    } catch (error) {
      console.error('获取热门品类失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: []
      }
    }
  }
}

// 创建单例实例
const categoryService = new CategoryService()

export default categoryService
export { CategoryService }
