<template>
	<view class="shop-container">
		<!-- 搜索栏 -->
		<view class="search-bar">
			<view class="search-input">
				<i class="search-icon">🔍</i>
				<input 
					v-model="searchKeyword" 
					placeholder="搜索商品" 
					@keyup.enter="handleSearch"
					@input="handleSearchInput"
				/>
			</view>
		</view>

		<!-- 分类筛选 -->
		<view class="category-filter">
			<view class="category-scroll">
				<view 
					class="category-item"
					:class="{ active: selectedCategory === '' }"
					@click="selectCategory('')"
				>
					全部
				</view>
				<view 
					v-for="category in categories"
					:key="category.uuid"
					class="category-item"
					:class="{ active: selectedCategory === category.uuid }"
					@click="selectCategory(category.uuid)"
				>
					{{ category.name }}
				</view>
			</view>
		</view>

		<!-- 排序栏 -->
		<view class="sort-bar">
			<view 
				class="sort-item" 
				:class="{ active: sortBy === 'created_at' }"
				@click="changeSort('created_at')"
			>
				最新
			</view>
			<view 
				class="sort-item" 
				:class="{ active: sortBy === 'price' }"
				@click="changeSort('price')"
			>
				价格
				<i class="sort-icon">{{ sortOrder === 'asc' ? '↑' : '↓' }}</i>
			</view>
			<view 
				class="sort-item" 
				:class="{ active: sortBy === 'sales' }"
				@click="changeSort('sales')"
			>
				销量
			</view>
		</view>

		<!-- 商品列表 -->
		<view class="product-list">
        <view class="product-item" v-for="item in products" :key="item.id" @click="goToProduct(item.id)">
				<image class="product-image" :src="item.images && item.images[0] || item.image_url " />
				<view class="product-info">
					<view class="product-title">{{ item.name }}</view>
					<view class="product-meta">
						<text class="category-name">{{ item.category_name }}</text>
						<text class="sales-count">已售{{ item.sales_count || 0 }}件</text>
					</view>
					<view class="price-section">
						<text class="current-price">¥{{ item.price }}</text>
						<text v-if="item.original_price" class="original-price">¥{{ item.original_price }}</text>
					</view>
					<view class="rating-section">
						<view class="rating-stars">
							<text v-for="i in 5" :key="i" class="star" :class="{ active: i <= (item.rating || 0) }">★</text>
						</view>
						<text class="rating-text">{{ item.rating || 0 }}</text>
						<text class="review-count">({{ item.review_count || 0 }})</text>
					</view>
				</view>
          <button class="cart-icon-btn" @click.stop="quickAdd(item)" aria-label="加入购物车">+</button>
			</view>
			
			<!-- 加载更多 -->
			<view v-if="loading" class="loading">
				<view class="loading-text">加载中...</view>
			</view>
			
			<!-- 没有更多数据 -->
			<view v-if="!hasMore && products.length > 0" class="no-more">
				<view class="no-more-text">没有更多数据了</view>
			</view>
			
			<!-- 空状态 -->
			<view v-if="!loading && products.length === 0" class="empty-state">
				<view class="empty-icon">📦</view>
				<view class="empty-text">暂无商品</view>
			</view>
		</view>
	</view>
</template>

