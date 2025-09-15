import request from '../api/request'

class WarehouseService {
  constructor() {
    this.baseUrl = '/api/web/warehouse'
  }

  // 获取仓库列表
  async getWarehouseList(params = {}) {
    try {
      const response = await request.get(`${this.baseUrl}/list`, { params })
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data.warehouses || [],
          pagination: response.data.data.pagination || {},
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取仓库列表失败',
          data: []
        }
      }
    } catch (error) {
      console.error('获取仓库列表失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: []
      }
    }
  }

  // 获取仓库详情
  async getWarehouseDetail(warehouseId) {
    try {
      const response = await request.get(`${this.baseUrl}/detail/${warehouseId}`)
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取仓库详情失败',
          data: null
        }
      }
    } catch (error) {
      console.error('获取仓库详情失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }

  // 创建仓库
  async createWarehouse(warehouseData) {
    try {
      const response = await request.post(`${this.baseUrl}/create`, warehouseData)
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '创建仓库失败',
          data: null
        }
      }
    } catch (error) {
      console.error('创建仓库失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }

  // 更新仓库
  async updateWarehouse(warehouseId, warehouseData) {
    try {
      const response = await request.put(`${this.baseUrl}/update/${warehouseId}`, warehouseData)
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '更新仓库失败',
          data: null
        }
      }
    } catch (error) {
      console.error('更新仓库失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }

  // 切换仓库状态
  async toggleWarehouseStatus(warehouseId) {
    try {
      const response = await request.put(`${this.baseUrl}/toggle-status/${warehouseId}`)
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '切换仓库状态失败',
          data: null
        }
      }
    } catch (error) {
      console.error('切换仓库状态失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }

  // 删除仓库
  async deleteWarehouse(warehouseId) {
    try {
      const response = await request.delete(`${this.baseUrl}/delete/${warehouseId}`)
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '删除仓库失败',
          data: null
        }
      }
    } catch (error) {
      console.error('删除仓库失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }

  // 批量删除仓库
  async batchDeleteWarehouses(warehouseIds) {
    try {
      const response = await request.delete(`${this.baseUrl}/batch-delete`, {
        warehouse_ids: warehouseIds
      })
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: response.data.message
        }
      } else {
        return {
          success: false,
          message: response.data.message || '批量删除仓库失败',
          data: null
        }
      }
    } catch (error) {
      console.error('批量删除仓库失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: null
      }
    }
  }
}

// 创建单例实例
const warehouseService = new WarehouseService()

export default warehouseService
export { WarehouseService }
