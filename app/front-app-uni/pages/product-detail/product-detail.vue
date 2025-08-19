<template>
	<view class="product-detail-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-left" @click="goBack">
				<text class="nav-icon">‹</text>
			</view>
			<view class="nav-tabs">
				<view v-for="(tab, index) in tabs" :key="index" class="tab-item"
					:class="{ active: currentTab === index }" @click="switchTab(index)">
					{{ tab }}
				</view>
			</view>
			<view class="nav-right">
				<text class="nav-icon" @click="shareProduct">��</text>
			</view>
		</view>

		<!-- 商品轮播图 -->
		<view class="product-swiper">
			<view class="swiper-container">
				<view class="swiper-wrapper" :style="{ transform: `translateX(-${currentImageIndex * 100}%)` }">
					<view v-for="(image, index) in productImages" :key="index" class="swiper-slide">
						<image class="swiper-image" :src="image" @click="previewImage(index)" />
					</view>
				</view>
				<view class="swiper-pagination" v-if="productImages.length > 1">
					<text v-for="(image, index) in productImages" :key="index" class="pagination-dot"
						:class="{ active: currentImageIndex === index }" @click="goToImage(index)"></text>
				</view>
				<view class="swiper-nav" v-if="productImages.length > 1">
					<button class="swiper-btn swiper-prev" @click="prevImage">‹</button>
					<button class="swiper-btn swiper-next" @click="nextImage">›</button>
				</view>
			</view>
		</view>

		<!-- 商品基本信息 -->
		<view class="product-info">
			<view class="price-section">
				<text class="current-price">¥{{ currentPrice }}</text>
				<text class="original-price" v-if="product.original_price && product.original_price > currentPrice">
					¥{{ product.original_price }}
				</text>
				<text class="discount-tag" v-if="product.original_price && product.original_price > currentPrice">
					省¥{{ (product.original_price - currentPrice).toFixed(2) }}
				</text>
			</view>
			<view class="title-section">
				<h1 class="product-title">{{ product.name }}</h1>
				<p class="product-subtitle">{{ product.description }}</p>
			</view>


		</view>

		<!-- 商品规格信息 -->
		<view class="spec-info" v-if="product.has_specs && product.specs">
			<view class="spec-preview single-line" @click="showSpecPopup">
				<text class="spec-label">规格</text>
				<text class="spec-value-line">{{ selectedSpecText || '请选择规格' }}</text>
				<text class="spec-qty">数量 {{ quantity }} 件</text>
				<text class="spec-arrow"><text class="arrow-icon">›</text></text>
			</view>
		</view>

		<!-- 收货地址预览 -->
		<view class="address-preview" @click="selectAddress">
			<view class="address-preview-title">收货地址</view>
			<view class="address-preview-content" v-if="selectedAddress">
				<view class="address-preview-text">
					<view class="address-line">{{ selectedAddress.full_address }}</view>
					<view class="address-estimate">预计3-5日送达</view>
				</view>
				<view class="address-preview-arrow">›</view>
			</view>
			<view class="address-preview-empty" v-else>
				<text>请选择收货地址</text>
				<view class="address-preview-arrow">›</view>
			</view>
		</view>

		<!-- 服务保障独立一行 -->
		<view class="service-guarantee">
			<text class="guarantee-icon">✓</text>
			<text class="guarantee-text">正品保证 · 7天无理由退换</text>
		</view>

		<!-- 商品评价 -->
		<view class="review-section">
			<view class="section-header">
				<h3 class="section-title">商品评价({{ product.review_count || 0 }})</h3>
				<text class="more-link" @click="goToReviews">好评率{{ product.positive_rate || 98 }}% ›</text>
			</view>
			<view class="review-item" v-if="product.top_review">
				<view class="user-info">
					<image class="user-avatar" :src="product.top_review.user.avatar" />
					<text class="user-name">{{ product.top_review.user.name }}</text>
				</view>
				<view class="review-content">
					<p>{{ product.top_review.content }}</p>
				</view>
				<view class="review-images" v-if="product.top_review.images && product.top_review.images.length > 0">
					<image v-for="(img, index) in product.top_review.images" :key="index" :src="img"
						class="review-image" @click="previewReviewImage(index)" />
				</view>
				<view class="review-spec">
					<text>{{ product.top_review.spec }}</text>
					<text class="review-time">{{ product.top_review.time }}</text>
				</view>
			</view>
		</view>

		<!-- 商品详情 -->
		<view class="detail-section">
			<view class="section-header">
				<h3 class="section-title">商品详情</h3>
			</view>
			<view class="detail-content"
				v-html="product.detail || '<p style=\'color: #999; text-align: center; padding: 20px;\'>暂无详情</p>'">
			</view>
		</view>

		<!-- 底部操作栏 -->
		<view class="bottom-bar" v-if="!showPopup">
			<view class="action-btn">
				<view class="btn-icon" @click="goToCustomerService">
					<text class="btn-icon-text">��</text>
					<text class="btn-text">客服</text>
				</view>
				<view class="btn-icon" @click="goToShop">
					<text class="btn-icon-text">��</text>
					<text class="btn-text">进店</text>
				</view>
				<view class="btn-icon" @click="goToCart">
					<text class="btn-icon-text">��</text>
					<text class="btn-text">购物车</text>
					<text v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</text>
				</view>
			</view>
			<view class="main-btn">
				<view class="add-cart-btn" @click="addToCart">加入购物车</view>
				<view class="buy-now-btn" @click="buyNow">立即购买</view>
			</view>
		</view>

		<!-- 规格选择弹出层 -->
		<view v-if="showPopup" class="spec-popup-overlay" @click="closeSpecPopup">
			<view class="spec-popup" @click.stop>
				<view class="popup-header">
					<view class="product-basic-info">
						<image class="product-image" :src="currentImage" alt="商品图片" />
						<view class="product-info">
							<view class="product-title">{{ product.name }}</view>
							<view class="price-info">
								<text class="current-price">¥{{ currentPrice }}</text>
								<text class="original-price"
									v-if="product.original_price && product.original_price > currentPrice">
									¥{{ product.original_price }}
								</text>
							</view>

						</view>
					</view>
					<text class="close-btn" @click="closeSpecPopup">×</text>
				</view>

				<view class="spec-content">

					<!-- 规格选择 -->
					<view class="spec-section" v-if="product.has_specs && product.specs && product.specs.length > 0">
						<view class="section-title">
							<text class="title-text">选择规格</text>
							<text class="title-tip" v-if="!canConfirm">请选择完整规格</text>
						</view>
						<view class="spec-groups">
							<view class="spec-group" v-for="(group, index) in product.specs" :key="index">
								<view class="spec-group-header">
									<text class="spec-name">{{ group.name }}</text>
									<text class="spec-required">*</text>
								</view>
								<view class="spec-values">
									<text v-for="(value, vIndex) in group.values" :key="vIndex" class="spec-value-item"
										:class="{ 
						selected: isSpecSelected(group.name, value),
						disabled: isSpecDisabled(group.name, value)
					  }" @click="selectSpec(group.name, value)">
										<text class="value-text">{{ value }}</text>
										<text class="value-check" v-if="isSpecSelected(group.name, value)">✓</text>
									</text>
								</view>
							</view>
						</view>
						<view class="selected-spec-display" v-if="selectedSpec">
							<view class="selected-header">
								<text class="selected-label">已选规格</text>
								<text class="selected-price"
									v-if="selectedCombination">¥{{ selectedCombination.price }}</text>
							</view>
							<view class="selected-text">{{ selectedSpec }}</view>

						</view>
					</view>

					<!-- 数量选择 -->
					<view class="quantity-section">
						<view class="section-title">
							<text class="title-text">购买数量</text>
						</view>
						<view class="quantity-selector">
							<button class="quantity-btn minus-btn" @click="decreaseQuantity" :disabled="quantity <= 1"
								:class="{ disabled: quantity <= 1 }">
								<text class="btn-icon">-</text>
							</button>
							<view class="quantity-input-wrapper">
								<input class="quantity-input" type="number" v-model.number="quantity" min="1"
									:max="currentStock" @input="validateQuantity" />
							</view>
							<button class="quantity-btn plus-btn" @click="increaseQuantity"
								:disabled="quantity >= currentStock" :class="{ disabled: quantity >= currentStock }">
								<text class="btn-icon">+</text>
							</button>
						</view>
					</view>
				</view>

				<!-- 底部确认区域 -->
				<view class="popup-footer">
					<view class="total-info">
						<text class="total-label">合计：</text>
						<text class="total-price">¥{{ (currentPrice * quantity).toFixed(2) }}</text>
					</view>
					<view class="confirm-btn" @click="confirmDirectBuy"
						:class="{ disabled: !canConfirm || !selectedAddress }">
						立即购买
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		productApi,
		cartApi
	} from '@/src/utils/api.js'
	import {
		getUserId
	} from '@/src/utils/auth.js'
	import request from '@/src/utils/request.js'
	import AddressService from '@/src/services/addressService.js'

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
					detail: '',
					price: 0,
					original_price: 0,
					discount: 0,
					stock: 0,
					images: [],
					tags: [],
					specs: [],
					spec_combinations: [],
					has_specs: false,
					review_count: 0,
					positive_rate: 98,
					top_review: null,
					rating: 0,
					sales_count: 0,
					category_name: '',
					merchant_name: ''
				},
				selectedSpecs: {},
				selectedSpec: '',
				selectedCombination: null,
				quantity: 1,
				cartCount: 0,
				_isFetchingCart: false,
				_lastCartFetchAt: 0,
				showPopup: false,
				loading: false,
				selectedAddress: null // 新增：用于存储选中的收货地址
			}
		},
		computed: {
			// 检查是否可以确认购买
			canConfirm() {
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
					return Object.keys(this.selectedSpecs).length === this.product.specs.length && this.selectedCombination
				}
				return true
			},
			// 确认按钮文本
			confirmButtonText() {
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
					return Object.keys(this.selectedSpecs).length === this.product.specs.length && this
						.selectedCombination ? '确定购买' : '请选择规格'
				}
				return '确定购买'
			},
			// 当前选中规格的价格
			currentPrice() {
				if (this.selectedCombination) {
					return this.selectedCombination.price
				}
				return this.product.price
			},
			// 当前选中规格的库存
			currentStock() {
				if (this.selectedCombination) {
					return this.selectedCombination.stock
				}
				return this.product.stock
			},
			// 当前选中规格的图片
			currentImage() {
				if (this.selectedCombination && this.selectedCombination.image_url) {
					return this.selectedCombination.image_url
				}
				return this.product.images && this.product.images[0] || '/static/default-product.png'
			},
			// 商品轮播图数据
			productImages() {
				return this.product.images || ['https://via.placeholder.com/400x300?text=商品图片']
			},
			// 已选规格文本
			selectedSpecText() {
				const selected = []
				for (const name in this.selectedSpecs) {
					selected.push(this.selectedSpecs[name])
				}
				return selected.join(' ')
			}
		},
		onLoad(options) {
			// 获取页面参数
			if (options.id) {
				this.productId = options.id
			}
			this.fetchProductDetail()
			this.fetchCartCount()
			this.loadAddressInfo()
			// 优先回显本地已选地址
			const cached = AddressService.getSelectedAddress()
			if (cached) {
				this.selectedAddress = cached
			}
		},
		activated() {
			// 当页面重新激活时（比如从地址选择页面返回），重新加载地址信息
			this.loadAddressInfo()
		},
		methods: {
			// 获取商品详情
			async fetchProductDetail() {
				if (!this.productId) return

				this.loading = true
				try {
					const response = await productApi.getProductDetail(this.productId)

					if (response.data.code === 200) {
						const productData = response.data.data

						// 处理图片URL
						if (productData.image_url) {
							const images = productData.image_url.split('$%%$')
							productData.images = images.filter(img => img.trim())
						} else {
							productData.images = []
						}

						// 处理规格数据
						if (productData.has_specs && productData.specs) {
							productData.specs = productData.specs.map(spec => ({
								...spec,
								values: Array.isArray(spec.values) ? spec.values : JSON.parse(spec
									.values || '[]')
							}))
						}

						// 处理规格组合数据
						if (productData.has_specs && productData.spec_combinations) {
							productData.spec_combinations = productData.spec_combinations.map(combo => ({
								...combo,
								spec_values: typeof combo.spec_values === 'string' ?
									JSON.parse(combo.spec_values) : combo.spec_values
							}))
						}

						this.product = productData

						// 调试信息
						console.log('商品详情数据:', this.product)
						console.log('富文本详情:', this.product.detail)

						// 如果有规格，默认选择第一个规格组合
						if (this.product.has_specs && this.product.specs && this.product.specs.length > 0) {
							this.selectDefaultSpecs()
						}
					} else {
						uni.showToast({
							title: response.data.message || '获取商品详情失败',
							icon: 'error'
						})
					}
				} catch (error) {
					console.error('获取商品详情失败:', error)
					uni.showToast({
						title: '网络错误',
						icon: 'error'
					})
				} finally {
					this.loading = false
				}
			},

			// 选择默认规格
			selectDefaultSpecs() {
				if (this.product.specs && this.product.specs.length > 0) {
					// 选择每个规格的第一个值
					this.product.specs.forEach(spec => {
						if (spec.values && spec.values.length > 0) {
							this.selectedSpecs[spec.name] = spec.values[0]
						}
					})
					this.updateSelectedSpecText()
					this.findMatchingCombination()
				}
			},

			// 获取购物车数量
			async fetchCartCount() {
				// 节流：500ms内只请求一次；并发保护
				const now = Date.now()
				if (this._isFetchingCart || (now - this._lastCartFetchAt) < 500) return
				this._isFetchingCart = true
				try {
					const response = await cartApi.getCart(getUserId())
					if (response.data.code === 200) {
						const data = response.data.data
						this.cartCount = (data && (data.item_count || (data.items?.length ?? 0))) || 0
					}
				} catch (error) {
					console.error('获取购物车数量失败:', error)
				} finally {
					this._isFetchingCart = false
					this._lastCartFetchAt = now
				}
			},

			// 加载地址信息
			async loadAddressInfo() {
				// 使用AddressService获取默认地址
				this.selectedAddress = await AddressService.getDefaultAddress(getUserId())
			},

			// 返回上一页
			goBack() {
				uni.navigateBack()
			},

			// 切换标签
			switchTab(index) {
				this.currentTab = index
			},

			// 预览图片
			previewImage(index) {
				// 简单的图片预览，实际项目中可以使用图片预览组件
				console.log('预览图片:', this.productImages[index])
			},

			// 上一张图片
			prevImage() {
				if (this.productImages.length > 1) {
					this.currentImageIndex = this.currentImageIndex > 0 ? this.currentImageIndex - 1 : this.productImages
						.length - 1
				}
			},

			// 下一张图片
			nextImage() {
				if (this.productImages.length > 1) {
					this.currentImageIndex = this.currentImageIndex < this.productImages.length - 1 ? this
						.currentImageIndex + 1 : 0
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

			// 分享商品
			shareProduct() {
				if (this.product.name) {
					uni.showToast({
						title: '商品已分享',
						icon: 'success'
					})
					// 实际项目中可以调用分享API
				}
			},

			// 跳转到评价页面
			goToReviews() {
				uni.navigateTo({
					url: `/pages/reviews/reviews?id=${this.productId}`
				})
			},

			// 显示规格选择弹窗
			showSpecPopup() {
				this.showPopup = true
			},

			// 关闭规格选择弹窗
			closeSpecPopup() {
				this.showPopup = false
			},

			// 直接购买：不弹出弹窗，直接跳转结算
			buyNow() {
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 && !this
					.selectedCombination) {
					uni.showToast({
						title: '请选择完整规格',
						icon: 'error'
					})
					return
				}
				if (this.quantity < 1 || this.quantity > this.currentStock) {
					uni.showToast({
						title: '请选择有效的购买数量',
						icon: 'error'
					})
					return
				}
				if (this.selectedAddress) {
					AddressService.setSelectedAddress(this.selectedAddress)
				}
				const query = {
					product_id: this.product.id,
					quantity: this.quantity
				}
				if (this.selectedCombination) {
					query.spec_combination_id = this.selectedCombination.id
				}
				if (this.selectedAddress && this.selectedAddress.id) {
					query.address_id = this.selectedAddress.id
				}
				// 构建查询字符串
				const queryString = Object.keys(query)
					.map(key => `${key}=${encodeURIComponent(query[key])}`)
					.join('&')
				uni.navigateTo({
					url: `/pages/checkout/checkout?${queryString}`
				})
			},

			// 选择规格
			selectSpec(name, value) {
				// 检查规格是否可用
				if (this.isSpecDisabled(name, value)) {
					return
				}
				this.$set(this.selectedSpecs, name, value)
				this.updateSelectedSpecText()
				this.findMatchingCombination()
			},

			// 检查规格是否已选择
			isSpecSelected(name, value) {
				return this.selectedSpecs[name] === value
			},

			// 检查规格是否禁用
			isSpecDisabled(name, value) {
				// 检查该规格值是否在任何可用的组合中
				if (!this.product.spec_combinations || this.product.spec_combinations.length === 0) {
					return false
				}

				// 检查该规格值是否在当前已选规格下可用
				const currentSpecs = {
					...this.selectedSpecs
				}
				currentSpecs[name] = value

				// 检查是否有匹配的组合
				const hasMatchingCombination = this.product.spec_combinations.some(combo => {
					return this.isSpecCombinationMatch(combo.spec_values, currentSpecs)
				})

				return !hasMatchingCombination
			},

			// 检查规格组合是否匹配
			isSpecCombinationMatch(comboSpecs, selectedSpecs) {
				for (const specName in selectedSpecs) {
					if (comboSpecs[specName] !== selectedSpecs[specName]) {
						return false
					}
				}
				return true
			},

			// 更新已选规格文本
			updateSelectedSpecText() {
				const selected = []
				for (const name in this.selectedSpecs) {
					selected.push(this.selectedSpecs[name])
				}
				this.selectedSpec = selected.join(' ')
			},

			// 查找匹配的规格组合
			findMatchingCombination() {
				if (!this.product.spec_combinations || this.product.spec_combinations.length === 0) {
					this.selectedCombination = null
					return
				}

				// 检查是否所有规格都已选择
				if (Object.keys(this.selectedSpecs).length !== this.product.specs.length) {
					this.selectedCombination = null
					return
				}

				// 查找完全匹配的组合
				const matchingCombo = this.product.spec_combinations.find(combo => {
					return this.isSpecCombinationMatch(combo.spec_values, this.selectedSpecs)
				})

				this.selectedCombination = matchingCombo || null
			},

			// 增加数量
			increaseQuantity() {
				if (this.quantity < this.currentStock) {
					this.quantity++
				} else {
					uni.showToast({
						title: '已达到最大库存',
						icon: 'error'
					})
				}
			},

			// 减少数量
			decreaseQuantity() {
				if (this.quantity > 1) {
					this.quantity--
				}
			},

			// 验证数量输入
			validateQuantity() {
				if (this.quantity < 1) {
					this.quantity = 1
				} else if (this.quantity > this.currentStock) {
					this.quantity = this.currentStock
				}
			},

			// 加入购物车
			async addToCart() {
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 &&
					Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					this.showSpecPopup()
					return
				}

				try {
					const cartData = {
						product_id: this.product.id,
						quantity: this.quantity,
						user_id: getUserId()
					}

					// 如果有规格组合，添加规格组合ID
					if (this.selectedCombination) {
						cartData.spec_combination_id = this.selectedCombination.id
					}

					const response = await cartApi.addToCart(cartData)
					if (response.data.code === 200) {
						// 使用更友好的提示
						uni.showToast({
							title: '已加入购物车',
							icon: 'success'
						})
						this.fetchCartCount()
					} else {
						uni.showToast({
							title: response.data.message || '加入购物车失败',
							icon: 'error'
						})
					}
				} catch (error) {
					console.error('加入购物车失败:', error)
					uni.showToast({
						title: '网络错误，请重试',
						icon: 'error'
					})
				}
			},

			// 跳转到客服页面
			goToCustomerService() {
				uni.navigateTo({
					url: '/pages/customer-service/customer-service'
				})
			},

			// 跳转到店铺页面
			goToShop() {
				uni.navigateTo({
					url: '/pages/shop/shop'
				})
			},

			// 跳转到购物车页面
			goToCart() {
				uni.navigateTo({
					url: '/pages/cart/cart'
				})
			},

			// 确认规格选择
			confirmSpec() {
				// 检查是否选择了完整规格
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 &&
					Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					uni.showToast({
						title: '请选择完整规格',
						icon: 'error'
					})
					return
				}

				// 检查是否有匹配的规格组合
				if (this.product.has_specs && !this.selectedCombination) {
					uni.showToast({
						title: '所选规格组合不可用',
						icon: 'error'
					})
					return
				}

				// 检查数量是否有效
				if (this.quantity < 1 || this.quantity > this.currentStock) {
					uni.showToast({
						title: '请选择有效的购买数量',
						icon: 'error'
					})
					return
				}

				this.closeSpecPopup()
				this.navigateToPayment()
			},

			// 跳转到下单页面
			navigateToPayment() {
				const params = {
					product_id: this.product.id,
					quantity: this.quantity
				}

				// 如果有规格组合，添加规格组合ID
				if (this.selectedCombination) {
					params.spec_combination_id = this.selectedCombination.id
				}

				const queryString = Object.keys(params)
					.map(key => `${key}=${encodeURIComponent(params[key])}`)
					.join('&')

				uni.navigateTo({
					url: `/pages/checkout/checkout?${queryString}`
				})
			},

			// 选择收货地址
			selectAddress() {
				uni.navigateTo({
					url: '/pages/address/address?from=product-detail'
				})
			},

			// 确认立即购买
			confirmDirectBuy() {
				if (!this.selectedAddress) {
					uni.showToast({
						title: '请先选择收货地址',
						icon: 'error'
					})
					return
				}
				if (this.product.has_specs && this.product.specs && this.product.specs.length > 0 &&
					Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					uni.showToast({
						title: '请选择完整规格',
						icon: 'error'
					})
					return
				}
				if (!this.selectedCombination) {
					uni.showToast({
						title: '所选规格组合不可用',
						icon: 'error'
					})
					return
				}
				if (this.quantity < 1 || this.quantity > this.currentStock) {
					uni.showToast({
						title: '请选择有效的购买数量',
						icon: 'error'
					})
					return
				}

				// 使用AddressService保存选中的地址
				AddressService.setSelectedAddress(this.selectedAddress)

				this.closeSpecPopup()

				// 跳转到结算页面
				const query = {
					product_id: this.product.id,
					quantity: this.quantity
				}
				if (this.selectedCombination) {
					query.spec_combination_id = this.selectedCombination.id
				}
				if (this.selectedAddress && this.selectedAddress.id) {
					query.address_id = this.selectedAddress.id
				}
				// 构建查询字符串
				const queryString = Object.keys(query)
					.map(key => `${key}=${encodeURIComponent(query[key])}`)
					.join('&')
				uni.navigateTo({
					url: `/pages/checkout/checkout?${queryString}`
				})
			}
		}
	}
