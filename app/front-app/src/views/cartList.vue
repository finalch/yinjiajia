<template>
	<div class="cart-container">
		<!-- 页面头部 -->
		<div class="cart-header">
			<h1 class="page-title">购物车</h1>
			<span class="item-count">{{ cartList.length }}件商品</span>
		</div>

		<!-- 购物车为空状态 -->
		<div v-if="cartList.length === 0" class="empty-cart">
			<div class="empty-icon">🛒</div>
			<div class="empty-text">购物车空空如也</div>
			<button class="shop-btn" @click="goToShop">去购物</button>
		</div>

		<!-- 购物车列表 -->
		<div v-else class="cart-content">
			<!-- 商品列表 -->
			<div class="cart-items">
				<div 
					v-for="(item, index) in cartList" 
					:key="item.id" 
					class="cart-item"
					:class="{ 'item-selected': item.selected }"
					@touchstart="startLongPress(item)"
					@touchend="endLongPress"
					@touchcancel="endLongPress"
					@mousedown="startLongPress(item)"
					@mouseup="endLongPress"
					@mouseleave="endLongPress"
				>
					<!-- 选择框 -->
					<div class="item-select">
						<label class="item-checkbox">
							<input 
								type="checkbox" 
								:checked="item.selected" 
								@change="toggleSelectItem(item)"
								class="select-checkbox"
							/>
							<span class="checkbox-custom"></span>
						</label>
					</div>

					<!-- 商品信息 -->
					<div class="item-info">
						<div class="item-image">
							<img :src="getItemImage(item)" :alt="item.product_name" />
						</div>
						<div class="item-details">
							<h3 class="item-name" :title="item.product_name">{{ item.product_name }}</h3>
							<!-- 显示规格信息 -->
							<div v-if="item.spec_combination_id" class="item-specs">
								<span class="spec-text">{{ getSpecText(item) }}</span>
							</div>
							<div class="item-price">¥{{ formatPrice(item.price) }}</div>
						</div>
					</div>

					<!-- 数量控制 -->
					<div class="quantity-control">
						<button 
							class="quantity-btn minus" 
							@click="decreaseQuantity(item)"
							:disabled="item.quantity <= 1"
						>
							<span>-</span>
						</button>
						<span class="quantity-display">{{ item.quantity }}</span>
						<button 
							class="quantity-btn plus" 
							@click="increaseQuantity(item)"
							:disabled="item.quantity >= item.stock"
						>
							<span>+</span>
						</button>
					</div>


				</div>
			</div>

			<!-- 底部结算区域 -->
			<div class="cart-footer">
				<!-- 全选区域 -->
				<div class="select-all-section">
					<label class="select-all-label">
						<input 
							type="checkbox" 
							:checked="isAllSelected" 
							@change="toggleSelectAll"
							class="select-checkbox"
						/>
						<span class="checkbox-custom"></span>
						<span class="select-text">全选</span>
					</label>
				</div>
				
				<!-- 合计信息 -->
				<div class="total-info">
					<span class="total-label">合计：</span>
					<span class="total-amount">¥{{ formatPrice(selectedTotalPrice) }}</span>
					<span class="selected-count">({{ selectedCount }}件)</span>
				</div>
				
				<!-- 结算按钮 -->
				<div class="checkout-section">
					<button 
						class="checkout-btn" 
						@click="goToPay"
						:disabled="selectedCount === 0"
						:class="{ 'disabled': selectedCount === 0 }"
					>
						结算 ({{ selectedCount }})
					</button>
				</div>
			</div>
		</div>

		<!-- 加载状态 -->
		<div v-if="loading" class="loading-overlay">
			<div class="loading-spinner"></div>
			<p>加载中...</p>
		</div>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cartApi } from '@/utils/api.js'

// 响应式数据
const cartList = ref([])
const loading = ref(false)
const longPressTimer = ref(null)
const longPressItem = ref(null)

// 模拟用户信息
const userInfo = ref({
	user_id: 1,
	username: 'test_user'
})

// 路由
const router = useRouter()

