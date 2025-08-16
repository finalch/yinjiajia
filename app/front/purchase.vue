<template>
	<view class="uni-status-bar"></view>
	<view class="shop-container">
		<!-- 顶部搜索栏和购物车 -->
		<view class="top-bar">
			<view class="search-bar" @click="goToSearch">
				<uni-icons type="search" size="18" color="#999"></uni-icons>
				<text class="search-text">搜索商品</text>
			</view>
			<view class="cart-icon" @click="goToCart">
				<uni-icons type="cart" size="24" color="#ff2442"></uni-icons>
				<text v-if="cartCount > 0" class="cart-badge">{{ cartCount }}</text>
			</view>
		</view>

		<!-- 分组标签栏 -->
		<scroll-view class="group-tabs" scroll-x>
			<view v-for="(group, index) in groups" :key="group.id" class="tab-item"
				:class="{ active: activeGroup === index }" @click="changeGroup(index)">
				{{ group.name }}
			</view>
		</scroll-view>

		<!-- 商品瀑布流 -->
		<view class="waterfall-container">
			<view class="waterfall-column">
				<view v-for="(item, index) in leftColumnItems" :key="item.id" class="product-item"
					@click="goToDetail(item.id)">
					<image class="product-image" :src="item.image" mode="widthFix"></image>
					<view class="product-info">
						<text class="product-title">{{ item.title }}</text>
						<view class="price-section">
							<text class="product-price">¥{{ item.price }}</text>
							<text class="original-price" v-if="item.original_price">¥{{ item.original_price }}</text>
						</view>
						<view class="sales-info">
							<text>已售{{ item.sales }}件</text>
						</view>
					</view>
				</view>
			</view>
			<view class="waterfall-column">
				<view v-for="(item, index) in rightColumnItems" :key="item.id" class="product-item"
					@click="goToDetail(item.id)">
					<image class="product-image" :src="item.image" mode="widthFix"></image>
					<view class="product-info">
						<text class="product-title">{{ item.title }}</text>
						<view class="price-section">
							<text class="product-price">¥{{ item.price }}</text>
							<text class="original-price" v-if="item.original_price">¥{{ item.original_price }}</text>
						</view>
						<view class="sales-info">
							<text>已售{{ item.sales }}件</text>
						</view>
					</view>
				</view>
			</view>
		</view>

		<!-- 加载更多提示 -->
		<view class="load-more" v-if="loading">
			<text>加载中...</text>
		</view>
		<view class="load-more" v-else-if="noMore">
			<text>没有更多了~</text>
		</view>
		<custom-tabbar :selected="selectedTabIndex" />
	</view>
</template>

