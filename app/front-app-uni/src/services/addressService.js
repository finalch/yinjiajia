import request from '@/src/utils/request.js'
import { getUserId } from '@/src/utils/auth.js'

/**
 * Address Service - 地址服务
 * 遵循DDD原则，封装地址相关的业务逻辑
 * 适配 uni-app 环境
 */
class AddressService {
	/**
	 * 获取用户默认地址
	 * 优先从本地存储获取，如果没有则从后端API获取并缓存
	 * @param {number} userId - 用户ID
	 * @returns {Promise<Object|null>} 默认地址对象或null
	 */
	static async getDefaultAddress(userId) {
		try {
			// 1. 优先从本地存储获取选中的地址
			const uid = userId || getUserId()
			const cachedAddress = this.getSelectedAddress()
			if (cachedAddress) {
				return cachedAddress
			}

			// 2. 如果本地存储中没有地址，则从后端获取默认地址
			const response = await request.get('/api/app/address/default', {
				params: { user_id: uid }
			})
			
			if (response.data.code === 200 && response.data.data) {
				const defaultAddress = response.data.data
				// 3. 缓存默认地址到本地存储
				this.setSelectedAddress(defaultAddress)
				return defaultAddress
			} else {
				console.error('获取默认地址失败:', response.data.message)
				return null
			}
		} catch (error) {
			console.error('获取默认地址异常:', error)
			return null
		}
	}

	/**
	 * 设置选中的地址到本地存储
	 * @param {Object} address - 地址对象
	 */
	static setSelectedAddress(address) {
		try {
			const uid = getUserId()
			if (address && uid) {
				// 使用 uni-app 的存储API
				uni.setStorageSync(`selectedAddress:${uid}`, JSON.stringify(address))
			}
		} catch (error) {
			console.error('保存地址到本地存储失败:', error)
		}
	}

	/**
	 * 清除选中的地址本地存储
	 */
	static clearSelectedAddress() {
		try {
			const uid = getUserId()
			if (uid) {
				uni.removeStorageSync(`selectedAddress:${uid}`)
			}
		} catch (error) {
			console.error('清除地址本地存储失败:', error)
		}
	}

	/**
	 * 从本地存储获取选中的地址
	 * @returns {Object|null} 地址对象或null
	 */
	static getSelectedAddress() {
		try {
			const uid = getUserId()
			if (!uid) return null
			
			const cachedAddress = uni.getStorageSync(`selectedAddress:${uid}`)
			if (cachedAddress) {
				return JSON.parse(cachedAddress)
			}
		} catch (error) {
			console.error('获取地址本地存储失败:', error)
			// 如果解析失败，清除损坏的数据
			this.clearSelectedAddress()
		}
		return null
	}

	/**
	 * 获取用户所有地址
	 * @param {number} userId - 用户ID
	 * @returns {Promise<Array>} 地址列表
	 */
	static async getUserAddresses(userId) {
		try {
			const uid = userId || getUserId()
			const response = await request.get('/api/app/address/', {
				params: { user_id: uid }
			})
			
			if (response.data.code === 200) {
				return response.data.data || []
			} else {
				console.error('获取地址列表失败:', response.data.message)
				return []
			}
		} catch (error) {
			console.error('获取地址列表异常:', error)
			return []
		}
	}

	/**
	 * 添加新地址
	 * @param {Object} addressData - 地址数据
	 * @returns {Promise<Object|null>} 添加结果
	 */
	static async addAddress(addressData) {
		try {
			const uid = getUserId()
			if (!uid) {
				throw new Error('用户未登录')
			}

			const response = await request.post('/api/app/address/', {
				...addressData,
				user_id: uid
			})
			
			if (response.data.code === 200) {
				return response.data.data
			} else {
				throw new Error(response.data.message || '添加地址失败')
			}
		} catch (error) {
			console.error('添加地址失败:', error)
			throw error
		}
	}

	/**
	 * 更新地址
	 * @param {number} addressId - 地址ID
	 * @param {Object} addressData - 地址数据
	 * @returns {Promise<Object|null>} 更新结果
	 */
	static async updateAddress(addressId, addressData) {
		try {
			const uid = getUserId()
			if (!uid) {
				throw new Error('用户未登录')
			}

			const response = await request.put(`/api/app/address/${addressId}`, {
				...addressData,
				user_id: uid
			})
			
			if (response.data.code === 200) {
				return response.data.data
			} else {
				throw new Error(response.data.message || '更新地址失败')
			}
		} catch (error) {
			console.error('更新地址失败:', error)
			throw error
		}
	}

	/**
	 * 删除地址
	 * @param {number} addressId - 地址ID
	 * @returns {Promise<boolean>} 删除结果
	 */
	static async deleteAddress(addressId) {
		try {
			const uid = getUserId()
			if (!uid) {
				throw new Error('用户未登录')
			}

			const response = await request.delete(`/api/app/address/${addressId}`)
			
			if (response.data.code === 200) {
				return true
			} else {
				throw new Error(response.data.message || '删除地址失败')
			}
		} catch (error) {
			console.error('删除地址失败:', error)
			throw error
		}
	}

	/**
	 * 设置默认地址
	 * @param {number} addressId - 地址ID
	 * @returns {Promise<boolean>} 设置结果
	 */
	static async setDefaultAddress(addressId) {
		try {
			const uid = getUserId()
			if (!uid) {
				throw new Error('用户未登录')
			}

			const response = await request.put(`/api/app/address/${addressId}/default`, {
				user_id: uid
			})
			
			if (response.data.code === 200) {
				return true
			} else {
				throw new Error(response.data.message || '设置默认地址失败')
			}
		} catch (error) {
			console.error('设置默认地址失败:', error)
			throw error
		}
	}

	/**
	 * 验证地址数据
	 * @param {Object} addressData - 地址数据
	 * @returns {Object} 验证结果 { isValid: boolean, errors: Array }
	 */
	static validateAddress(addressData) {
		const errors = []
		
		if (!addressData.receiver_name || addressData.receiver_name.trim() === '') {
			errors.push('收货人姓名不能为空')
		}
		
		if (!addressData.phone || !/^1[3-9]\d{9}$/.test(addressData.phone)) {
			errors.push('请输入正确的手机号码')
		}
		
		if (!addressData.province || addressData.province.trim() === '') {
			errors.push('省份不能为空')
		}
		
		if (!addressData.city || addressData.city.trim() === '') {
			errors.push('城市不能为空')
		}
		
		if (!addressData.district || addressData.district.trim() === '') {
			errors.push('区县不能为空')
		}
		
		if (!addressData.detail_address || addressData.detail_address.trim() === '') {
			errors.push('详细地址不能为空')
		}
		
		return {
			isValid: errors.length === 0,
			errors
		}
	}
}

export default AddressService