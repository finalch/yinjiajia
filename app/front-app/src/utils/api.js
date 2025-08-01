import request from './request.js'

// 商品相关API
export const productApi = {
	// 获取商品列表
	getProducts(params = {}) {
		return request({
			url: '/api/app/product/',
			method: 'GET',
			params
		})
	},
	
	// 获取商品详情
	getProductDetail(productId) {
		return request({
			url: `/api/app/product/${productId}`,
			method: 'GET'
		})
	},
	
	// 获取商品分类
	getCategories() {
		return request({
			url: '/api/app/product/categories',
			method: 'GET'
		})
	}
}

// 购物车相关API
export const cartApi = {
	// 获取购物车列表
	getCart(userId = 1) {
		return request({
			url: '/api/app/cart/',
			method: 'GET',
			params: { user_id: userId }
		})
	},
	
	// 添加商品到购物车
	addToCart(data) {
		return request({
			url: '/api/app/cart/',
			method: 'POST',
			data
		})
	},
	
	// 更新购物车商品数量
	updateCartItem(itemId, data) {
		return request({
			url: `/api/app/cart/${itemId}`,
			method: 'PUT',
			data
		})
	},
	
	// 删除购物车商品
	removeCartItem(itemId, userId = 1) {
		return request({
			url: `/api/app/cart/${itemId}`,
			method: 'DELETE',
			params: { user_id: userId }
		})
	},
	
	// 清空购物车
	clearCart(userId = 1) {
		return request({
			url: '/api/app/cart/clear',
			method: 'DELETE',
			params: { user_id: userId }
		})
	}
}

// 订单相关API
export const orderApi = {
	// 获取订单列表
	getOrders(params = {}) {
		return request({
			url: '/api/app/order/',
			method: 'GET',
			params
		})
	},
	
	// 获取订单详情
	getOrderDetail(orderId, userId = 1) {
		return request({
			url: `/api/app/order/${orderId}`,
			method: 'GET',
			params: { user_id: userId }
		})
	},
	
	// 创建订单
	createOrder(data) {
		return request({
			url: '/api/app/order/',
			method: 'POST',
			data
		})
	},
	
	// 取消订单
	cancelOrder(orderId, userId = 1) {
		return request({
			url: `/api/app/order/${orderId}/cancel`,
			method: 'POST',
			params: { user_id: userId }
		})
	}
}

export default {
	productApi,
	cartApi,
	orderApi
} 