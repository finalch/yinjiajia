<template>
	<div class="product-detail-container">
		<!-- 顶部导航栏 -->
		<div class="nav-bar">
			<div class="nav-left" @click="goBack">
				<span class="nav-icon">←</span>
			</div>
			<div class="nav-tabs">
				<div v-for="(tab, index) in tabs" :key="index" class="tab-item"
					:class="{ active: currentTab === index }" @click="switchTab(index)">
					{{ tab }}
				</div>
			</div>
			<div class="nav-right">
				<span class="nav-icon">⋯</span>
			</div>
		</div>

		<!-- 商品轮播图 -->
		<div class="product-swiper">
			<div class="swiper-container">
				<div class="swiper-wrapper" :style="{ transform: `translateX(-${currentImageIndex * 100}%)` }">
					<div v-for="(image, index) in product.images" :key="index" class="swiper-slide">
						<img class="swiper-image" :src="image || 'https://via.placeholder.com/400x300?text=商品图片'" @click="previewImage(index)" />
					</div>
				</div>
				<div class="swiper-pagination" v-if="product.images && product.images.length > 1">
					<span v-for="(image, index) in product.images" :key="index" 
						class="pagination-dot" :class="{ active: currentImageIndex === index }" @click="goToImage(index)"></span>
				</div>
				<div class="swiper-nav" v-if="product.images && product.images.length > 1">
					<button class="swiper-btn swiper-prev" @click="prevImage">‹</button>
					<button class="swiper-btn swiper-next" @click="nextImage">›</button>
				</div>
			</div>
		</div>

		<!-- 商品基本信息 -->
		<div class="product-info">
			<div class="price-section">
				<span class="current-price">¥{{ product.price }}</span>
				<span class="original-price" v-if="product.original_price">¥{{ product.original_price }}</span>
				<span class="discount-tag" v-if="product.discount">省¥{{ product.discount }}</span>
			</div>
			<div class="title-section">
				<h1 class="product-title">{{ product.name }}</h1>
				<p class="product-subtitle">{{ product.description }}</p>
			</div>
			<div class="tags-section">
				<span v-for="(tag, index) in product.tags" :key="index" class="tag-item">{{ tag }}</span>
			</div>
		</div>

		<!-- 商品评价 -->
		<div class="review-section">
			<div class="section-header">
				<h3 class="section-title">商品评价({{ product.review_count || 0 }})</h3>
				<span class="more-link">好评率{{ product.positive_rate || 98 }}% ></span>
			</div>
			<div class="review-item" v-if="product.top_review">
				<div class="user-info">
					<img class="user-avatar" :src="product.top_review.user.avatar" />
					<span class="user-name">{{ product.top_review.user.name }}</span>
				</div>
				<div class="review-content">
					<p>{{ product.top_review.content }}</p>
				</div>
				<div class="review-images" v-if="product.top_review.images && product.top_review.images.length > 0">
					<img v-for="(img, index) in product.top_review.images" :key="index" :src="img"
						class="review-image" @click="previewReviewImage(index)" />
				</div>
				<div class="review-spec">
					<span>{{ product.top_review.spec }}</span>
					<span class="review-time">{{ product.top_review.time }}</span>
				</div>
			</div>
		</div>

		<!-- 商品详情 -->
		<div class="detail-section">
			<div class="section-header">
				<h3 class="section-title">商品详情</h3>
			</div>
			<div class="detail-content" v-html="product.detail"></div>
		</div>

		<!-- 底部操作栏 -->
		<div class="bottom-bar" v-if="!showPopup">
			<div class="action-btn">
				<div class="btn-icon" @click="goToCustomerService">
					<span class="btn-icon-text">💬</span>
					<span class="btn-text">客服</span>
				</div>
				<div class="btn-icon" @click="goToShop">
					<span class="btn-icon-text">🏪</span>
					<span class="btn-text">进店</span>
				</div>
				<div class="btn-icon" @click="goToCart">
					<span class="btn-icon-text">🛒</span>
					<span class="btn-text">购物车</span>
					<span v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</span>
				</div>
			</div>
			<div class="main-btn">
				<div class="add-cart-btn" @click="addToCart">加入购物车</div>
				<div class="buy-now-btn" @click="showSpecPopup">立即购买</div>
			</div>
		</div>

		<!-- 规格选择弹出层 -->
		<div v-if="showPopup" class="spec-popup-overlay" @click="closeSpecPopup">
			<div class="spec-popup" @click.stop>
				<div class="popup-header">
					<img class="product-image" :src="product.images && product.images[0]" />
					<div class="product-info">
						<span class="price">¥{{ product.price }}</span>
						<span class="stock">库存{{ product.stock }}件</span>
						<span class="selected-spec">已选：{{ selectedSpec || '请选择规格' }}</span>
					</div>
					<span class="close-btn" @click="closeSpecPopup">×</span>
				</div>
				<div class="spec-content">
					<div class="spec-group" v-for="(group, index) in product.specs" :key="index">
						<span class="spec-name">{{ group.name }}</span>
						<div class="spec-values">
							<span v-for="(value, vIndex) in group.values" :key="vIndex" class="spec-value"
								:class="{ selected: isSpecSelected(group.name, value) }"
								@click="selectSpec(group.name, value)">
								{{ value }}
							</span>
						</div>
					</div>
					<div class="quantity-selector">
						<span class="quantity-label">数量</span>
						<div class="quantity-control">
							<button class="minus-btn" @click="decreaseQuantity">-</button>
							<input class="quantity-input" type="number" v-model="quantity" />
							<button class="plus-btn" @click="increaseQuantity">+</button>
						</div>
					</div>
				</div>
				<div class="popup-footer">
					<button class="confirm-btn" @click="confirmSpec">确定购买</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
	import { productApi, cartApi } from '@/utils/api.js'
	
	export default {
		name: 'ProductDetail',
		data() {
			return {
				productId: null,
				currentTab: 0,
				currentImageIndex: 0,
				tabs: ['商品', '评价', '详情', '推荐'],
				product: {
					id: '',
					name: '',
					description: '',
					price: 0,
					original_price: 0,
					discount: 0,
					stock: 0,
					images: [],
					tags: [],
					specs: [],
					review_count: 0,
					positive_rate: 98,
					top_review: null,
					detail: '',
					rating: 0,
					sales_count: 0,
					category_name: '',
					merchant_name: ''
				},
				selectedSpecs: {},
				selectedSpec: '',
				quantity: 1,
				cartCount: 0,
				showPopup: false,
				loading: false
			}
		},
		mounted() {
			this.productId = this.$route.params.id
			this.fetchProductDetail()
			this.fetchCartCount()
		},
		methods: {
			// 获取商品详情
			async fetchProductDetail() {
				if (!this.productId) return
				
				this.loading = true
				try {
					const response = await productApi.getProductDetail(this.productId)
					
					if (response.data.code === 200) {
						this.product = response.data.data
					} else {
						alert(response.data.message || '获取商品详情失败')
					}
				} catch (error) {
					console.error('获取商品详情失败:', error)
					alert('网络错误')
				} finally {
					this.loading = false
				}
			},
			
			// 获取购物车数量
			async fetchCartCount() {
				try {
					const response = await cartApi.getCart()
					
					if (response.data.code === 200) {
						this.cartCount = response.data.data.length || 0
					}
				} catch (error) {
					console.error('获取购物车数量失败:', error)
				}
			},
			
			// 返回上一页
			goBack() {
				this.$router.go(-1)
			},
			
			// 切换标签
			switchTab(index) {
				this.currentTab = index
			},
			
			// 预览图片
			previewImage(index) {
				// 简单的图片预览，实际项目中可以使用图片预览组件
				console.log('预览图片:', this.product.images[index])
			},
			
			// 上一张图片
			prevImage() {
				if (this.product.images && this.product.images.length > 1) {
					this.currentImageIndex = this.currentImageIndex > 0 ? this.currentImageIndex - 1 : this.product.images.length - 1
				}
			},
			
			// 下一张图片
			nextImage() {
				if (this.product.images && this.product.images.length > 1) {
					this.currentImageIndex = this.currentImageIndex < this.product.images.length - 1 ? this.currentImageIndex + 1 : 0
				}
			},
			
			// 跳转到指定图片
			goToImage(index) {
				this.currentImageIndex = index
			},
			
			// 预览评价图片
			previewReviewImage(index) {
				if (this.product.top_review && this.product.top_review.images) {
					console.log('预览评价图片:', this.product.top_review.images[index])
				}
			},
			
			// 显示规格选择弹窗
			showSpecPopup() {
				this.showPopup = true
			},
			
			// 关闭规格选择弹窗
			closeSpecPopup() {
				this.showPopup = false
			},
			
			// 选择规格
			selectSpec(name, value) {
				this.$set(this.selectedSpecs, name, value)
				this.updateSelectedSpecText()
			},
			
			// 检查规格是否已选择
			isSpecSelected(name, value) {
				return this.selectedSpecs[name] === value
			},
			
			// 更新已选规格文本
			updateSelectedSpecText() {
				const selected = []
				for (const name in this.selectedSpecs) {
					selected.push(this.selectedSpecs[name])
				}
				this.selectedSpec = selected.join(' ')
			},
			
			// 增加数量
			increaseQuantity() {
				if (this.quantity < this.product.stock) {
					this.quantity++
				} else {
					alert('已达到最大库存')
				}
			},
			
			// 减少数量
			decreaseQuantity() {
				if (this.quantity > 1) {
					this.quantity--
				}
			},
			
			// 加入购物车
			async addToCart() {
				if (this.product.specs && this.product.specs.length > 0 && 
					Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					this.showSpecPopup()
					return
				}
				
				try {
					const response = await cartApi.addToCart({
						product_id: this.product.id,
						quantity: this.quantity,
						spec: this.selectedSpec
					})
					
					if (response.data.code === 200) {
						alert('已加入购物车')
						this.fetchCartCount()
					} else {
						alert(response.data.message || '加入购物车失败')
					}
				} catch (error) {
					console.error('加入购物车失败:', error)
					alert('网络错误')
				}
			},
			
			// 跳转到客服页面
			goToCustomerService() {
				this.$router.push('/customer-service')
			},
			
			// 跳转到店铺页面
			goToShop() {
				this.$router.push('/shop')
			},
			
			// 跳转到购物车页面
			goToCart() {
				this.$router.push('/cart')
			},
			
			// 确认规格选择
			confirmSpec() {
				if (this.product.specs && this.product.specs.length > 0 && 
					Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					alert('请选择完整规格')
					return
				}
				this.closeSpecPopup()
				this.navigateToPayment()
			},
			
			// 跳转到支付页面
			navigateToPayment() {
				const params = {
					product_id: this.product.id,
					quantity: this.quantity
				}
				if (this.selectedSpec) {
					params.spec = this.selectedSpec
				}
				
				const queryString = Object.keys(params)
					.map(key => `${key}=${encodeURIComponent(params[key])}`)
					.join('&')
				
				this.$router.push(`/payment?${queryString}`)
			}
		}
	}
