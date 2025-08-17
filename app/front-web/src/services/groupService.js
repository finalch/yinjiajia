import request from '../api/request'
import authService from './authService'

class GroupService {
  constructor() {
    this.baseUrl = '/api/web/group/'
  }

  // 获取分组列表
  async getGroups(params = {}) {
    try {
      // 如果没有传入 merchant_id，则从当前登录用户获取
      // if (!params.merchant_id) {
      //   const userInfo = authService.getUserInfo()
      //   params.merchant_id = userInfo?.merchant_id || 1 // 默认值
      // }

      const response = await request.get(this.baseUrl, { params })
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data.list || [],
          total: response.data.data.total || 0
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取分组列表失败',
          data: []
        }
      }
    } catch (error) {
      console.error('获取分组列表失败:', error)
      return {
        success: false,
        message: '网络错误，请重试',
        data: []
      }
    }
  }

  // 获取单个分组详情
  async getGroup(groupId) {
    try {
      const response = await request.get(`${this.baseUrl}/${groupId}`)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data
        }
      } else {
        return {
          success: false,
          message: response.data.message || '获取分组详情失败'
        }
      }
    } catch (error) {
      console.error('获取分组详情失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 创建分组
  async createGroup(groupData) {
    try {
      const response = await request.post(this.baseUrl, groupData)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: '创建分组成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '创建分组失败'
        }
      }
    } catch (error) {
      console.error('创建分组失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 更新分组
  async updateGroup(groupId, groupData) {
    try {
      const response = await request.put(`${this.baseUrl}/${groupId}`, groupData)
      
      if (response.data.code === 200) {
        return {
          success: true,
          data: response.data.data,
          message: '更新分组成功'
        }
      } else {
        return {
          success: false,
          message: response.data.message || '更新分组失败'
        }
      }
    } catch (error) {
      console.error('更新分组失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 删除分组
  async deleteGroup(groupId) {
    try {
        const response = await request.delete(`${this.baseUrl}/${groupId}`)
        
        if (response.data.code === 200) {
          return {
            success: true,
            message: '删除分组成功'
          }
        } else {
          return {
            success: false,
            message: response.data.message || '删除分组失败'
          }
        }
      } catch (error) {
        console.error('删除分组失败:', error)
        return {
          success: false,
          message: '网络错误，请重试'
        }
      }
    }

  // 批量删除分组
  async batchDeleteGroups(groupIds) {
    try {
      const response = await request.delete(`${this.baseUrl}/batch`, {
        data: { group_ids: groupIds }
      })
      
      if (response.data.code === 200) {
        return {
          success: true,
          message: '批量删除分组成功',
          data: response.data.data
        }
      } else {
        return {
          success: false,
          message: response.data.message || '批量删除分组失败'
        }
      }
    } catch (error) {
      console.error('批量删除分组失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }

  // 切换分组状态
  async toggleGroupStatus(groupId, status) {
    try {
      const response = await request.put(`${this.baseUrl}/${groupId}`, { status })
      
      if (response.data.code === 200) {
        return {
          success: true,
          message: '状态更新成功',
          data: response.data.data
        }
      } else {
        return {
          success: false,
          message: response.data.message || '状态更新失败'
        }
      }
    } catch (error) {
      console.error('状态更新失败:', error)
      return {
        success: false,
        message: '网络错误，请重试'
      }
    }
  }
}

// 创建单例实例
const groupService = new GroupService()

export default groupService
export { GroupService }