<script>
  import { productApi, cartApi } from '@/src/utils/api.js'
  import { getUserId } from '@/src/utils/auth.js'
  import categoryService from '@/src/services/categoryService.js'
	
	export default {
		name: 'Shop',
		data() {
			return {
				products: [],
				categories: [],
				selectedCategory: '',
				searchKeyword: '',
				sortBy: 'created_at',
				sortOrder: 'desc',
				page: 1,
				perPage: 16,
				loading: false,
				refreshing: false,
				hasMore: true,
				total: 0
			}
		},
			onLoad() {
			this.fetchCategories()
			this.fetchProducts()
		},
		
		onShow() {
			// 页面显示时的逻辑
		},
		methods: {
			// 获取商品品类
			async fetchCategories() {
				try {
					const response = await categoryService.getCategories();
          this.categories = response.data
				} catch (error) {
					console.error('获取分类失败:', error)
					uni.showToast({
						title: '获取分类失败',
						icon: 'none'
					})
				}
			},
			
			// 获取商品列表
			async fetchProducts(refresh = false) {
				if (this.loading) return
				
				this.loading = true
				
				if (refresh) {
					this.page = 1
					this.products = []
					this.hasMore = true
				}
				
				try {
					const params = {
						page: this.page,
						per_page: this.perPage,
						sort_by: this.sortBy,
						sort_order: this.sortOrder
					}
					
					if (this.selectedCategory) {
						params.category_uuid = this.selectedCategory
					}
					
					if (this.searchKeyword) {
						params.search = this.searchKeyword
					}
					
					const response = await productApi.getProducts(params)
					
					if (response.data.code === 200) {
						const { list, total, has_next } = response.data.data
						
						if (refresh) {
							this.products = list
						} else {
							this.products = [...this.products, ...list]
						}
						
						this.total = total
						this.hasMore = has_next
						
						if (this.refreshing) {
							this.refreshing = false
						}
					} else {
						uni.showToast({
							title: response.data.message || '获取商品失败',
							icon: 'none'
						})
					}
				} catch (error) {
					console.error('获取商品失败:', error)
					uni.showToast({
						title: '网络错误',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			
			// 选择分类
			selectCategory(categoryId) {
				this.selectedCategory = categoryId
				this.fetchProducts(true)
			},
			
			// 搜索
			handleSearch() {
				this.fetchProducts(true)
			},
			
			// 搜索输入
			handleSearchInput() {
				// 可以添加防抖逻辑
			},
			
			// 改变排序
			changeSort(sortBy) {
				if (this.sortBy === sortBy) {
					this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
				} else {
					this.sortBy = sortBy
					this.sortOrder = 'desc'
				}
				this.fetchProducts(true)
			},
			
			// 跳转到商品详情
			goToProduct(productId) {
				uni.navigateTo({
					url: `/pages/product-detail/product-detail?id=${productId}`
				})
			},

      // 一键加入购物车（若有规格则默认第一个活动规格组合）
      async quickAdd(item) {
        try {
          const specCombinationId = item.has_specs ? item.default_spec_combination_id : undefined
          const res = await cartApi.quickAddToCart({
            productId: item.id,
            userId: getUserId(),
            quantity: 1,
            specCombinationId
          })
          if (res.data.code === 200) {
            uni.showToast({
              title: '已加入购物车',
              icon: 'success'
            })
          } else {
            uni.showToast({
              title: res.data.message || '加入购物车失败',
              icon: 'none'
            })
          }
        } catch (e) {
          console.error('加入购物车失败:', e)
          uni.showToast({
            title: '网络错误，加入购物车失败',
            icon: 'none'
          })
        }
      },
			
			// 设置滚动监听
			setupScrollListener() {
				// uni-app中不需要手动设置滚动监听，可以使用onReachBottom
			},
			
			// 移除滚动监听
			removeScrollListener() {
				// uni-app中不需要手动移除滚动监听
			},
			
			// 处理滚动事件 - 使用uni-app的onReachBottom生命周期
			onReachBottom() {
				if (this.hasMore && !this.loading) {
					this.loadMore()
				}
			},
			
			// 加载更多
			loadMore() {
				if (this.hasMore && !this.loading) {
					this.page++
					this.fetchProducts()
				}
			}
		}
	}
</script>

<style scoped>
	.shop-container {
		padding: 40rpx;
		margin: 0 auto;
	}

	.search-bar {
		margin-bottom: 40rpx;
	}

	.search-input {
		display: flex;
		align-items: center;
		background-color: #fff;
		border-radius: 40rpx;
		padding: 20rpx 30rpx;
		border: 2rpx solid #eee;
		box-shadow: 0 4rpx 8rpx rgba(0,0,0,0.1);
	}

	.search-icon {
		margin-right: 20rpx;
		color: #999;
	}

	.search-input input {
		flex: 1;
		border: none;
		outline: none;
		font-size: 28rpx;
		color: #333;
		background: transparent;
	}

	.category-filter {
		margin-bottom: 40rpx;
	}

	.category-scroll {
		display: flex;
		overflow-x: auto;
		gap: 20rpx;
		padding: 20rpx 0;
	}

	.category-item {
		padding: 16rpx 30rpx;
		font-size: 28rpx;
		color: #666;
		border-radius: 40rpx;
		background-color: #f5f5f5;
		cursor: pointer;
		white-space: nowrap;
		transition: all 0.3s;
	}

	.category-item:hover {
		background-color: #e0e0e0;
	}

	.category-item.active {
		background-color: #e93b3d;
		color: #fff;
		font-weight: bold;
	}

	.sort-bar {
		display: flex;
		background-color: #fff;
		margin-bottom: 20px;
		padding: 15px;
		border-radius: 8px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.sort-item {
		display: flex;
		align-items: center;
		font-size: 14px;
		color: #666;
		margin-right: 30px;
		cursor: pointer;
		transition: color 0.3s;
	}

	.sort-item:hover {
		color: #e93b3d;
	}

	.sort-item.active {
		color: #e93b3d;
		font-weight: bold;
	}

	.sort-icon {
		margin-left: 5px;
		font-size: 12px;
	}

	.product-list {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 12px;
		margin-bottom: 20px;
	}

	.product-item {
		background-color: #fff;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 2px 8px rgba(0,0,0,0.1);
		transition: transform 0.3s, box-shadow 0.3s;
		cursor: pointer;
    height: 280px;
    display: flex;
    flex-direction: column;
    position: relative;
	}

	.product-item:hover {
		transform: translateY(-3px);
		box-shadow: 0 6px 16px rgba(0,0,0,0.15);
	}

	.product-image {
		width: 100%;
		height: 160px;
		object-fit: cover;
	}

	.product-info {
		padding: 12px;
		display: flex;
		flex-direction: column;
		flex: 1;
	}

	.product-title {
		font-size: 13px;
		line-height: 1.3;
		color: #333;
		margin-bottom: 6px;
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
		height: 34px;
	}

	.product-meta {
		display: flex;
		justify-content: space-between;
		font-size: 11px;
		color: #999;
		margin-bottom: 6px;
	}

	.price-section {
		display: flex;
		align-items: baseline;
		margin-bottom: 6px;
		flex: 1;
	}

	.current-price {
		font-size: 16px;
		color: #e93b3d;
		font-weight: bold;
	}

	.original-price {
		font-size: 12px;
		color: #999;
		text-decoration: line-through;
		margin-left: 8px;
	}

	.rating-section {
		display: flex;
		align-items: center;
		font-size: 11px;
		color: #999;
	}

  .cart-icon-btn {
    position: absolute;
    right: 8px;
    bottom: 8px;
    width: 22px;
    height: 22px;
    border-radius: 11px;
    border: none;
    background: #e93b3d;
    color: #fff;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(233,59,61,0.25);
    transition: transform .1s ease, box-shadow .2s ease, background .2s ease;
    font-size: 14px;
    line-height: 1;
    font-weight: 700;
  }

  .cart-icon-btn:hover {
    background: #d63333;
    box-shadow: 0 4px 12px rgba(233,59,61,0.35);
  }

  .cart-icon-btn:active {
    transform: scale(0.96);
  }

	.rating-stars {
		display: flex;
		margin-right: 5px;
	}

	.star {
		color: #ddd;
		font-size: 12px;
	}

	.star.active {
		color: #ffd700;
	}

	.rating-text {
		margin-right: 5px;
	}

	.loading, .no-more, .empty-state {
		grid-column: 1 / -1;
		padding: 30px 0;
		text-align: center;
	}

	.loading-text, .no-more-text {
		color: #999;
		font-size: 14px;
	}

	.empty-icon {
		font-size: 60px;
		margin-bottom: 15px;
		opacity: 0.5;
	}

	.empty-text {
		font-size: 14px;
		color: #999;
	}

	@media (max-width: 768px) {
		.shop-container {
			padding: 10px;
		}
		
		.product-list {
			grid-template-columns: repeat(2, 1fr);
			gap: 10px;
		}
		
		.product-item {
			height: 260px;
		}
		
		.product-image {
			height: 140px;
		}
		
		.product-info {
			padding: 10px;
		}
		
		.product-title {
			font-size: 12px;
			height: 32px;
		}
		
		.current-price {
			font-size: 15px;
		}
		
		.sort-bar {
			padding: 10px;
		}
		
		.sort-item {
			margin-right: 20px;
		}
	}
	
	@media (max-width: 480px) {
		.product-list {
			gap: 8px;
		}
		
		.product-item {
			height: 240px;
		}
		
		.product-image {
			height: 120px;
		}
		
		.product-info {
			padding: 8px;
		}
		
		.product-title {
			font-size: 11px;
			height: 28px;
		}
		
		.current-price {
			font-size: 14px;
		}
	}
</style>