</script>

<style scoped>
	.product-detail-container {
		padding-bottom: 100px;
		background-color: #f8f9fa;
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
		padding: 0 15px;
		background-color: rgba(255, 255, 255, 0.98);
		backdrop-filter: blur(20px);
		z-index: 1000;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
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
		font-size: 18px;
		color: #333;
		cursor: pointer;
		font-weight: 500;
	}

	.nav-tabs {
		flex: 1;
		display: flex;
		justify-content: center;
	}

	.tab-item {
		padding: 0 20px;
		font-size: 15px;
		color: #666;
		height: 44px;
		line-height: 44px;
		position: relative;
		cursor: pointer;
		transition: color 0.3s;
	}

	.tab-item.active {
		color: #ff4757;
		font-weight: 600;
	}

	.tab-item.active::after {
		content: '';
		position: absolute;
		bottom: 8px;
		left: 20px;
		right: 20px;
		height: 3px;
		background: linear-gradient(90deg, #ff4757, #ff6b7a);
		border-radius: 3px;
	}

	/* 商品轮播图样式 */
	.product-swiper {
		padding: 10px 0;
		background-color: #fff;
		margin-top: 44px;
		/* 与导航栏底部对齐 */
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.swiper-container {
		position: relative;
		width: 100%;
		height: 300px;
		/* 轮播图高度 */
		overflow: hidden;
	}

	.swiper-wrapper {
		display: flex;
		transition: transform 0.3s ease-in-out;
	}

	.swiper-slide {
		flex: 0 0 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.swiper-image {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 8px;
		cursor: pointer;
	}

	.swiper-pagination {
		position: absolute;
		bottom: 10px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		gap: 8px;
	}

	.pagination-dot {
		width: 8px;
		height: 8px;
		background-color: #ccc;
		border-radius: 50%;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.pagination-dot.active {
		background-color: #ff4757;
	}

	.swiper-nav {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		display: flex;
		gap: 10px;
		z-index: 10;
	}

	.swiper-btn {
		width: 40px;
		height: 40px;
		background-color: rgba(0, 0, 0, 0.6);
		color: #fff;
		border: none;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: pointer;
		font-size: 20px;
		transition: background-color 0.3s;
	}

	.swiper-btn:hover {
		background-color: rgba(0, 0, 0, 0.8);
	}

	.swiper-prev {
		left: 10px;
	}

	.swiper-next {
		right: 10px;
	}

	/* 商品基本信息样式 */
	.product-info {
		padding: 15px;
		background-color: #fff;
		margin-top: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	/* 收货地址预览 */
	.address-preview {
		margin-top: 10px;
		padding: 12px 16px;
		background: #fff;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		cursor: pointer;
	}

	.address-preview-title {
		font-size: 15px;
		font-weight: 600;
		color: #333;
		margin-bottom: 8px;
	}

	.address-preview-content,
	.address-preview-empty {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.address-preview-text {
		flex: 1;
		min-width: 0;
	}

	.address-line {
		color: #111827;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.address-estimate {
		color: #6b7280;
		margin-top: 4px;
		font-size: 13px;
	}

	.address-preview-arrow {
		color: #cbd5e1;
		padding-left: 8px;
	}

	.service-guarantee {
		margin-top: 8px;
		padding: 10px 16px;
		background: #fff;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.guarantee-icon {
		color: #10b981;
	}

	.guarantee-text {
		color: #111827;
		font-size: 15px;
	}

	.spec-qty {
		color: #6b7280;
		font-size: 13px;
	}

	.price-section {
		display: flex;
		align-items: baseline;
		margin-bottom: 8px;
	}

	.current-price {
		font-size: 24px;
		font-weight: bold;
		color: #ff4757;
	}

	.original-price {
		font-size: 14px;
		color: #999;
		text-decoration: line-through;
		margin-left: 8px;
	}

	.discount-tag {
		font-size: 12px;
		color: #fff;
		background-color: #ff4757;
		padding: 4px 8px;
		border-radius: 4px;
		margin-left: 8px;
	}

	.title-section {
		margin-bottom: 10px;
	}

	.product-title {
		font-size: 20px;
		font-weight: bold;
		color: #333;
		margin-bottom: 5px;
	}

	.product-subtitle {
		font-size: 14px;
		color: #666;
		line-height: 1.5;
	}

	.logistics-info {
		display: flex;
		gap: 15px;
		margin-top: 10px;
		font-size: 13px;
		color: #666;
	}

	.logistics-item {
		display: flex;
		align-items: center;
	}

	.logistics-icon {
		font-size: 16px;
		margin-right: 5px;
	}

	/* 商品规格信息样式 */
	.spec-info {
		padding: 16px 20px;
		background-color: #fff;
		margin-top: 10px;
		border-radius: 12px;
		box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
	}

	.spec-preview {
		display: flex;
		align-items: center;
		justify-content: space-between;
		cursor: pointer;
		transition: all 0.3s ease;
		position: relative;
	}

	.spec-preview.single-line {
		gap: 8px;
	}

	.spec-preview:hover {
		background-color: #f8f9fa;
		border-radius: 8px;
		margin: -4px;
		padding: 4px;
	}

	.spec-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.spec-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.spec-label {
		font-size: 15px;
		color: #333;
		font-weight: 500;
	}

	.spec-price {
		font-size: 16px;
		color: #ff4757;
		font-weight: 600;
	}

	.spec-selection {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.spec-value-line {
		flex: 1;
		min-width: 0;
		color: #666;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		padding: 0 6px;
	}

	.spec-value {
		font-size: 14px;
		color: #666;
	}

	.spec-stock {
		font-size: 12px;
		color: #999;
		background-color: #f0f0f0;
		padding: 2px 6px;
		border-radius: 4px;
	}

	.spec-arrow {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background-color: #f0f0f0;
		transition: all 0.3s ease;
	}

	.spec-preview:hover .spec-arrow {
		background-color: #ff4757;
		transform: scale(1.1);
	}

	.arrow-icon {
		font-size: 16px;
		color: #999;
		transition: color 0.3s ease;
	}

	.spec-preview:hover .arrow-icon {
		color: white;
	}

	/* 商品评价样式 */
	.review-section {
		padding: 15px;
		background-color: #fff;
		margin-top: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.section-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 10px;
	}

	.section-title {
		font-size: 18px;
		font-weight: bold;
		color: #333;
	}

	.more-link {
		font-size: 14px;
		color: #666;
		cursor: pointer;
		text-decoration: none;
		border-bottom: 1px dashed #666;
		transition: border-bottom-color 0.3s;
	}

	.more-link:hover {
		border-bottom-color: #ff4757;
	}

	.review-item {
		padding: 15px;
		border-bottom: 1px solid #eee;
	}

	.review-item:last-child {
		border-bottom: none;
	}

	.user-info {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
	}

	.user-avatar {
		width: 30px;
		height: 30px;
		border-radius: 50%;
		margin-right: 8px;
		object-fit: cover;
	}

	.user-name {
		font-size: 14px;
		color: #333;
		font-weight: 500;
	}

	.review-content {
		font-size: 14px;
		color: #333;
		line-height: 1.6;
		margin-bottom: 10px;
	}

	.review-images {
		display: flex;
		gap: 5px;
		margin-bottom: 10px;
	}

	.review-image {
		width: 50px;
		height: 50px;
		object-fit: cover;
		border-radius: 4px;
	}

	.review-spec {
		font-size: 13px;
		color: #999;
		margin-top: 8px;
	}

	/* 商品详情样式 */
	.detail-section {
		padding: 15px;
		background-color: #fff;
		margin-top: 10px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.detail-content {
		font-size: 14px;
		line-height: 1.6;
		color: #333;
	}

	/* 富文本内容样式 */
	.detail-content img {
		max-width: 100%;
		height: auto;
		margin: 10px 0;
		border-radius: 8px;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.detail-content p {
		margin: 12px 0;
		line-height: 1.8;
	}

	.detail-content h1,
	.detail-content h2,
	.detail-content h3,
	.detail-content h4,
	.detail-content h5,
	.detail-content h6 {
		margin: 20px 0 12px 0;
		font-weight: 600;
		color: #333;
		line-height: 1.4;
	}

	.detail-content h1 {
		font-size: 20px;
	}

	.detail-content h2 {
		font-size: 18px;
	}

	.detail-content h3 {
		font-size: 16px;
	}

	.detail-content h4 {
		font-size: 15px;
	}

	.detail-content h5 {
		font-size: 14px;
	}

	.detail-content h6 {
		font-size: 13px;
	}

	.detail-content ul,
	.detail-content ol {
		margin: 12px 0;
		padding-left: 24px;
	}

	.detail-content li {
		margin: 6px 0;
		line-height: 1.6;
	}

	.detail-content blockquote {
		margin: 16px 0;
		padding: 12px 16px;
		background-color: #f8f9fa;
		border-left: 4px solid #ff4757;
		border-radius: 6px;
		font-style: italic;
		color: #666;
	}

	.detail-content table {
		width: 100%;
		border-collapse: collapse;
		margin: 16px 0;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.detail-content th,
	.detail-content td {
		border: 1px solid #e9ecef;
		padding: 12px;
		text-align: left;
	}

	.detail-content th {
		background-color: #f8f9fa;
		font-weight: 600;
		color: #495057;
	}

	.detail-content code {
		background-color: #f8f9fa;
		padding: 2px 6px;
		border-radius: 4px;
		font-family: 'Courier New', monospace;
		font-size: 13px;
		color: #e83e8c;
	}

	.detail-content pre {
		background-color: #f8f9fa;
		padding: 16px;
		border-radius: 8px;
		overflow-x: auto;
		margin: 16px 0;
		border: 1px solid #e9ecef;
	}

	.detail-content a {
		color: #ff4757;
		text-decoration: none;
		border-bottom: 1px solid transparent;
		transition: border-bottom-color 0.3s;
	}

	.detail-content a:hover {
		border-bottom-color: #ff4757;
	}

	/* 底部操作栏样式 */
	.bottom-bar {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 60px;
		display: flex;
		align-items: center;
		justify-content: space-around;
		background-color: #fff;
		box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.08);
		z-index: 999;
	}

	.action-btn {
		display: flex;
		gap: 20px;
	}

	.btn-icon {
		display: flex;
		flex-direction: column;
		align-items: center;
		cursor: pointer;
		color: #666;
		transition: color 0.3s;
	}

	.btn-icon:hover {
		color: #ff4757;
	}

	.btn-icon-text {
		font-size: 24px;
		margin-bottom: 5px;
	}

	.btn-text {
		font-size: 12px;
		color: #666;
	}

	.cart-badge {
		position: absolute;
		top: -5px;
		right: -5px;
		background-color: #ff4757;
		color: #fff;
		font-size: 10px;
		font-weight: bold;
		padding: 2px 6px;
		border-radius: 10px;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}

	.main-btn {
		display: flex;
		gap: 10px;
	}

	.add-cart-btn,
	.buy-now-btn {
		flex: 1;
		height: 40px;
		line-height: 40px;
		text-align: center;
		border-radius: 20px;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.add-cart-btn {
		background-color: #ff4757;
		color: #fff;
	}

	.add-cart-btn:hover {
		background-color: #e83e8c;
	}

	.buy-now-btn {
		background-color: #4CAF50;
		color: #fff;
	}

	.buy-now-btn:hover {
		background-color: #388e3c;
	}

	/* 规格选择弹出层样式 */
	.spec-popup-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: flex-end;
		justify-content: center;
		z-index: 1001;
		backdrop-filter: blur(4px);
	}

	.spec-popup {
		background-color: #fff;
		border-radius: 20px 20px 0 0;
		box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.15);
		width: 100%;
		max-height: 85vh;
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.popup-header {
		display: flex;
		align-items: center;
		padding: 20px;
		border-bottom: 1px solid #f0f0f0;
		background-color: #fff;
		position: relative;
	}

	.product-basic-info {
		display: flex;
		align-items: center;
		flex: 1;
		gap: 16px;
	}

	.product-image {
		width: 72px;
		height: 72px;
		border-radius: 12px;
		object-fit: cover;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.product-info {
		display: flex;
		flex-direction: column;
		gap: 6px;
		flex: 1;
	}

	.product-title {
		font-size: 16px;
		font-weight: 600;
		color: #333;
		line-height: 1.4;
		line-clamp: 2;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}

	.price-info {
		display: flex;
		align-items: baseline;
		gap: 8px;
	}

	.current-price {
		font-size: 18px;
		font-weight: 600;
		color: #ff4757;
	}

	.original-price {
		font-size: 13px;
		color: #999;
		text-decoration: line-through;
	}

	.stock-info {
		display: none;
	}

	.close-btn {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: 50%;
		background-color: #f0f0f0;
		color: #666;
		cursor: pointer;
		transition: all 0.3s ease;
		font-size: 18px;
		font-weight: bold;
	}

	.close-btn:hover {
		background-color: #ff4757;
		color: white;
		transform: scale(1.1);
	}

	.spec-content {
		padding: 20px;
		flex: 1;
		display: flex;
		flex-direction: column;
		overflow-y: auto;
	}

	.address-section {
		display: none;
	}

	.section-title {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
	}

	.title-text {
		font-size: 16px;
		font-weight: 600;
		color: #333;
	}

	.title-tip {
		font-size: 12px;
		color: #ff4757;
		background-color: #ffece6;
		padding: 4px 8px;
		border-radius: 4px;
		cursor: pointer;
	}

	.address-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		background-color: #f8f9fa;
		border-radius: 8px;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.address-content:hover {
		background-color: #f0f0f0;
	}

	.address-info {
		flex: 1;
	}

	.receiver-info {
		display: flex;
		align-items: center;
		margin-bottom: 4px;
	}

	.receiver-name {
		font-size: 15px;
		color: #333;
		font-weight: 500;
		margin-right: 8px;
	}

	.receiver-phone {
		font-size: 14px;
		color: #666;
	}

	.address-detail {
		font-size: 14px;
		color: #666;
		line-height: 1.4;
	}

	.address-arrow {
		font-size: 18px;
		color: #999;
		transition: transform 0.3s ease;
	}

	.address-content:hover .address-arrow {
		transform: translateX(5px);
	}

	.no-address {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 12px 16px;
		background-color: #f8f9fa;
		border-radius: 8px;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.no-address:hover {
		background-color: #f0f0f0;
	}

	.no-address span {
		font-size: 14px;
		color: #666;
	}

	.logistics-section {
		display: none;
	}

	.logistics-info {
		font-size: 14px;
		color: #666;
		line-height: 1.6;
	}

	.spec-section {
		margin-bottom: 24px;
	}

	.spec-groups {
		display: flex;
		flex-direction: column;
		gap: 20px;
	}

	.spec-group {
		background-color: #f8f9fa;
		border-radius: 8px;
		padding: 16px;
	}

	.spec-group-header {
		display: flex;
		align-items: center;
		margin-bottom: 12px;
	}

	.spec-name {
		font-size: 14px;
		color: #333;
		font-weight: 500;
	}

	.spec-required {
		color: #ff4757;
		margin-left: 4px;
		font-weight: bold;
	}

	.spec-values {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.spec-value-item {
		position: relative;
		font-size: 14px;
		color: #333;
		padding: 8px 16px;
		border: 2px solid #e0e0e0;
		border-radius: 20px;
		background-color: #fff;
		cursor: pointer;
		transition: all 0.3s ease;
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.spec-value-item:hover {
		border-color: #ff4757;
		background-color: #fff5f5;
	}

	.spec-value-item.selected {
		border-color: #ff4757;
		background-color: #ff4757;
		color: white;
		font-weight: 500;
	}

	.spec-value-item.disabled {
		color: #ccc;
		background-color: #f5f5f5;
		border-color: #e0e0e0;
		cursor: not-allowed;
	}

	.value-text {
		flex: 1;
	}

	.value-check {
		font-size: 12px;
		font-weight: bold;
	}

	.selected-spec-display {
		background-color: #f8f9fa;
		border-radius: 8px;
		padding: 16px;
		margin-top: 16px;
	}

	.selected-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 8px;
	}

	.selected-label {
		font-size: 14px;
		color: #666;
		font-weight: 500;
	}

	.selected-price {
		font-size: 16px;
		color: #ff4757;
		font-weight: 600;
	}

	.selected-text {
		font-size: 14px;
		color: #333;
		margin-bottom: 8px;
		line-height: 1.4;
	}

	.selected-stock {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.stock-label {
		font-size: 12px;
		color: #999;
	}

	.stock-value {
		font-size: 12px;
		color: #333;
		font-weight: 500;
	}

	.quantity-section {
		margin-top: 24px;
		padding-top: 20px;
		border-top: 1px solid #eee;
	}

	.quantity-selector {
		display: flex;
		align-items: center;
		gap: 12px;
		margin-top: 12px;
	}

	.quantity-btn {
		width: 36px;
		height: 36px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px solid #e0e0e0;
		border-radius: 50%;
		background-color: #fff;
		color: #333;
		cursor: pointer;
		font-size: 18px;
		font-weight: bold;
		transition: all 0.3s ease;
	}

	.quantity-btn:hover:not(.disabled) {
		border-color: #ff4757;
		background-color: #fff5f5;
	}

	.quantity-btn.disabled {
		color: #ccc;
		background-color: #f5f5f5;
		border-color: #e0e0e0;
		cursor: not-allowed;
	}

	.quantity-input-wrapper {
		position: relative;
		width: 80px;
		height: 36px;
	}

	.quantity-input {
		width: 100%;
		height: 100%;
		text-align: center;
		border: 2px solid #e0e0e0;
		border-radius: 18px;
		font-size: 14px;
		color: #333;
		font-weight: 500;
		background-color: #fff;
	}

	.quantity-input:focus {
		outline: none;
		border-color: #ff4757;
		background-color: #fff5f5;
	}

	.quantity-tip {
		display: none;
	}

	.popup-footer {
		padding: 20px;
		border-top: 1px solid #eee;
		display: flex;
		justify-content: space-between;
		align-items: center;
		background-color: #fff;
		border-radius: 0 0 16px 16px;
	}

	.total-info {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.total-label {
		font-size: 14px;
		color: #666;
	}

	.total-price {
		font-size: 20px;
		font-weight: 600;
		color: #ff4757;
	}

	.confirm-btn {
		padding: 14px 32px;
		background: linear-gradient(135deg, #ff4757, #ff3742);
		color: white;
		border: none;
		border-radius: 25px;
		font-size: 16px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		box-shadow: 0 4px 12px rgba(255, 71, 87, 0.2);
	}

	.confirm-btn:hover:not(:disabled) {
		background: linear-gradient(135deg, #ff3742, #ff2f3a);
		transform: translateY(-2px);
		box-shadow: 0 6px 16px rgba(255, 71, 87, 0.3);
	}

	.confirm-btn:disabled {
		background: #ccc;
		cursor: not-allowed;
		transform: none;
		box-shadow: none;
	}
</style>