// 计算属性
const selectedCount = computed(() => {
	return cartList.value.filter(item => item.selected).length
})

const selectedTotalPrice = computed(() => {
	return cartList.value.reduce((total, item) => {
		return item.selected ? total + item.item_total : total
	}, 0)
})

const isAllSelected = computed(() => {
	return cartList.value.length > 0 && cartList.value.every(item => item.selected)
})

// 方法
const formatPrice = (price) => {
	return Number(price).toFixed(2)
}

// 获取商品图片
const getItemImage = (item) => {
	// 如果有规格组合图片，优先使用规格组合图片
	if (item.spec_combination_id && item.spec_combination_image) {
		return item.spec_combination_image
	}
	// 否则使用商品图片
	return item.product_image || 'https://via.placeholder.com/80x80/f5f5f5/cccccc?text=商品'
}

// 获取规格文本
const getSpecText = (item) => {
	if (!item.spec_combination_id) return ''
	
	// 这里可以根据规格组合ID获取规格文本
	// 暂时返回规格组合ID，后续可以从商品详情中获取完整规格信息
	return `规格: ${item.spec_combination_id}`
}

const showToast = (message) => {
	alert(message)
}

// 获取购物车列表
const fetchCartList = async () => {
	loading.value = true
	try {
		const response = await cartApi.getCart(userInfo.value.user_id)
		if (response.data.code === 200) {
			// 为每个商品添加selected属性
			cartList.value = response.data.data.items.map(item => ({
				...item,
				selected: false
			}))
		} else {
			showToast(response.data.message || '获取购物车失败')
		}
	} catch (error) {
		console.error('获取购物车列表失败:', error)
		showToast('网络错误，请重试')
	} finally {
		loading.value = false
	}
}

// 全选/取消全选
const toggleSelectAll = () => {
	const newSelectState = !isAllSelected.value
	cartList.value = cartList.value.map(item => ({
		...item,
		selected: newSelectState
	}))
}

// 单选/取消单选
const toggleSelectItem = (item) => {
	item.selected = !item.selected
}

// 增加商品数量
const increaseQuantity = async (item) => {
	if (item.quantity >= item.stock) {
		showToast('已达到最大库存')
		return
	}
	
	try {
		const response = await cartApi.updateCartItem(item.id, {
			quantity: item.quantity + 1,
			user_id: userInfo.value.user_id
		})
		
		if (response.data.code === 200) {
			item.quantity++
			item.item_total = item.price * item.quantity
			// showToast('数量更新成功')
		} else {
			showToast(response.data.message || '更新数量失败')
		}
	} catch (error) {
		console.error('更新数量失败:', error)
		showToast('网络错误，请重试')
	}
}

// 减少商品数量
const decreaseQuantity = async (item) => {
	if (item.quantity <= 1) {
		return
	}
	
	try {
		const response = await cartApi.updateCartItem(item.id, {
			quantity: item.quantity - 1,
			user_id: userInfo.value.user_id
		})
		
		if (response.data.code === 200) {
			item.quantity--
			item.item_total = item.price * item.quantity
			// showToast('数量更新成功')
		} else {
			showToast(response.data.message || '更新数量失败')
		}
	} catch (error) {
		console.error('更新数量失败:', error)
		// showToast('网络错误，请重试')
	}
}

// 删除商品
const removeFromCart = async (item) => {
	try {
		const response = await cartApi.removeCartItem(item.id, userInfo.value.user_id)
		
		if (response.data.code === 200) {
			const index = cartList.value.findIndex(cartItem => cartItem.id === item.id)
			if (index > -1) {
				cartList.value.splice(index, 1)
			}
			// showToast('删除成功')
		} else {
			showToast(response.data.message || '删除失败')
		}
	} catch (error) {
		console.error('删除商品失败:', error)
		showToast('网络错误，请重试')
	}
}

