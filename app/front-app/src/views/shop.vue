<template>
	<view class="shop-container">
		<!-- 店铺头部 -->
		<view class="shop-header">
			<image class="shop-bg"
				src="https://img10.360buyimg.com/img/s1000x300_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg"
				mode="widthFix"></image>
			<view class="shop-info">
				<image class="shop-logo"
					src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
				</image>
				<view class="shop-meta">
					<text class="shop-name">Apple官方旗舰店</text>
					<view class="shop-rate">
						<uni-rate :value="4.9" :size="14" :readonly="true"></uni-rate>
						<text class="rate-text">4.9</text>
					</view>
					<view class="shop-tags">
						<text class="tag">官方认证</text>
						<text class="tag">品牌直营</text>
						<text class="tag">金牌卖家</text>
					</view>
				</view>
				<view class="follow-btn" @click="toggleFollow">
					<text>{{ isFollowed ? '已关注' : '+ 关注' }}</text>
				</view>
			</view>
		</view>

		<!-- 店铺导航 -->
		<view class="shop-nav">
			<view class="nav-item" @click="switchTab('all')" :class="{ active: currentTab === 'all' }">
				<text>全部商品</text>
			</view>
			<view class="nav-item" @click="switchTab('new')" :class="{ active: currentTab === 'new' }">
				<text>新品上架</text>
			</view>
			<view class="nav-item" @click="switchTab('hot')" :class="{ active: currentTab === 'hot' }">
				<text>热销排行</text>
			</view>
			<view class="nav-item" @click="switchTab('discount')" :class="{ active: currentTab === 'discount' }">
				<text>促销活动</text>
			</view>
		</view>

		<!-- 商品列表 -->
		<scroll-view class="product-list" scroll-y>
			<view class="product-item" v-for="item in products" :key="item.id" @click="goToProduct(item.id)">
				<image class="product-image" :src="item.image" mode="aspectFill"></image>
				<view class="product-info">
					<text class="product-title">{{ item.title }}</text>
					<view class="price-section">
						<text class="current-price">¥{{ item.price }}</text>
						<text class="sales">已售{{ item.sales }}件</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 返回顶部 -->
		<view class="back-top" @click="backToTop" v-show="showBackTop">
			<uni-icons type="arrowup" size="20" color="#666"></uni-icons>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				isFollowed: false,
				currentTab: 'all',
				showBackTop: false,
				products: [{
						id: '1001',
						title: 'Apple iPhone 14 Pro Max (A2896) 256GB 暗紫色 支持移动联通电信5G',
						image: 'https://img10.360buyimg.com/mobilecms/s360x360_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg',
						price: '8999.00',
						sales: '2.5万'
					},
					{
						id: '1002',
						title: 'Apple MacBook Pro 14英寸 M2 Pro芯片 16G 512G 深空灰',
						image: 'https://img10.360buyimg.com/mobilecms/s360x360_jfs/t1/234567/32/12345/67890/5f6789abE12345678/abcdef123456.jpg',
						price: '15999.00',
						sales: '1.2万'
					},
					// 更多商品...
				]
			}
		},
		onLoad(options) {
			this.shopId = options.id
			this.fetchShopData()
		},
		onPageScroll(e) {
			this.showBackTop = e.scrollTop > 300
		},
		methods: {
			fetchShopData() {
				// 实际项目中这里应该是API请求
				console.log('加载店铺数据:', this.shopId)
			},
			toggleFollow() {
				this.isFollowed = !this.isFollowed
				uni.showToast({
					title: this.isFollowed ? '关注成功' : '已取消关注',
					icon: 'none'
				})
			},
			switchTab(tab) {
				this.currentTab = tab
				// 这里可以添加加载对应商品列表的逻辑
			},
			goToProduct(id) {
				uni.navigateTo({
					url: `/pages/product/detail?id=${id}`
				})
			},
			backToTop() {
				uni.pageScrollTo({
					scrollTop: 0,
					duration: 300
				})
			}
		}
	}
</script>

<style scoped>
	.shop-container {
		padding-bottom: 50px;
	}

	.shop-header {
		position: relative;
	}

	.shop-bg {
		width: 100%;
		height: 150px;
	}

	.shop-info {
		position: relative;
		padding: 15px;
		display: flex;
		align-items: center;
		background-color: #fff;
	}

	.shop-logo {
		width: 60px;
		height: 60px;
		border-radius: 5px;
		border: 1px solid #f5f5f5;
		margin-right: 15px;
	}

	.shop-meta {
		flex: 1;
	}

	.shop-name {
		font-size: 16px;
		font-weight: bold;
		margin-bottom: 5px;
		display: block;
	}

	.shop-rate {
		display: flex;
		align-items: center;
		margin-bottom: 5px;
	}

	.rate-text {
		font-size: 12px;
		color: #ff9500;
		margin-left: 5px;
	}

	.shop-tags {
		display: flex;
	}

	.tag {
		font-size: 10px;
		color: #e93b3d;
		border: 1px solid #e93b3d;
		border-radius: 2px;
		padding: 0 4px;
		margin-right: 5px;
	}

	.follow-btn {
		font-size: 12px;
		color: #e93b3d;
		border: 1px solid #e93b3d;
		border-radius: 15px;
		padding: 5px 10px;
	}

	.shop-nav {
		display: flex;
		background-color: #fff;
		margin-bottom: 10px;
	}

	.nav-item {
		flex: 1;
		text-align: center;
		padding: 12px 0;
		font-size: 14px;
		color: #666;
	}

	.nav-item.active {
		color: #e93b3d;
		font-weight: bold;
		position: relative;
	}

	.nav-item.active::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 20px;
		height: 3px;
		background-color: #e93b3d;
		border-radius: 3px;
	}

	.product-list {
		height: calc(100vh - 300px);
	}

	.product-item {
		display: flex;
		padding: 10px;
		background-color: #fff;
		margin-bottom: 10px;
	}

	.product-image {
		width: 100px;
		height: 100px;
		border-radius: 5px;
		margin-right: 10px;
	}

	.product-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: space-between;
	}

	.product-title {
		font-size: 14px;
		line-height: 1.4;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
	}

	.price-section {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.current-price {
		font-size: 16px;
		color: #e93b3d;
		font-weight: bold;
	}

	.sales {
		font-size: 12px;
		color: #999;
	}

	.back-top {
		position: fixed;
		right: 15px;
		bottom: 70px;
		width: 40px;
		height: 40px;
		border-radius: 20px;
		background-color: rgba(255, 255, 255, 0.9);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>