</script>

<style scoped>
	.product-detail-container {
		padding-bottom: 100px;
		background-color: #f5f5f5;
		min-height: 100vh;
	}

	/* 导航栏样式 */
	.nav-bar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 10px;
		background-color: rgba(255, 255, 255, 0.95);
		backdrop-filter: blur(10px);
		z-index: 1000;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}

	.nav-left,
	.nav-right {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.nav-icon {
		font-size: 20px;
		color: #333;
		cursor: pointer;
	}

	.nav-tabs {
		flex: 1;
		display: flex;
		justify-content: center;
	}

	.tab-item {
		padding: 0 15px;
		font-size: 15px;
		color: #666;
		height: 44px;
		line-height: 44px;
		position: relative;
		cursor: pointer;
	}

	.tab-item.active {
		color: #e93b3d;
		font-weight: bold;
	}

	.tab-item.active::after {
		content: '';
		position: absolute;
		bottom: 5px;
		left: 15px;
		right: 15px;
		height: 3px;
		background-color: #e93b3d;
		border-radius: 3px;
	}

	/* 商品轮播图样式 */
	.product-swiper {
		width: 100%;
		height: 375px;
		margin-top: 44px;
		position: relative;
		overflow: hidden;
	}

	.swiper-container {
		width: 100%;
		height: 100%;
		position: relative;
	}

	.swiper-wrapper {
		display: flex;
		width: 100%;
		height: 100%;
		transition: transform 0.3s ease;
	}

	.swiper-slide {
		flex: 0 0 100%;
		width: 100%;
		height: 100%;
	}

	.swiper-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
		cursor: pointer;
	}

	.swiper-pagination {
		position: absolute;
		bottom: 20px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		gap: 8px;
		z-index: 10;
	}

	.pagination-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: rgba(255, 255, 255, 0.5);
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.pagination-dot:hover {
		background-color: rgba(255, 255, 255, 0.8);
	}

	.pagination-dot.active {
		background-color: #fff;
	}

	.swiper-nav {
		position: absolute;
		top: 50%;
		left: 0;
		right: 0;
		transform: translateY(-50%);
		display: flex;
		justify-content: space-between;
		padding: 0 15px;
		z-index: 10;
	}

	.swiper-btn {
		width: 40px;
		height: 40px;
		border-radius: 50%;
		background-color: rgba(0, 0, 0, 0.3);
		color: white;
		border: none;
		font-size: 20px;
		cursor: pointer;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background-color 0.3s;
	}

	.swiper-btn:hover {
		background-color: rgba(0, 0, 0, 0.5);
	}

	.swiper-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	/* 商品信息样式 */
	.product-info {
		padding: 15px;
		background-color: #fff;
		margin-bottom: 10px;
	}

	.price-section {
		display: flex;
		align-items: flex-end;
		margin-bottom: 10px;
	}

	.current-price {
		font-size: 24px;
		color: #e93b3d;
		font-weight: bold;
		margin-right: 8px;
	}

	.original-price {
		font-size: 14px;
		color: #999;
		text-decoration: line-through;
		margin-right: 10px;
	}

	.discount-tag {
		font-size: 12px;
		color: #e93b3d;
		border: 1px solid #e93b3d;
		border-radius: 2px;
		padding: 0 4px;
	}

	.title-section {
		margin-bottom: 10px;
	}

	.product-title {
		font-size: 16px;
		font-weight: bold;
		line-height: 1.4;
		margin: 0 0 5px 0;
		color: #333;
	}

	.product-subtitle {
		font-size: 14px;
		color: #666;
		line-height: 1.4;
		margin: 0;
	}

	.tags-section {
		display: flex;
		flex-wrap: wrap;
		gap: 5px;
	}

	.tag-item {
		font-size: 12px;
		color: #e93b3d;
		background-color: #ffeeee;
		border-radius: 2px;
		padding: 2px 5px;
	}

	/* 评价样式 */
	.review-section {
		background-color: #fff;
		padding: 15px;
		margin-bottom: 10px;
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 15px;
	}

	.section-title {
		font-size: 16px;
		font-weight: bold;
		margin: 0;
		color: #333;
	}

	.more-link {
		font-size: 14px;
		color: #999;
		cursor: pointer;
	}

	.review-item {
		padding-top: 10px;
	}

	.user-info {
		display: flex;
		align-items: center;
		margin-bottom: 10px;
	}

	.user-avatar {
		width: 30px;
		height: 30px;
		border-radius: 15px;
		margin-right: 10px;
		object-fit: cover;
	}

	.user-name {
		font-size: 14px;
		color: #666;
	}

	.review-content {
		font-size: 14px;
		color: #333;
		line-height: 1.5;
		margin-bottom: 10px;
	}

	.review-images {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 10px;
	}

	.review-image {
		width: 80px;
		height: 80px;
		border-radius: 4px;
		object-fit: cover;
		cursor: pointer;
	}

	.review-spec {
		display: flex;
		justify-content: space-between;
		font-size: 12px;
		color: #999;
	}

	.review-time {
		color: #999;
	}

	/* 详情样式 */
	.detail-section {
		background-color: #fff;
		padding: 15px;
	}

	.detail-content {
		font-size: 14px;
		line-height: 1.6;
		color: #333;
	}

	.detail-content img {
		max-width: 100%;
		height: auto;
	}

	/* 底部操作栏样式 */
	.bottom-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 50px;
		background-color: #fff;
		display: flex;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		z-index: 999;
	}

	.action-btn {
		width: 45%;
		display: flex;
		justify-content: space-around;
		align-items: center;
	}

	.btn-icon {
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
		cursor: pointer;
	}

	.btn-icon-text {
		font-size: 16px;
		margin-bottom: 2px;
	}

	.btn-text {
		font-size: 12px;
		color: #666;
	}

	.cart-badge {
		position: absolute;
		top: -5px;
		right: -5px;
		background-color: #e93b3d;
		color: white;
		border-radius: 10px;
		font-size: 10px;
		min-width: 16px;
		height: 16px;
		line-height: 16px;
		text-align: center;
		padding: 0 4px;
	}

	.main-btn {
		flex: 1;
		display: flex;
	}

	.add-cart-btn,
	.buy-now-btn {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: center;
		color: white;
		font-size: 16px;
		cursor: pointer;
		border: none;
	}

	.add-cart-btn {
		background-color: #ff9500;
	}

	.buy-now-btn {
		background-color: #e93b3d;
	}

	/* 规格弹出层样式 */
	.spec-popup-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.5);
		z-index: 2000;
		display: flex;
		align-items: flex-end;
	}

	.spec-popup {
		background-color: #fff;
		border-radius: 12px 12px 0 0;
		max-height: 70vh;
		width: 100%;
		display: flex;
		flex-direction: column;
	}

	.popup-header {
		padding: 15px;
		display: flex;
		position: relative;
		border-bottom: 1px solid #f5f5f5;
	}

	.product-image {
		width: 80px;
		height: 80px;
		border-radius: 4px;
		margin-right: 10px;
		object-fit: cover;
	}

	.product-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

	.price {
		font-size: 18px;
		color: #e93b3d;
		font-weight: bold;
	}

	.stock {
		font-size: 14px;
		color: #999;
	}

	.selected-spec {
		font-size: 14px;
		color: #333;
	}

	.close-btn {
		position: absolute;
		top: 15px;
		right: 15px;
		font-size: 24px;
		color: #999;
		cursor: pointer;
	}

	.spec-content {
		flex: 1;
		padding: 15px;
		max-height: 50vh;
		overflow-y: auto;
	}

	.spec-group {
		margin-bottom: 20px;
	}

	.spec-name {
		font-size: 14px;
		color: #666;
		margin-bottom: 10px;
		display: block;
	}

	.spec-values {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
	}

	.spec-value {
		font-size: 14px;
		color: #333;
		border: 1px solid #ddd;
		border-radius: 4px;
		padding: 5px 12px;
		cursor: pointer;
		transition: all 0.3s;
	}

	.spec-value:hover {
		border-color: #e93b3d;
	}

	.spec-value.selected {
		color: #e93b3d;
		border-color: #e93b3d;
		background-color: #ffeeee;
	}

	.quantity-selector {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-top: 20px;
	}

	.quantity-label {
		font-size: 14px;
		color: #666;
	}

	.quantity-control {
		display: flex;
		align-items: center;
	}

	.quantity-input {
		width: 50px;
		height: 30px;
		border: 1px solid #ddd;
		border-radius: 4px;
		text-align: center;
		margin: 0 5px;
	}

	.minus-btn,
	.plus-btn {
		width: 30px;
		height: 30px;
		border: 1px solid #ddd;
		border-radius: 4px;
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 16px;
		cursor: pointer;
		transition: all 0.3s;
	}

	.minus-btn:hover,
	.plus-btn:hover {
		background-color: #f5f5f5;
	}

	.popup-footer {
		padding: 15px;
		border-top: 1px solid #f5f5f5;
	}

	.confirm-btn {
		background-color: #e93b3d;
		color: white;
		height: 44px;
		border-radius: 22px;
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 16px;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.confirm-btn:hover {
		background-color: #d63333;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.product-detail-container {
			padding-bottom: 80px;
		}

		.nav-bar {
			height: 40px;
		}

		.nav-left,
		.nav-right {
			width: 40px;
			height: 40px;
		}

		.tab-item {
			padding: 0 12px;
			font-size: 14px;
			height: 40px;
			line-height: 40px;
		}

		.product-swiper {
			height: 300px;
			margin-top: 40px;
		}

		.product-info {
			padding: 12px;
		}

		.current-price {
			font-size: 20px;
		}

		.product-title {
			font-size: 14px;
		}

		.product-subtitle {
			font-size: 12px;
		}

		.bottom-bar {
			height: 45px;
		}

		.btn-text {
			font-size: 11px;
		}

		.add-cart-btn,
		.buy-now-btn {
			font-size: 14px;
		}

		.spec-popup {
			max-height: 60vh;
		}

		.spec-content {
			max-height: 40vh;
		}
	}

	@media (max-width: 480px) {
		.product-swiper {
			height: 250px;
		}

		.product-info {
			padding: 10px;
		}

		.current-price {
			font-size: 18px;
		}

		.product-title {
			font-size: 13px;
		}

		.promotion-section,
		.review-section,
		.detail-section {
			padding: 10px 12px;
		}

		.section-title {
			font-size: 14px;
		}

		.bottom-bar {
			height: 40px;
		}

		.btn-text {
			font-size: 10px;
		}

		.add-cart-btn,
		.buy-now-btn {
			font-size: 13px;
		}
	}

	/* 加载状态样式 */
	.loading-container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 200px;
	}

	.loading-text {
		color: #999;
		font-size: 14px;
	}

	/* 错误状态样式 */
	.error-container {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 200px;
		padding: 20px;
	}

	.error-icon {
		font-size: 48px;
		color: #999;
		margin-bottom: 10px;
	}

	.error-text {
		color: #999;
		font-size: 14px;
		text-align: center;
	}

	.retry-btn {
		margin-top: 15px;
		padding: 8px 16px;
		background-color: #e93b3d;
		color: white;
		border: none;
		border-radius: 4px;
		font-size: 14px;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.retry-btn:hover {
		background-color: #d63333;
	}

	/* 图片预览样式 */
	.image-preview {
		cursor: pointer;
		transition: transform 0.3s;
	}

	.image-preview:hover {
		transform: scale(1.05);
	}

	/* 滚动条样式 */
	.spec-content::-webkit-scrollbar {
		width: 4px;
	}

	.spec-content::-webkit-scrollbar-track {
		background: #f1f1f1;
		border-radius: 2px;
	}

	.spec-content::-webkit-scrollbar-thumb {
		background: #c1c1c1;
		border-radius: 2px;
	}

	.spec-content::-webkit-scrollbar-thumb:hover {
		background: #a8a8a8;
	}

	/* 动画效果 */
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.product-info,
	.promotion-section,
	.review-section,
	.detail-section {
		animation: fadeIn 0.5s ease-out;
	}

	/* 商品标签样式优化 */
	.tag-item {
		font-size: 11px;
		color: #e93b3d;
		background-color: #ffeeee;
		border-radius: 3px;
		padding: 3px 6px;
		margin-right: 6px;
		margin-bottom: 4px;
		display: inline-block;
	}

	/* 促销信息样式优化 */
	.promotion-item {
		display: flex;
		align-items: center;
		padding: 6px 0;
		border-bottom: 1px solid #f5f5f5;
	}

	.promotion-item:last-child {
		border-bottom: none;
	}

	.promo-tag {
		font-size: 11px;
		color: #e93b3d;
		border: 1px solid #e93b3d;
		border-radius: 3px;
		padding: 1px 4px;
		margin-right: 8px;
		flex-shrink: 0;
	}

	.promo-text {
		font-size: 13px;
		color: #333;
		flex: 1;
		line-height: 1.4;
	}

	/* 评价样式优化 */
	.review-item {
		padding-top: 12px;
		border-top: 1px solid #f5f5f5;
	}

	.review-item:first-child {
		border-top: none;
		padding-top: 0;
	}

	.user-info {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}

	.user-avatar {
		width: 28px;
		height: 28px;
		border-radius: 14px;
		margin-right: 8px;
		object-fit: cover;
	}

	.user-name {
		font-size: 13px;
		color: #666;
	}

	.review-content {
		font-size: 13px;
		color: #333;
		line-height: 1.5;
		margin-bottom: 8px;
	}

	.review-images {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		margin-bottom: 8px;
	}

	.review-image {
		width: 70px;
		height: 70px;
		border-radius: 4px;
		object-fit: cover;
		cursor: pointer;
		transition: transform 0.3s;
	}

	.review-image:hover {
		transform: scale(1.05);
	}

	.review-spec {
		display: flex;
		justify-content: space-between;
		font-size: 11px;
		color: #999;
	}

	.review-time {
		color: #999;
	}

	/* 底部操作栏优化 */
	.bottom-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 50px;
		background-color: #fff;
		display: flex;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		z-index: 999;
	}

	.action-btn {
		width: 45%;
		display: flex;
		justify-content: space-around;
		align-items: center;
	}

	.btn-icon {
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
		cursor: pointer;
		transition: opacity 0.3s;
	}

	.btn-icon:hover {
		opacity: 0.8;
	}

	.btn-text {
		font-size: 11px;
		color: #666;
		margin-top: 2px;
	}

	.cart-badge {
		position: absolute;
		top: -5px;
		right: -5px;
		background-color: #e93b3d;
		color: white;
		border-radius: 10px;
		font-size: 10px;
		min-width: 16px;
		height: 16px;
		line-height: 16px;
		text-align: center;
		padding: 0 4px;
	}

	.main-btn {
		flex: 1;
		display: flex;
	}

	.add-cart-btn,
	.buy-now-btn {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: center;
		color: white;
		font-size: 15px;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.add-cart-btn {
		background-color: #ff9500;
	}

	.add-cart-btn:hover {
		background-color: #e6850e;
	}

	.buy-now-btn {
		background-color: #e93b3d;
	}

	.buy-now-btn:hover {
		background-color: #d63333;
	}
	</style>