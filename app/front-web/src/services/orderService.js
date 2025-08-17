import request from '../api/request'

class OrderService {
    constructor() {
        this.baseUrl = '/api/web/order/'
    }

    async getOrders(params = {}) {
        try {
            const response = await request.get(this.baseUrl, {params})
            if (response.data.code === 200) {
                return {
                    success: true,
                    data: response.data.data || [],
                    total: response.data.data?.length || 0,
                    pagination: response.data.data?.pagination || {}
                }
            } else {
                return {
                    success: false,
                    message: response.data.message || '获取订单列表失败',
                    data: []
                }
            }
        } catch (error) {
            console.error('获取订单列表失败:', error)
            return {
                success: false,
                message: '网络错误，请重试',
                data: []
            }
        }
    }
    async getOrderStatistics() {
        try {
            const response = await request.get(this.baseUrl + 'statistics')
            if (response.data.code === 200) {
                return response.data
            } else {
                return {
                    success: false,
                    message: response.data.message || '获取订单统计失败',
                    data: []
                }
            }
        } catch (error) {
            console.error('获取订单统计失败:', error)
            return {
                success: false,
                message: '网络错误，请重试',
                data: []
            }
        }
    }
}

const orderService = new OrderService()

export default orderService
export {OrderService}