<script>
	import customTabbar from '@/components/custom-tabbar/custom-tabbar.vue';

	export default {
		components: {
			customTabbar
		},
		data() {
			return {
				selectedTabIndex: 1,
				activeGroup: 0,
				// 添加模拟分组数据
				groups: [{
						id: 1,
						name: "推荐"
					},
					{
						id: 2,
						name: "手机数码"
					},
					{
						id: 3,
						name: "家用电器"
					},
					{
						id: 4,
						name: "食品生鲜"
					},
					{
						id: 5,
						name: "美妆护肤"
					},
					{
						id: 6,
						name: "服饰鞋包"
					},
					{
						id: 7,
						name: "家居生活"
					}
				],
				products: [],
				page: 1,
				pageSize: 10,
				loading: false,
				noMore: false,
				cartCount: 3, // 设置默认购物车数量
				columnHeights: {
					left: 0,
					right: 0
				}
			}
		},
		computed: {
			leftColumnItems() {
				return this.products.filter(item => item.column === 'left')
			},
			rightColumnItems() {
				return this.products.filter(item => item.column === 'right')
			}
		},
		methods: {
			distributeProducts(newProducts) {
				newProducts.forEach(item => {
					const itemHeight = Math.random() * 100 + 200 // 200-300之间的随机高度

					if (this.columnHeights.left <= this.columnHeights.right) {
						item.column = 'left'
						this.columnHeights.left += itemHeight
					} else {
						item.column = 'right'
						this.columnHeights.right += itemHeight
					}
				})
			},
			async fetchGroups() {
				try {
					// 注释掉API请求，直接使用模拟数据
					// const res = await uni.request({
					// 	url: 'http://your-api-domain.com/api/groups',
					// 	method: 'GET'
					// })
					// if (res[1].data.code === 200) {
					// 	this.groups = res[1].data.data
					// 	// 默认加载第一个分组的商品
					// 	this.fetchProducts(this.groups[0].id)
					// }

					// 使用模拟数据后直接加载第一个分组的商品
					this.fetchProducts(this.groups[0].id)
				} catch (error) {
					console.error('获取分组失败:', error)
				}
			},
			async fetchProducts(groupId, isLoadMore = false) {
				if (this.loading) return
				this.loading = true

				if (!isLoadMore) {
					this.page = 1
					this.noMore = false
					this.columnHeights = {
						left: 0,
						right: 0
					}
				}

				try {
					// 注释掉API请求，使用模拟商品数据
					// const res = await uni.request({
					// 	url: 'http://your-api-domain.com/api/products',
					// 	method: 'GET',
					// 	data: {
					// 		category_id: categoryId,
					// 		page: this.page,
					// 		page_size: this.pageSize
					// 	}
					// })

					// 模拟API返回结构
					const mockProducts = this.generateMockProducts(groupId)
					const newProducts = mockProducts.data.items

					this.distributeProducts(newProducts)

					if (isLoadMore) {
						this.products = [...this.products, ...newProducts]
					} else {
						this.products = newProducts
					}

					if (newProducts.length < this.pageSize) {
						this.noMore = true
					}
					this.page++
				} catch (error) {
					console.error('获取商品失败:', error)
				} finally {
					this.loading = false
				}
			},
			// 添加生成模拟商品数据的方法
			generateMockProducts(groupId) {
				const groupMap = {
					1: ["推荐商品", "red"],
					2: ["手机", "digital"],
					3: ["家电", "appliance"],
					4: ["食品", "food"],
					5: ["美妆", "beauty"],
					6: ["服饰", "clothing"],
					7: ["家居", "home"]
				}

				const [groupName, type] = groupMap[groupId] || ["商品", "product"]
				const mockImages = [
					"https://img.yzcdn.cn/vant/apple-1.jpg",
					"https://img.yzcdn.cn/vant/apple-2.jpg",
					"https://img.yzcdn.cn/vant/apple-3.jpg",
					"https://img.yzcdn.cn/vant/apple-4.jpg",
					"https://img.yzcdn.cn/vant/apple-5.jpg",
					"https://img.yzcdn.cn/vant/apple-6.jpg",
					"https://img.yzcdn.cn/vant/apple-7.jpg",
					"https://img.yzcdn.cn/vant/apple-8.jpg"
				]

				const products = []
				for (let i = 0; i < this.pageSize; i++) {
					const price = (Math.random() * 100 + 20).toFixed(2)
					const originalPrice = (parseFloat(price) + Math.random() * 50).toFixed(2)

					products.push({
						id: `${groupId}_${this.page}_${i}`,
						title: `${groupName}${i+1} ${this.getRandomProductDesc(type)}`,
						price: price,
						original_price: Math.random() > 0.3 ? originalPrice : null,
						sales: Math.floor(Math.random() * 1000),
						image: mockImages[i % mockImages.length]
					})
				}

				return {
					code: 200,
					data: {
						items: products
					}
				}
			},
			// 添加获取随机商品描述的方法
			getRandomProductDesc(type) {
				const descMap = {
					red: ["新品上市", "热卖推荐", "限时特惠", "爆款"],
					digital: ["智能手机", "蓝牙耳机", "智能手表", "平板电脑", "数码相机"],
					appliance: ["冰箱", "洗衣机", "空调", "电视机", "微波炉"],
					food: ["新鲜水果", "进口零食", "有机蔬菜", "海鲜水产"],
					beauty: ["精华液", "面膜", "口红", "粉底液", "眼霜"],
					clothing: ["T恤", "牛仔裤", "连衣裙", "运动鞋", "外套"],
					home: ["床上用品", "厨具", "收纳", "装饰画", "灯具"],
					product: ["优质商品", "热销商品", "新品", "特价商品"]
				}

				const descs = descMap[type] || descMap.product
				return descs[Math.floor(Math.random() * descs.length)]
			},
			changeGroup(index) {
				this.activeGroup = index
				const groupId = this.groups[index].id
				this.fetchProducts(groupId)
			},
			goToDetail(productId) {
				uni.navigateTo({
					url: `/pages/trade-list/product-detail?id=${productId}`
				})
			},
			goToSearch() {
				uni.navigateTo({
					url: '/pages/search/products'
				})
			},
			goToCart() {
				uni.navigateTo({
					url: '/pages/trade-list/cartList'
				})
			},
			async fetchCartCount() {
				try {
					// 注释掉API请求，直接使用模拟数据
					// const res = await uni.request({
					// 	url: 'http://your-api-domain.com/api/cart/count',
					// 	method: 'GET',
					// 	header: {
					// 		'Authorization': 'Bearer ' + uni.getStorageSync('token')
					// 	}
					// })
					// if (res[1].data.code === 200) {
					// 	this.cartCount = res[1].data.data.count
					// }

					// 模拟购物车数量
					this.cartCount = Math.floor(Math.random() * 10)
				} catch (error) {
					console.error('获取购物车数量失败:', error)
				}
			},
			onReachBottomHandler() {
				if (!this.noMore && !this.loading) {
					const groupId = this.groups[this.activeGroup].id
					this.fetchProducts(groupId, true)
				}
			}
		},
		mounted() {
			this.fetchGroups()
			this.fetchCartCount()
		},
		onReachBottom() {
			this.onReachBottomHandler()
		}
	}
