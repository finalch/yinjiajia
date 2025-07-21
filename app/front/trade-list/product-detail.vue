<template>
	<view class="product-detail-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-left" @click="goBack">
				<uni-icons type="arrowleft" size="24" color="#333"></uni-icons>
			</view>
			<view class="nav-tabs">
				<view v-for="(tab, index) in tabs" :key="index" class="tab-item"
					:class="{ active: currentTab === index }" @click="switchTab(index)">
					{{ tab }}
				</view>
			</view>
			<view class="nav-right">
				<uni-icons type="more-filled" size="24" color="#333"></uni-icons>
			</view>
		</view>

		<!-- 商品轮播图 -->
		<swiper class="product-swiper" :indicator-dots="true" :autoplay="true" :interval="3000" :duration="500">
			<swiper-item v-for="(image, index) in product.images" :key="index">
				<image class="swiper-image" :src="image" mode="widthFix" @click="previewImage(index)"></image>
			</swiper-item>
		</swiper>

		<!-- 商品基本信息 -->
		<view class="product-info">
			<view class="price-section">
				<text class="current-price">¥{{ product.price }}</text>
				<text class="original-price" v-if="product.original_price">¥{{ product.original_price }}</text>
				<text class="discount-tag" v-if="product.discount">省¥{{ product.discount }}</text>
			</view>
			<view class="title-section">
				<text class="product-title">{{ product.title }}</text>
				<text class="product-subtitle">{{ product.subtitle }}</text>
			</view>
			<view class="tags-section">
				<text v-for="(tag, index) in product.tags" :key="index" class="tag-item">{{ tag }}</text>
			</view>
		</view>

		<!-- 促销信息 -->
		<view class="promotion-section">
			<view class="promotion-item" v-for="(promo, index) in product.promotions" :key="index">
				<text class="promo-tag">{{ promo.tag }}</text>
				<text class="promo-text">{{ promo.text }}</text>
				<uni-icons type="arrowright" size="16" color="#999"></uni-icons>
			</view>
		</view>

		<!-- 商品评价 -->
		<view class="review-section">
			<view class="section-header">
				<text class="section-title">商品评价({{ product.review_count }})</text>
				<text class="more-link">好评率{{ product.positive_rate }}% ></text>
			</view>
			<view class="review-item" v-if="product.top_review">
				<view class="user-info">
					<image class="user-avatar" :src="product.top_review.user.avatar"></image>
					<text class="user-name">{{ product.top_review.user.name }}</text>
				</view>
				<view class="review-content">
					<text>{{ product.top_review.content }}</text>
				</view>
				<view class="review-images" v-if="product.top_review.images.length > 0">
					<image v-for="(img, index) in product.top_review.images" :key="index" :src="img"
						class="review-image" @click="previewReviewImage(index)"></image>
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
				<text class="section-title">商品详情</text>
			</view>
			<rich-text :nodes="product.detail"></rich-text>
		</view>

		<!-- 底部操作栏 -->
		<view class="bottom-bar" v-if="!showPopup">
			<view class="action-btn">
				<view class="btn-icon" @click="goToCustomerService">
					<uni-icons type="chat" size="20" color="#666"></uni-icons>
					<text class="btn-text">客服</text>
				</view>
				<view class="btn-icon" @click="goToShop">
					<uni-icons type="shop" size="20" color="#666"></uni-icons>
					<text class="btn-text">进店</text>
				</view>
				<view class="btn-icon" @click="goToCart">
					<uni-icons type="cart" size="20" color="#666"></uni-icons>
					<text class="btn-text">购物车</text>
					<text v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</text>
				</view>

			</view>
			<view class="main-btn">
				<view class="add-cart-btn" @click="addToCart">加入购物车</view>
				<view class="buy-now-btn" @click="showSpecPopup">立即购买</view>
			</view>
		</view>

		<!-- 规格选择弹出层 -->
		<uni-popup ref="specPopup" type="bottom" :maskBackgroundColor="'rgba(0,0,0,0)'"
			:is-mask-click='true' @change="onPopupChange">
			<view class="spec-popup">
				<view class="popup-header">
					<image class="product-image" :src="product.images[0]" mode="aspectFill"></image>
					<view class="product-info">
						<text class="price">¥{{ product.price }}</text>
						<text class="stock">库存{{ product.stock }}件</text>
						<text class="selected-spec">已选：{{ selectedSpec || '请选择规格' }}</text>
					</view>
					<uni-icons type="close" size="24" color="#999" @click="closeSpecPopup"></uni-icons>
				</view>
				<scroll-view class="spec-content" scroll-y>
					<view class="spec-group" v-for="(group, index) in product.specs" :key="index">
						<text class="spec-name">{{ group.name }}</text>
						<view class="spec-values">
							<text v-for="(value, vIndex) in group.values" :key="vIndex" class="spec-value"
								:class="{ selected: isSpecSelected(group.name, value) }"
								@click="selectSpec(group.name, value)">
								{{ value }}
							</text>
						</view>
					</view>
					<view class="quantity-selector">
						<text class="quantity-label">数量</text>
						<view class="quantity-control">
							<view class="minus-btn" @click="decreaseQuantity">-</view>
							<input class="quantity-input" type="number" v-model="quantity" />
							<view class="plus-btn" @click="increaseQuantity">+</view>
						</view>
					</view>
				</scroll-view>
				<view class="popup-footer">
					<view class="confirm-btn" @click="confirmSpec">确定购买</view>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
	
	export default {
		
		data() {
			return {
				currentTab: 0,
				tabs: ['商品', '评价', '详情', '推荐'],
				product: {
					id: '123456',
					title: 'Apple iPhone 13 (A2634) 128GB 星光色 支持移动联通电信5G 双卡双待',
					subtitle: '【A15仿生芯片】 【6.1英寸超视网膜XDR显示屏】 【双摄系统】',
					price: '5999.00',
					original_price: '6799.00',
					discount: '800',
					stock: 100,
					images: [
						'https://img10.360buyimg.com/mobilecms/s360x360_jfs/t1/210420/8/1074/139501/6140d9d4E0e7b8150/0d1caa6a5c0b890e.jpg',
						'https://img10.360buyimg.com/mobilecms/s360x360_jfs/t1/120559/17/14641/119965/6140d9d4Ea5c4a8b5/0e9c9c7c7e9a8d5c.jpg',
						'https://img10.360buyimg.com/mobilecms/s360x360_jfs/t1/207490/33/1058/139501/6140d9d4Ea8b8a7d1/5a1b4a6e5c0b890e.jpg'
					],
					tags: ['自营', '音加加物流', '七天无理由退货', '以旧换新'],
					promotions: [{
							tag: '券',
							text: '满6000减600元'
						},
						{
							tag: '赠',
							text: '赠价值199元原装充电器'
						},
						{
							tag: '省',
							text: '下单立省800元'
						}
					],
					specs: [{
							name: '颜色',
							values: ['星光色', '午夜色', '蓝色', '粉色', '红色']
						},
						{
							name: '版本',
							values: ['128GB', '256GB', '512GB']
						}
					],
					review_count: '2.5万+',
					positive_rate: '98',
					top_review: {
						user: {
							name: '音加加用户123',
							avatar: 'https://img12.360buyimg.com/img/s80x80_jfs/t1/210420/8/1074/139501/6140d9d4E0e7b8150/0d1caa6a5c0b890e.jpg'
						},
						content: '手机非常好用，运行流畅，拍照效果很棒，电池续航也很给力，非常满意的一次购物体验！',
						images: [
							'https://img10.360buyimg.com/img/s80x80_jfs/t1/210420/8/1074/139501/6140d9d4E0e7b8150/0d1caa6a5c0b890e.jpg',
							'https://img10.360buyimg.com/img/s80x80_jfs/t1/120559/17/14641/119965/6140d9d4Ea5c4a8b5/0e9c9c7c7e9a8d5c.jpg'
						],
						spec: '星光色 128GB',
						time: '2023-05-15'
					},
					detail: `
          <div style="font-size:14px;color:#333;">
            <p><img src="https://img10.360buyimg.com/img/s1000x1000_jfs/t1/210420/8/1074/139501/6140d9d4E0e7b8150/0d1caa6a5c0b890e.jpg" style="width:100%;"/></p>
            <p><strong>商品名称：</strong>Apple iPhone 13</p>
            <p><strong>商品编号：</strong>100012345678</p>
            <p><strong>商品毛重：</strong>0.54kg</p>
            <p><strong>商品产地：</strong>中国大陆</p>
            <p><strong>CPU型号：</strong>A15</p>
            <p><strong>运行内存：</strong>其他</p>
            <p><strong>机身存储：</strong>128GB</p>
            <p><strong>存储卡：</strong>不支持存储卡</p>
            <p><strong>摄像头数量：</strong>后置双摄</p>
            <p><strong>后摄主摄像素：</strong>1200万像素</p>
            <p><strong>前摄主摄像素：</strong>1200万像素</p>
            <p><strong>主屏幕尺寸（英寸）：</strong>6.1英寸</p>
            <p><strong>分辨率：</strong>2532x1170</p>
            <p><strong>屏幕比例：</strong>其他</p>
            <p><strong>屏幕刷新率：</strong>其他</p>
            <p><strong>充电器：</strong>其他</p>
            <p><strong>热点：</strong>人脸识别，无线充电，快速充电，防水防尘，NFC，5G</p>
            <p><strong>操作系统：</strong>iOS</p>
            <p><img src="https://img10.360buyimg.com/img/s1000x1000_jfs/t1/120559/17/14641/119965/6140d9d4Ea5c4a8b5/0e9c9c7c7e9a8d5c.jpg" style="width:100%;"/></p>
          </div>
        `
				},
				selectedSpecs: {},
				selectedSpec: '',
				quantity: 1,
				cartCount: 3,
				showPopup: false,
			}
		},
		onLoad(options) {
			this.productId = options.id
			this.fetchProductDetail()
			this.fetchCartCount()
		},
		methods: {
			goToShop() {
				uni.navigateTo({
					url: `/pages/trade-list/shop?id=${this.product.shop_id || '123'}`
				})
			},
			goToCustomerService() {
				uni.navigateTo({
					url: '/pages/trade-list/customer-service'
				})
			},

			fetchProductDetail() {
				// 实际项目中这里应该是API请求
				// uni.request({
				//   url: 'https://your-api.com/product/detail',
				//   data: { id: this.productId },
				//   success: (res) => {
				//     this.product = res.data.data
				//   }
				// })

				// 这里使用模拟数据
				console.log('加载商品详情:', this.productId)
			},
			fetchCartCount() {
				// 实际项目中这里应该是API请求
				// uni.request({
				//   url: 'https://your-api.com/cart/count',
				//   success: (res) => {
				//     this.cartCount = res.data.data.count
				//   }
				// })

				// 这里使用模拟数据
				this.cartCount = Math.floor(Math.random() * 10)
			},
			goBack() {
				uni.navigateBack()
			},
			switchTab(index) {
				this.currentTab = index
				// 这里可以添加滚动到对应位置的逻辑
			},
			previewImage(index) {
				uni.previewImage({
					current: this.product.images[index],
					urls: this.product.images
				})
			},
			previewReviewImage(index) {
				uni.previewImage({
					current: this.product.top_review.images[index],
					urls: this.product.top_review.images
				})
			},
			showSpecPopup() {
				this.showPopup = true
				this.$refs.specPopup.open()
			},
			closeSpecPopup() {
				this.showPopup = false
				this.$refs.specPopup.close()
			},
			selectSpec(name, value) {
				this.$set(this.selectedSpecs, name, value)
				this.updateSelectedSpecText()
			},
			isSpecSelected(name, value) {
				return this.selectedSpecs[name] === value
			},
			updateSelectedSpecText() {
				const selected = []
				for (const name in this.selectedSpecs) {
					selected.push(this.selectedSpecs[name])
				}
				this.selectedSpec = selected.join(' ')
			},
			increaseQuantity() {
				if (this.quantity < this.product.stock) {
					this.quantity++
				} else {
					uni.showToast({
						title: '已达到最大库存',
						icon: 'none'
					})
				}
			},
			decreaseQuantity() {
				if (this.quantity > 1) {
					this.quantity--
				}
			},


			addToCart() {
				if (Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					this.showSpecPopup()
					return
				}
				
				// 实际项目中这里应该是API请求
				// uni.request({
				//   url: 'https://your-api.com/cart/add',
				//   method: 'POST',
				//   data: {
				//     product_id: this.product.id,
				//     spec: this.selectedSpec,
				//     quantity: this.quantity
				//   },
				//   success: (res) => {
				//     uni.showToast({
				//       title: '已加入购物车'
				//     })
				//     this.fetchCartCount()
				//   }
				// })

				// 这里使用模拟数据
				uni.showToast({
					title: '已加入购物车'
				})
				this.cartCount++
			},
			
			goToCart() {
				uni.navigateTo({
					url: '/pages/trade-list/cartList'
				})
			},

			onPopupChange(e) {
				this.showPopup = e.show;
			},

			confirmSpec() {
				if (Object.keys(this.selectedSpecs).length < this.product.specs.length) {
					uni.showToast({
						title: '请选择完整规格',
						icon: 'none'
					})
					return
				}
				this.closeSpecPopup();
				this.navigateToPayment()
			},

			navigateToPayment() {
				// 实际项目中这里应该是跳转到支付页面
				// 传递商品ID、规格、数量等参数
				// uni.navigateTo({
				// 	url: `/pages/trade-list/payment?product_id=${this.product.id}&
				// 	spec=${encodeURIComponent(this.selectedSpec)}&quantity=${this.quantity}`
				// })
				uni.navigateTo({
					url: `/pages/trade-list/payment?product_id=${this.product.id}&quantity=${this.quantity}`
				})
			}
		}
	}
