import request from '../utils/request.js'

/**
 * Address Service - 地址服务
 * 遵循DDD原则，封装地址相关的业务逻辑
 */
class AddressService {
  /**
   * 获取用户默认地址
   * 优先从localStorage获取，如果没有则从后端API获取并缓存
   * @param {number} userId - 用户ID
   * @returns {Promise<Object|null>} 默认地址对象或null
   */
  static async getDefaultAddress(userId) {
    try {
      // 1. 优先从localStorage获取选中的地址
      const cachedAddress = localStorage.getItem('selectedAddress')
      if (cachedAddress) {
        try {
          return JSON.parse(cachedAddress)
        } catch (e) {
          console.error('解析缓存的地址失败:', e)
          localStorage.removeItem('selectedAddress')
        }
      }
      
      // 2. 如果localStorage中没有地址，则从后端获取默认地址
      const response = await request.get('/api/app/address/default', { 
        params: { user_id: userId } 
      })
      
      if (response.data.code === 200 && response.data.data) {
        const defaultAddress = response.data.data
        // 3. 缓存默认地址到localStorage
        localStorage.setItem('selectedAddress', JSON.stringify(defaultAddress))
        return defaultAddress
      } else {
        console.error('获取默认地址失败:', response.data.message)
        return null
      }
    } catch (error) {
      console.error('加载地址信息失败:', error)
      return null
    }
  }

  /**
   * 设置选中的地址到缓存
   * @param {Object} address - 地址对象
   */
  static setSelectedAddress(address) {
    if (address) {
      localStorage.setItem('selectedAddress', JSON.stringify(address))
    }
  }

  /**
   * 清除选中的地址缓存
   */
  static clearSelectedAddress() {
    localStorage.removeItem('selectedAddress')
  }

  /**
   * 从缓存获取选中的地址
   * @returns {Object|null} 地址对象或null
   */
  static getSelectedAddress() {
    try {
      const cachedAddress = localStorage.getItem('selectedAddress')
      if (cachedAddress) {
        return JSON.parse(cachedAddress)
      }
    } catch (e) {
      console.error('解析缓存的地址失败:', e)
      localStorage.removeItem('selectedAddress')
    }
    return null
  }
}

export default AddressService 