// 清空购物车
const clearAllItems = async () => {
	try {
		const response = await cartApi.clearCart(userInfo.value.user_id)
		
		if (response.data.code === 200) {
			cartList.value = []
			// showToast('购物车已清空')
		} else {
			showToast(response.data.message || '清空购物车失败')
		}
	} catch (error) {
		console.error('清空购物车失败:', error)
		showToast('网络错误，请重试')
	}
}

// 去支付
const goToPay = () => {
	const selectedItems = cartList.value.filter(item => item.selected)
	if (selectedItems.length === 0) {
		showToast('请选择至少一个商品')
		return
	}

	const totalAmount = selectedItems.reduce((total, item) => {
		return total + item.item_total
	}, 0)

	const cartItemIds = selectedItems.map(item => item.id).join(',')
  router.push({
    path: '/checkout',
    query: { 
      cart_items: cartItemIds
    }
  })
}

// 长按开始
const startLongPress = (item) => {
	longPressItem.value = item
	longPressTimer.value = setTimeout(() => {
		if (confirm(`确定要删除"${item.product_name}"吗？`)) {
			removeFromCart(item)
		}
	}, 1000) // 1秒长按触发
}

// 长按结束
const endLongPress = () => {
	if (longPressTimer.value) {
		clearTimeout(longPressTimer.value)
		longPressTimer.value = null
	}
	longPressItem.value = null
}

// 去商城
const goToShop = () => {
	router.push('/')
}

// 生命周期
onMounted(() => {
	fetchCartList()
})
</script>

<style scoped>
.cart-container {
	padding: 20px;
	max-width: 1200px;
	margin: 0 auto;
}

/* 页面头部 */
.cart-header {
	background-color: #fff;
	padding: 20px;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	margin-bottom: 20px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.page-title {
	font-size: 24px;
	font-weight: bold;
	color: #333;
	margin: 0;
}

.item-count {
	font-size: 14px;
	color: #666;
}

/* 空购物车状态 */
.empty-cart {
	background-color: #fff;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	padding: 60px 20px;
	text-align: center;
}

.empty-icon {
	font-size: 48px;
	margin-bottom: 20px;
}

.empty-text {
	font-size: 16px;
	color: #666;
	margin-bottom: 30px;
}

.shop-btn {
	background-color: #e93b3d;
	color: white;
	border: none;
	padding: 12px 30px;
	border-radius: 20px;
	font-size: 14px;
	font-weight: bold;
	cursor: pointer;
	transition: background-color 0.3s;
}

.shop-btn:hover {
	background-color: #d63333;
}

/* 购物车内容 */
.cart-content {
	background-color: #fff;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	overflow: hidden;
}

/* 商品列表 */
.cart-items {
	padding: 0;
}

.cart-item {
	display: flex;
	align-items: center;
	padding: 20px;
	border-bottom: 1px solid #eee;
	transition: background-color 0.3s;
	user-select: none;
	cursor: pointer;
}

.cart-item:hover {
	background-color: #f8f9fa;
}

.cart-item:last-child {
	border-bottom: none;
}

.item-selected {
	background-color: #fff3f3;
}

.item-select {
	flex-shrink: 0;
	margin-right: 15px;
}

.item-checkbox {
	display: flex;
	align-items: center;
	cursor: pointer;
}

.select-checkbox {
	display: none;
}

.checkbox-custom {
	width: 18px;
	height: 18px;
	border: 2px solid #ddd;
	border-radius: 3px;
	position: relative;
	transition: all 0.3s;
}

.select-checkbox:checked + .checkbox-custom {
	background: #e93b3d;
	border-color: #e93b3d;
}

.select-checkbox:checked + .checkbox-custom::after {
	content: '✓';
	position: absolute;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	color: white;
	font-size: 10px;
	font-weight: bold;
}

.item-info {
	display: flex;
	align-items: center;
	gap: 15px;
	flex: 1;
	min-width: 0;
}

.item-image {
	width: 80px;
	height: 80px;
	border-radius: 6px;
	overflow: hidden;
	flex-shrink: 0;
}

.item-image img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.item-details {
	flex: 1;
	min-width: 0;
}

.item-name {
	font-size: 13px;
	font-weight: 500;
	color: #333;
	margin: 0 0 6px 0;
	line-height: 1.3;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
	word-break: break-word;
}

.item-price {
	font-size: 16px;
	font-weight: bold;
	color: #e93b3d;
}

.item-specs {
	margin: 4px 0;
}

.spec-text {
	font-size: 12px;
	color: #666;
	background-color: #f5f5f5;
	padding: 2px 6px;
	border-radius: 3px;
}

.quantity-control {
	display: flex;
	align-items: center;
	gap: 6px;
	flex-shrink: 0;
	margin: 0 15px;
}

.quantity-btn {
	width: 24px;
	height: 24px;
	border: 1px solid #ddd;
	background: white;
	border-radius: 3px;
	display: flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	transition: all 0.3s;
	font-size: 12px;
	font-weight: bold;
}

.quantity-btn:hover:not(:disabled) {
	border-color: #e93b3d;
	color: #e93b3d;
}

.quantity-btn:disabled {
	opacity: 0.5;
	cursor: not-allowed;
}

.quantity-display {
	min-width: 25px;
	text-align: center;
	font-size: 12px;
	font-weight: 500;
	color: #333;
}



/* 底部结算区域 */
.cart-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 15px 20px;
	border-top: 1px solid #eee;
	background-color: #f8f9fa;
	min-height: 60px;
}

