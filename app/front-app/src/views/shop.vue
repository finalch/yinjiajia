<template>
	<div class="shop-container">
		<!-- 搜索栏 -->
		<div class="search-bar">
			<div class="search-input">
				<i class="search-icon">🔍</i>
				<input 
					v-model="searchKeyword" 
					placeholder="搜索商品" 
					@keyup.enter="handleSearch"
					@input="handleSearchInput"
				/>
			</div>
		</div>

		<!-- 分类筛选 -->
		<div class="group-filter">
			<div class="group-scroll">
				<div 
					class="group-item" 
					:class="{ active: selectedCategory === '' }"
					@click="selectCategory('')"
				>
					全部
				</div>
				<div 
					v-for="group in groups" 
					:key="group.id"
					class="group-item" 
					:class="{ active: selectedCategory === group.id }"
					@click="selectCategory(group.id)"
				>
					{{ group.name }}
				</div>
			</div>
		</div>

		<!-- 排序栏 -->
		<div class="sort-bar">
			<div 
				class="sort-item" 
				:class="{ active: sortBy === 'created_at' }"
				@click="changeSort('created_at')"
			>
				最新
			</div>
			<div 
				class="sort-item" 
				:class="{ active: sortBy === 'price' }"
				@click="changeSort('price')"
			>
				价格
				<i class="sort-icon">{{ sortOrder === 'asc' ? '↑' : '↓' }}</i>
			</div>
			<div 
				class="sort-item" 
				:class="{ active: sortBy === 'sales' }"
				@click="changeSort('sales')"
			>
				销量
			</div>
		</div>

		<!-- 商品列表 -->
		<div class="product-list">
        <div class="product-item" v-for="item in products" :key="item.id" @click="goToProduct(item.id)">
				<img class="product-image" :src="item.images && item.images[0] || item.image_url " />
				<div class="product-info">
					<div class="product-title">{{ item.name }}</div>
					<div class="product-meta">
						<span class="group-name">{{ item.category_name }}</span>
						<span class="sales-count">已售{{ item.sales_count || 0 }}件</span>
					</div>
					<div class="price-section">
						<span class="current-price">¥{{ item.price }}</span>
						<span v-if="item.original_price" class="original-price">¥{{ item.original_price }}</span>
					</div>
					<div class="rating-section">
						<div class="rating-stars">
							<span v-for="i in 5" :key="i" class="star" :class="{ active: i <= (item.rating || 0) }">★</span>
						</div>
						<span class="rating-text">{{ item.rating || 0 }}</span>
						<span class="review-count">({{ item.review_count || 0 }})</span>
					</div>
				</div>
          <button class="cart-icon-btn" @click.stop="quickAdd(item)" aria-label="加入购物车">+</button>
			</div>
			
			<!-- 加载更多 -->
			<div v-if="loading" class="loading">
				<div class="loading-text">加载中...</div>
			</div>
			
			<!-- 没有更多数据 -->
			<div v-if="!hasMore && products.length > 0" class="no-more">
				<div class="no-more-text">没有更多数据了</div>
			</div>
			
			<!-- 空状态 -->
			<div v-if="!loading && products.length === 0" class="empty-state">
				<div class="empty-icon">📦</div>
				<div class="empty-text">暂无商品</div>
			</div>
		</div>
	</div>
</template>

<script>
  import { productApi, cartApi } from '@/utils/api.js'
  import { getUserId } from '@/utils/auth.js'
	
	export default {
		name: 'Shop',
		data() {
			return {
				products: [],
				groups: [],
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
			mounted() {
		this.fetchCategories()
		this.fetchProducts()
		this.setupScrollListener()
	},
	
	beforeUnmount() {
		this.removeScrollListener()
	},
		methods: {
			// 获取商品分类
			async fetchCategories() {
				try {
					const response = await productApi.getCategories()
					
					if (response.data.code === 200) {
						this.groups = response.data.data
					}
				} catch (error) {
					console.error('获取分类失败:', error)
					alert('获取分类失败')
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
						params.category_id = this.selectedCategory
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
						alert(response.data.message || '获取商品失败')
					}
				} catch (error) {
					console.error('获取商品失败:', error)
					alert('网络错误')
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
				this.$router.push(`/product/${productId}`)
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
            // alert('已加入购物车')
          } else {
            alert(res.data.message || '加入购物车失败')
          }
        } catch (e) {
          console.error('加入购物车失败:', e)
          alert('网络错误，加入购物车失败')
        }
      },
			
			// 设置滚动监听
			setupScrollListener() {
				window.addEventListener('scroll', this.handleScroll)
			},
			
			// 移除滚动监听
			removeScrollListener() {
				window.removeEventListener('scroll', this.handleScroll)
			},
			
			// 处理滚动事件
			handleScroll() {
				if (this.loading || !this.hasMore) return
				
				const scrollTop = window.pageYOffset || document.documentElement.scrollTop
				const windowHeight = window.innerHeight
				const documentHeight = document.documentElement.scrollHeight
				
				if (scrollTop + windowHeight >= documentHeight - 100) {
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
		padding: 20px;
		max-width: 1200px;
		margin: 0 auto;
	}

	.search-bar {
		margin-bottom: 20px;
	}

	.search-input {
		display: flex;
		align-items: center;
		background-color: #fff;
		border-radius: 20px;
		padding: 10px 15px;
		border: 1px solid #eee;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.search-icon {
		margin-right: 10px;
		color: #999;
	}

	.search-input input {
		flex: 1;
		border: none;
		outline: none;
		font-size: 14px;
		color: #333;
		background: transparent;
	}

	.group-filter {
		margin-bottom: 20px;
	}

	.group-scroll {
		display: flex;
		overflow-x: auto;
		gap: 10px;
		padding: 10px 0;
	}

	.group-item {
		padding: 8px 15px;
		font-size: 14px;
		color: #666;
		border-radius: 20px;
		background-color: #f5f5f5;
		cursor: pointer;
		white-space: nowrap;
		transition: all 0.3s;
	}

	.group-item:hover {
		background-color: #e0e0e0;
	}

	.group-item.active {
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