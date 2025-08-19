<template>
	<view class="cart-container">
		<!-- 页面头部 -->
		<view class="cart-header">
			<h1 class="page-title">购物车</h1>
			<text class="item-count">{{ cartList.length }}件商品</text>
		</view>

		<!-- 购物车为空状态 -->
		<view v-if="cartList.length === 0" class="empty-cart">
			<view class="empty-icon">��</view>
			<view class="empty-text">购物车空空如也</view>
			<view class="shop-btn" @click="goToShop">去购物</view>
		</view>

		<!-- 购物车列表 -->
		<view v-else class="cart-content">
			<!-- 商品列表 -->
			<view class="cart-items">
				<view v-for="(item, index) in cartList" :key="item.id" class="cart-item"
					:class="{ 'item-selected': item.selected }" @touchstart="startLongPress(item)"
					@touchend="endLongPress" @touchcancel="endLongPress" @mousedown="startLongPress(item)"
					@mouseup="endLongPress" @mouseleave="endLongPress">
					<!-- 选择框 -->
					<view class="item-select" @click="toggleSelectItem(item)">
						<view class="checkbox-custom" :class="{ 'checked': item.selected }">
							<text v-if="item.selected" class="check-icon">✓</text>
						</view>
					</view>

					<!-- 商品信息 -->
					<view class="item-info">
						<view class="item-image">
							<image :src="getItemImage(item)" />
						</view>
						<view class="item-details">
							<h3 class="item-name" :title="item.product_name">{{ item.product_name }}</h3>
							<!-- 显示规格信息 -->
							<view v-if="item.spec_combination_id" class="item-specs">
								<text class="spec-text">{{ getSpecText(item) }}</text>
							</view>
							<view class="item-price">¥{{ formatPrice(item.price) }}</view>
						</view>
					</view>

					<!-- 数量控制 -->
					<view class="quantity-control">
						<button class="quantity-btn minus" @click="decreaseQuantity(item)"
							:disabled="item.quantity <= 1">
							<text>-</text>
						</button>
						<text class="quantity-display">{{ item.quantity }}</text>
						<button class="quantity-btn plus" @click="increaseQuantity(item)"
							:disabled="item.quantity >= item.stock">
							<text>+</text>
						</button>
					</view>


				</view>
			</view>

			<!-- 底部结算区域 -->
			<view class="cart-footer">
				<!-- 全选区域 -->
				<view class="select-all-section" @click="toggleSelectAll">
					<view class="select-all-label">
						<view class="checkbox-custom" :class="{ 'checked': isAllSelected }">
							<text v-if="isAllSelected" class="check-icon">✓</text>
						</view>
						<text class="select-text">全选</text>
					</view>
				</view>

				<!-- 合计信息 -->
				<view class="total-info">
					<text class="total-label">合计：</text>
					<text class="total-amount">¥{{ formatPrice(selectedTotalPrice) }}</text>
					<text class="selected-count">({{ selectedCount }}件)</text>
				</view>

				<!-- 结算按钮 -->
				<view class="checkout-section">
					<view class="checkout-btn" @click="goToPay" :disabled="selectedCount === 0"
						:class="{ 'disabled': selectedCount === 0 }">
						结算 ({{ selectedCount }})
					</view>
				</view>
			</view>
		</view>

		<!-- 加载状态 -->
		<view v-if="loading" class="loading-overlay">
			<view class="loading-spinner"></view>
			<p>加载中...</p>
		</view>
		
		<!-- 确认删除模态框 -->
		<ConfirmModal
			:visible="showConfirmModal"
			:title="confirmModalData.title"
			:content="confirmModalData.content"
			type="delete"
			@confirm="handleConfirmDelete"
			@cancel="handleCancelDelete"
		/>
	</view>
</template>

<script setup>
	import {
		ref,
		computed,
		onMounted
	} from 'vue'
	import {
		cartApi
	} from '@/src/utils/api.js'
	import {
		getUserId
	} from '@/src/utils/auth.js'
	import ConfirmModal from '@/components/ConfirmModal.vue'

	// 响应式数据
	const cartList = ref([])
	const loading = ref(false)
	const longPressTimer = ref(null)
	const longPressItem = ref(null)
	
	// 确认模态框相关
	const showConfirmModal = ref(false)
	const confirmModalData = ref({
		title: '',
		content: '',
		item: null
	})

	// 当前登录用户
	const userInfo = ref({
		user_id: getUserId(),
	})



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
		
		// 使用 uni-app 的导航方法
		uni.navigateTo({
			url: `/pages/checkout/checkout?cart_items=${cartItemIds}`
		})
	}

	// 长按开始
	const startLongPress = (item) => {
		longPressItem.value = item
		longPressTimer.value = setTimeout(() => {
			// 使用自定义确认模态框
			confirmModalData.value = {
				title: '确认删除',
				content: `确定要删除"${item.product_name}"吗？`,
				item: item
			}
			showConfirmModal.value = true
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
	
	// 处理确认模态框确认
	const handleConfirmDelete = () => {
		if (confirmModalData.value.item) {
			removeFromCart(confirmModalData.value.item)
		}
		showConfirmModal.value = false
		confirmModalData.value = { title: '', content: '', item: null }
	}
	
	// 处理确认模态框取消
	const handleCancelDelete = () => {
		showConfirmModal.value = false
		confirmModalData.value = { title: '', content: '', item: null }
	}

	// 去商城
	const goToShop = () => {
		uni.navigateTo({
			url: '/pages/shop/shop'
		})
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
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
		display: flex;
		align-items: center;
		cursor: pointer;
		padding: 8px;
		border-radius: 6px;
		transition: background-color 0.2s;
	}

	.item-select:active {
		background-color: rgba(233, 59, 61, 0.1);
	}

	.checkbox-custom {
		width: 18px;
		height: 18px;
		border: 2px solid #ddd;
		border-radius: 3px;
		position: relative;
		transition: all 0.3s;
		display: flex;
		align-items: center;
		justify-content: center;
		background: white;
	}

	.checkbox-custom.checked {
		background: #e93b3d;
		border-color: #e93b3d;
	}

	.check-icon {
		color: white;
		font-size: 10px;
		font-weight: bold;
		line-height: 1;
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
		padding: 8px;
		border-radius: 6px;
		transition: background-color 0.2s;
	}

	.select-all-section:active {
		background-color: rgba(233, 59, 61, 0.1);
	}

	.select-all-label {
		display: flex;
		align-items: center;
		gap: 8px;
		cursor: pointer;
	}

	.select-all-section .checkbox-custom {
		width: 20px;
		height: 20px;
		border: 2px solid #ddd;
		border-radius: 4px;
		position: relative;
		transition: all 0.3s;
		display: flex;
		align-items: center;
		justify-content: center;
		background: white;
	}

	.select-all-section .checkbox-custom.checked {
		background: #e93b3d;
		border-color: #e93b3d;
	}

	.select-all-section .check-icon {
		color: white;
		font-size: 12px;
		font-weight: bold;
		line-height: 1;
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
		0% {
			transform: rotate(0deg);
		}

		100% {
			transform: rotate(360deg);
		}
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