.select-all-section {
	flex-shrink: 0;
	display: flex;
	align-items: center;
	min-width: 80px;
}

.select-all-label {
	display: flex;
	align-items: center;
	gap: 8px;
	cursor: pointer;
}

.select-text {
	font-size: 14px;
	color: #333;
}

.total-info {
	flex: 1;
	display: flex;
	align-items: center;
	gap: 8px;
	margin: 0 15px;
	justify-content: center;
	white-space: nowrap;
}

.total-label {
	font-size: 14px;
	color: #333;
}

.total-amount {
	font-size: 18px;
	font-weight: bold;
	color: #e93b3d;
}

.selected-count {
	font-size: 12px;
	color: #666;
}

.checkout-section {
	flex-shrink: 0;
	min-width: 100px;
}

.checkout-btn {
	background-color: #e93b3d;
	color: white;
	border: none;
	padding: 12px 30px;
	border-radius: 20px;
	font-size: 14px;
	font-weight: bold;
	cursor: pointer;
	transition: all 0.3s;
}

.checkout-btn:hover:not(.disabled) {
	background-color: #d63333;
}

.checkout-btn.disabled {
	background-color: #ccc;
	cursor: not-allowed;
}

/* 加载状态 */
.loading-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(255, 255, 255, 0.8);
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	z-index: 1000;
}

.loading-spinner {
	width: 40px;
	height: 40px;
	border: 4px solid #f3f3f3;
	border-top: 4px solid #e93b3d;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin-bottom: 10px;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
	.cart-container {
		padding: 15px;
	}
	
	.cart-header {
		padding: 15px;
		margin-bottom: 15px;
	}
	
	.page-title {
		font-size: 20px;
	}
	
	.cart-item {
		padding: 15px;
		flex-wrap: wrap;
	}
	
	.item-info {
		flex: 1;
		min-width: 0;
	}
	
	.item-name {
		font-size: 12px;
	}
	
	.item-price {
		font-size: 13px;
	}
	
	.quantity-control {
		margin: 0 8px;
	}
	
	.quantity-btn {
		width: 22px;
		height: 22px;
		font-size: 11px;
	}
	
	.quantity-display {
		min-width: 22px;
		font-size: 11px;
	}
	
	.cart-footer {
		padding: 15px;
		flex-direction: column;
		gap: 15px;
		min-height: auto;
	}
	
	.select-all-section {
		align-self: flex-start;
		min-width: auto;
	}
	
	.total-info {
		align-items: flex-start;
		margin: 0;
		justify-content: flex-start;
	}
	
	.checkout-section {
		min-width: auto;
	}
	
	.checkout-btn {
		width: 100%;
		padding: 12px 20px;
		font-size: 14px;
	}
}
</style>