</script>

<style scoped>
	.uni-status-bar {
		background-color: #f5f5f5;
	}	
	.shop-container {
		padding: 10px;
		background-color: #f5f5f5;
		margin-top: 40rpx;
	}

	.top-bar {
		display: flex;
		align-items: center;
		padding: 10px 0;
		margin-bottom: 10px;
	}

	.search-bar {
		flex: 1;
		display: flex;
		align-items: center;
		background-color: #f1f1f1;
		border-radius: 18px;
		padding: 8px 15px;
		margin-right: 15px;
	}

	.search-text {
		color: #999;
		font-size: 14px;
		margin-left: 8px;
	}

	.cart-icon {
		position: relative;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.cart-badge {
		position: absolute;
		top: -5px;
		right: -5px;
		background-color: #ff2442;
		color: white;
		border-radius: 10px;
		font-size: 10px;
		min-width: 16px;
		height: 16px;
		line-height: 16px;
		text-align: center;
		padding: 0 4px;
	}

	.group-tabs {
		white-space: nowrap;
		margin-bottom: 10px;
	}
	
	/* 添加以下样式来移除分组标签栏的黑色横线 */
	.group-tabs ::v-deep ::-webkit-scrollbar {
		display: none;
		width: 0 !important;
		height: 0 !important;
		-webkit-appearance: none;
		background: transparent;
	}

	.tab-item {
		display: inline-block;
		padding: 8px 15px;
		margin-right: 10px;
		font-size: 14px;
		color: #333;
		border-radius: 15px;
		background-color: #f1f1f1;
	}

	.tab-item.active {
		background-color: #ff2442;
		color: white;
	}

	.waterfall-container {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.waterfall-column {
		flex: 0 0 48%;
	}

	.product-item {
		background-color: white;
		border-radius: 8px;
		overflow: hidden;
		margin-bottom: 12px;
		box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
		transition: transform 0.2s;
	}

	.product-item:active {
		transform: scale(0.98);
	}

	.product-image {
		width: 100%;
		display: block;
	}

	.product-info {
		padding: 8px;
	}

	.product-title {
		font-size: 13px;
		color: #333;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
		margin-bottom: 5px;
		line-height: 1.4;
	}

	.price-section {
		display: flex;
		align-items: center;
		margin-bottom: 5px;
	}

	.product-price {
		font-size: 16px;
		color: #ff2442;
		font-weight: bold;
		margin-right: 5px;
	}

	.original-price {
		font-size: 12px;
		color: #999;
		text-decoration: line-through;
	}

	.sales-info {
		font-size: 12px;
		color: #999;
	}

	.load-more {
		text-align: center;
		padding: 15px 0;
		color: #999;
		font-size: 14px;
	}
</style>