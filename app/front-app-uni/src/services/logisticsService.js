import request from '../utils/request'

class LogisticsService {
    constructor() {
        this.baseUrl = '/api/app/logistics/'
    }

    /**
     * 查询物流路由信息
     * @param {string} trackingNumber - 物流单号
     * @param {string} company - 物流公司代码
     * @param {string} shippingNo - 运单号
     * @returns {Promise<Object>} 物流路由信息
     */
    async queryLogisticsRoute(trackingNumber, company, shippingNo) {
        try {
            const response = await request.post(this.baseUrl + 'query/route', {
                tracking_number: trackingNumber,
                company: company,
                shipping_no: shippingNo
            })
            
            if (response.data.code === 200) {
                return {
                    success: true,
                    data: response.data.data || {},
                    message: '查询成功'
                }
            } else {
                return {
                    success: false,
                    message: response.data.message || '查询物流信息失败',
                    data: null
                }
            }
        } catch (error) {
            console.error('查询物流路由失败:', error)
            return {
                success: false,
                message: '网络错误，请重试',
                data: null
            }
        }
    }
}

const logisticsService = new LogisticsService()

export default logisticsService
export { LogisticsService }
