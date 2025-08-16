<template>
  <div class="shop">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-select v-model="filters.group" placeholder="选择分类" clearable>
            <el-option
              v-for="group in groups"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.sort" placeholder="排序方式">
            <el-option label="默认排序" value="default" />
            <el-option label="价格从低到高" value="price-asc" />
            <el-option label="价格从高到低" value="price-desc" />
            <el-option label="销量优先" value="sales" />
            <el-option label="最新上架" value="newest" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="filters.priceRange"
            placeholder="价格区间 (如: 100-1000)"
            clearable
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 商品列表 -->
    <div class="product-list">
      <el-row :gutter="20">
        <el-col 
          :span="6" 
          v-for="product in products" 
          :key="product.id"
          class="product-col"
        >
          <el-card class="product-card" @click="goToProduct(product.id)">
            <div class="product-image-container">
              <img :src="product.image" :alt="product.name" class="product-image">
              <div class="product-overlay">
                <el-button type="primary" size="small" @click.stop="addToCart(product)">
                  加入购物车
                </el-button>
                <el-button size="small" @click.stop="addToWishlist(product)">
                  收藏
                </el-button>
              </div>
            </div>
            <div class="product-info">
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-description">{{ product.description }}</p>
              <div class="product-meta">
                <span class="product-price">¥{{ product.price }}</span>
                <span class="product-sales">已售 {{ product.sales }}</span>
              </div>
              <div class="product-rating">
                <el-rate :value="product.rating" disabled show-score />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Shop',
  setup() {
    const router = useRouter()
    const route = useRoute()

    // 筛选条件
    const filters = reactive({
      group: '',
      sort: 'default',
      priceRange: ''
    })

    // 分页
    const currentPage = ref(1)
    const pageSize = ref(12)
    const total = ref(100)

    // 商品分类
    const groups = ref([
      { id: 1, name: '手机数码' },
      { id: 2, name: '服装配饰' },
      { id: 3, name: '家居生活' },
      { id: 4, name: '美妆护肤' },
      { id: 5, name: '运动户外' },
      { id: 6, name: '图书音像' }
    ])

    // 商品列表
    const products = ref([
      {
        id: 1001,
        name: 'Apple iPhone 15 Pro',
        description: '最新款iPhone，A17 Pro芯片，钛金属设计',
        price: 7999,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 2500,
        rating: 4.8,
        group: 1
      },
      {
        id: 1002,
        name: 'MacBook Pro 14英寸',
        description: 'M2 Pro芯片，专业级性能',
        price: 14999,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 1200,
        rating: 4.9,
        group: 1
      },
      {
        id: 1003,
        name: 'AirPods Pro',
        description: '主动降噪，空间音频',
        price: 1899,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 5000,
        rating: 4.7,
        group: 1
      },
      {
        id: 1004,
        name: 'iPad Air',
        description: 'M1芯片，10.9英寸全面屏',
        price: 4399,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 1800,
        rating: 4.6,
        group: 1
      },
      {
        id: 2001,
        name: 'Nike Air Max 270',
        description: '舒适缓震，时尚设计',
        price: 899,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 3200,
        rating: 4.5,
        group: 2
      },
      {
        id: 2002,
        name: 'Adidas Ultraboost 22',
        description: '能量回弹，轻盈透气',
        price: 1299,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 2100,
        rating: 4.7,
        group: 2
      },
      {
        id: 3001,
        name: '小米空气净化器',
        description: '高效过滤，智能控制',
        price: 599,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 4500,
        rating: 4.4,
        group: 3
      },
      {
        id: 3002,
        name: '戴森吸尘器 V15',
        description: '强劲吸力，无线设计',
        price: 4599,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        sales: 800,
        rating: 4.8,
        group: 3
      }
    ])

    // 应用筛选
    const applyFilters = () => {
      // 这里应该调用API获取筛选后的商品
      console.log('应用筛选:', filters)
      ElMessage.success('筛选已应用')
    }

    // 重置筛选
    const resetFilters = () => {
      filters.group = ''
      filters.sort = 'default'
      filters.priceRange = ''
      applyFilters()
    }

    // 分页处理
    const handleSizeChange = (val) => {
      pageSize.value = val
      // 重新加载数据
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      // 重新加载数据
    }

    // 跳转到商品详情
    const goToProduct = (productId) => {
      router.push(`/product/${productId}`)
    }

    // 加入购物车
    const addToCart = (product) => {
      ElMessage.success(`已将 ${product.name} 加入购物车`)
    }

    // 添加到收藏
    const addToWishlist = (product) => {
      ElMessage.success(`已将 ${product.name} 添加到收藏`)
    }

    onMounted(() => {
      // 从URL参数获取分类筛选
      if (route.query.group) {
        filters.group = parseInt(route.query.group)
      }
    })

    return {
      filters,
      groups,
      products,
      currentPage,
      pageSize,
      total,
      applyFilters,
      resetFilters,
      handleSizeChange,
      handleCurrentChange,
      goToProduct,
      addToCart,
      addToWishlist
    }
  }
}
</script>

<style scoped>
.shop {
  max-width: 1200px;
  margin: 0 auto;
}

.filter-bar {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-list {
  margin-bottom: 30px;
}

.product-col {
  margin-bottom: 20px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  height: 100%;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.product-image-container {
  position: relative;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.product-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .product-overlay {
  opacity: 1;
}

.product-info {
  padding: 15px;
}

.product-name {
  font-size: 1rem;
  margin-bottom: 8px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e74c3c;
}

.product-sales {
  font-size: 0.8rem;
  color: #999;
}

.product-rating {
  display: flex;
  align-items: center;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}
</style> 