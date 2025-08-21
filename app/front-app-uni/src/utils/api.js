import request from './request.js'

// 导出request供其他文件使用
export {
	request
}

// 商品相关API
export const productApi = {
	// 获取商品列表
	getProducts(params = {}) {
		return request.get('/api/app/product/', params)
	},

	// 获取商品详情
	getProductDetail(productId) {
		return request.get(`/api/app/product/${productId}`)
	},

	// 获取商品分组
	getGroups() {
		return request.get('/api/app/product/groups')
	}
}

// 购物车相关API
export const cartApi = {
	// 获取购物车列表
	getCart(userId = 1) {
		return request.get('/api/app/cart/', {
			user_id: userId
		})
	},

	// 添加商品到购物车
	addToCart(data) {
		return request.post('/api/app/cart/', data)
	},
	// 快捷加入购物车（商品页默认选择第一个规格）
	quickAddToCart({
		productId,
		userId = 1,
		quantity = 1,
		specCombinationId
	}) {
		const payload = {
			user_id: userId,
			product_id: productId,
			quantity
		}
		if (specCombinationId) payload.spec_combination_id = specCombinationId
		return request.post('/api/app/cart/', payload)
	},

	// 更新购物车商品数量
	updateCartItem(itemId, data) {
		return request.put(`/api/app/cart/${itemId}`, data)
	},

	// 删除购物车商品
	removeCartItem(itemId, userId = 1) {
		return request.delete(`/api/app/cart/${itemId}?user_id=${userId}`)
	},

	// 清空购物车
	clearCart(userId = 1) {
		return request.delete(`/api/app/cart/clear?user_id=${userId}`)
	}
}

// 订单相关API
export const orderApi = {
	// 获取订单列表
	getOrders(params = {}) {
		return request.get('/api/app/order/', params)
	},

	// 获取订单详情
	getOrderDetail(orderId, userId = 1) {
		return request.get(`/api/app/order/${orderId}`, {
			user_id: userId
		})
	},

	// 创建订单
	createOrder(data) {
		return request.post('/api/app/order/', data)
	},

	// 取消订单
	cancelOrder(orderId, userId = 1) {
		return request.post(`/api/app/order/${orderId}/cancel`, {
			user_id: userId
		})
	}
}

export default {
	productApi,
	cartApi,
	orderApi
}

// 认证API
export const authApi = {
	register({
		phone,
		password
	}) {
		return request.post('/api/app/auth/register', {
			phone,
			password
		})
	},
	login({
		phone,
		password
	}) {
		return request.post('/api/app/auth/login', {
			phone,
			password
		})
	},
	validate(token) {
		return request.get('/api/app/auth/validate', {
			token
		})
	}
}

export const addressApi = {
	defalut_address() {
		return request.get('/api/app/address/default')
	}
}