</script>

<style scoped>
	.product-detail-container {
		padding-bottom: 100px;
		background-color: #f5f5f5;
		z-index: 1;
	}

	/* 导航栏样式 */
	.nav-bar {
		position: fixed;
		top: var(--status-bar-height); /* 适配APP状态栏 */
		left: 0;
		right: 0;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 10px;
		background-color: rgba(255, 255, 255, 0.9);
		
	}

	.nav-left,
	.nav-right {
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
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
	}

	.swiper-image {
		width: 100%;
		height: 100%;
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
		display: block;
	}

	.product-subtitle {
		font-size: 14px;
		color: #666;
		line-height: 1.4;
		display: block;
		margin-top: 5px;
	}

	.tags-section {
		display: flex;
		flex-wrap: wrap;
	}

	.tag-item {
		font-size: 12px;
		color: #e93b3d;
		background-color: #ffeeee;
		border-radius: 2px;
		padding: 2px 5px;
		margin-right: 8px;
		margin-bottom: 5px;
	}

	/* 促销信息样式 */
	.promotion-section {
		background-color: #fff;
		padding: 10px 15px;
		margin-bottom: 10px;
	}

	.promotion-item {
		display: flex;
		align-items: center;
		padding: 5px 0;
	}

	.promo-tag {
		font-size: 12px;
		color: #e93b3d;
		border: 1px solid #e93b3d;
		border-radius: 2px;
		padding: 0 4px;
		margin-right: 8px;
	}

	.promo-text {
		font-size: 14px;
		color: #333;
		flex: 1;
	}

	/* 规格选择样式 */
	.spec-section {
		background-color: #fff;
		padding: 15px;
		display: flex;
		align-items: center;
		margin-bottom: 10px;
	}

	.spec-label {
		font-size: 14px;
		color: #999;
		margin-right: 15px;
	}

	.spec-text {
		font-size: 14px;
		color: #333;
		flex: 1;
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
	}

	.more-link {
		font-size: 14px;
		color: #999;
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
		margin-bottom: 10px;
	}

	.review-image {
		width: 80px;
		height: 80px;
		margin-right: 10px;
		margin-bottom: 10px;
		border-radius: 4px;
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
		/* 调整为3个按钮的宽度 */
		display: flex;
		justify-content: space-around;
		align-items: center;
	}

	.btn-icon {
		display: flex;
		flex-direction: column;
		align-items: center;
		position: relative;
	}

	.btn-text {
		font-size: 12px;
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
		font-size: 16px;
	}

	.add-cart-btn {
		background-color: #ff9500;
	}

	.buy-now-btn {
		background-color: #e93b3d;
	}

	/* 规格弹出层样式 */
	.spec-popup {
		background-color: #fff;
		border-radius: 12px 12px 0 0;
		max-height: 70vh;
		display: flex;
		flex-direction: column;
		z-index: 1000;
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

	.spec-content {
		flex: 1;
		padding: 15px;
		max-height: 50vh;
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
	}

	.spec-value {
		font-size: 14px;
		color: #333;
		border: 1px solid #ddd;
		border-radius: 4px;
		padding: 5px 12px;
		margin-right: 10px;
		margin-bottom: 10px;
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
	}
</style>