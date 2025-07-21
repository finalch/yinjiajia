<template>
  <div class="cart">
    <h1 class="page-title">购物车</h1>
    
    <div v-if="cartItems.length === 0" class="empty-cart">
      <el-empty description="购物车是空的">
        <el-button type="primary" @click="$router.push('/shop')">
          去购物
        </el-button>
      </el-empty>
    </div>
    
    <div v-else class="cart-content">
      <!-- 购物车商品列表 -->
      <div class="cart-items">
        <el-card class="cart-header">
          <el-row :gutter="20">
            <el-col :span="1">
              <el-checkbox
                v-model="selectAll"
                @change="handleSelectAll"
              />
            </el-col>
            <el-col :span="8">商品信息</el-col>
            <el-col :span="3">单价</el-col>
            <el-col :span="3">数量</el-col>
            <el-col :span="3">小计</el-col>
            <el-col :span="3">操作</el-col>
          </el-row>
        </el-card>
        
        <el-card
          v-for="item in cartItems"
          :key="item.id"
          class="cart-item"
        >
          <el-row :gutter="20" align="middle">
            <el-col :span="1">
              <el-checkbox
                v-model="item.selected"
                @change="handleItemSelect"
              />
            </el-col>
            <el-col :span="8">
              <div class="product-info">
                <el-image
                  :src="item.image"
                  fit="cover"
                  class="product-image"
                  @click="$router.push(`/product/${item.productId}`)"
                />
                <div class="product-details">
                  <h3 class="product-name">{{ item.name }}</h3>
                  <p class="product-specs">{{ item.specs }}</p>
                </div>
              </div>
            </el-col>
            <el-col :span="3">
              <span class="product-price">¥{{ item.price }}</span>
            </el-col>
            <el-col :span="3">
              <el-input-number
                v-model="item.quantity"
                :min="1"
                :max="item.stock"
                size="small"
                @change="updateQuantity(item)"
              />
            </el-col>
            <el-col :span="3">
              <span class="subtotal">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
            </el-col>
            <el-col :span="3">
              <el-button
                type="danger"
                size="small"
                @click="removeItem(item.id)"
              >
                删除
              </el-button>
            </el-col>
          </el-row>
        </el-card>
      </div>
      
      <!-- 购物车底部 -->
      <div class="cart-footer">
        <el-card>
          <el-row :gutter="20" align="middle">
            <el-col :span="8">
              <el-checkbox
                v-model="selectAll"
                @change="handleSelectAll"
              >
                全选
              </el-checkbox>
              <el-button
                type="text"
                @click="removeSelected"
                :disabled="!hasSelectedItems"
              >
                删除选中
              </el-button>
            </el-col>
            <el-col :span="8" class="cart-summary">
              <div class="summary-item">
                <span>已选择 {{ selectedCount }} 件商品</span>
              </div>
              <div class="summary-item">
                <span>总计: </span>
                <span class="total-price">¥{{ totalPrice.toFixed(2) }}</span>
              </div>
            </el-col>
            <el-col :span="8" class="checkout-actions">
              <el-button
                type="primary"
                size="large"
                @click="checkout"
                :disabled="!hasSelectedItems"
              >
                结算 ({{ selectedCount }})
              </el-button>
            </el-col>
          </el-row>
        </el-card>
      </div>
    </div>
    
    <!-- 推荐商品 -->
    <div class="recommendations">
      <h2 class="section-title">为您推荐</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="product in recommendedProducts" :key="product.id">
          <el-card class="product-card" @click="$router.push(`/product/${product.id}`)">
            <img :src="product.image" :alt="product.name" class="product-image">
            <div class="product-info">
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">¥{{ product.price }}</p>
              <el-button type="primary" size="small" @click.stop="addToCart(product)">
                加入购物车
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Cart',
  setup() {
    const router = useRouter()

    // 购物车商品
    const cartItems = ref([
      {
        id: 1,
        productId: 1001,
        name: 'Apple iPhone 15 Pro',
        specs: '暗紫色 256GB',
        price: 7999,
        quantity: 1,
        stock: 10,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        selected: true
      },
      {
        id: 2,
        productId: 1003,
        name: 'AirPods Pro',
        specs: '白色',
        price: 1899,
        quantity: 2,
        stock: 50,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        selected: true
      },
      {
        id: 3,
        productId: 1004,
        name: 'iPad Air',
        specs: '深空灰 64GB',
        price: 4399,
        quantity: 1,
        stock: 15,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        selected: false
      }
    ])

    // 推荐商品
    const recommendedProducts = ref([
      {
        id: 2001,
        name: 'Apple Watch Series 9',
        price: 2999,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2002,
        name: 'Sony WH-1000XM5',
        price: 2899,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2003,
        name: 'Nintendo Switch OLED',
        price: 2299,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2004,
        name: 'DJI Mini 3 Pro',
        price: 4799,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      }
    ])

    // 计算属性
    const selectAll = computed({
      get() {
        return cartItems.value.length > 0 && cartItems.value.every(item => item.selected)
      },
      set(value) {
        cartItems.value.forEach(item => item.selected = value)
      }
    })

    const selectedCount = computed(() => {
      return cartItems.value.filter(item => item.selected).length
    })

    const hasSelectedItems = computed(() => {
      return selectedCount.value > 0
    })

    const totalPrice = computed(() => {
      return cartItems.value
        .filter(item => item.selected)
        .reduce((total, item) => total + (item.price * item.quantity), 0)
    })

    // 方法
    const handleSelectAll = () => {
      // 通过计算属性自动处理
    }

    const handleItemSelect = () => {
      // 通过计算属性自动处理
    }

    const updateQuantity = (item) => {
      ElMessage.success(`已更新 ${item.name} 的数量`)
    }

    const removeItem = async (itemId) => {
      try {
        await ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const index = cartItems.value.findIndex(item => item.id === itemId)
        if (index > -1) {
          cartItems.value.splice(index, 1)
          ElMessage.success('商品已删除')
        }
      } catch {
        // 用户取消删除
      }
    }

    const removeSelected = async () => {
      if (!hasSelectedItems.value) return
      
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${selectedCount.value} 件商品吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        cartItems.value = cartItems.value.filter(item => !item.selected)
        ElMessage.success('选中商品已删除')
      } catch {
        // 用户取消删除
      }
    }

    const checkout = () => {
      if (!hasSelectedItems.value) {
        ElMessage.warning('请选择要结算的商品')
        return
      }
      
      const selectedItems = cartItems.value.filter(item => item.selected)
      // 这里可以将选中的商品信息传递给结算页面
      router.push('/checkout')
    }

    const addToCart = (product) => {
      ElMessage.success(`已将 ${product.name} 加入购物车`)
    }

    onMounted(() => {
      // 可以在这里加载购物车数据
    })

    return {
      cartItems,
      recommendedProducts,
      selectAll,
      selectedCount,
      hasSelectedItems,
      totalPrice,
      handleSelectAll,
      handleItemSelect,
      updateQuantity,
      removeItem,
      removeSelected,
      checkout,
      addToCart
    }
  }
}
</script>

<style scoped>
.cart {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: #333;
}

.empty-cart {
  text-align: center;
  padding: 60px 0;
}

.cart-content {
  margin-bottom: 40px;
}

.cart-header {
  margin-bottom: 10px;
  font-weight: bold;
  color: #333;
}

.cart-item {
  margin-bottom: 10px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.product-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  cursor: pointer;
}

.product-details {
  flex: 1;
}

.product-name {
  font-size: 1rem;
  margin-bottom: 5px;
  color: #333;
}

.product-specs {
  font-size: 0.9rem;
  color: #666;
}

.product-price {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e74c3c;
}

.subtotal {
  font-size: 1.1rem;
  font-weight: bold;
  color: #e74c3c;
}

.cart-footer {
  margin-top: 20px;
}

.cart-summary {
  text-align: center;
}

.summary-item {
  margin-bottom: 10px;
}

.total-price {
  font-size: 1.5rem;
  font-weight: bold;
  color: #e74c3c;
}

.checkout-actions {
  text-align: right;
}

.recommendations {
  margin-top: 40px;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 20px;
  color: #333;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-card .product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 4px;
}

.product-card .product-info {
  padding: 10px 0;
}

.product-card .product-name {
  font-size: 0.9rem;
  margin-bottom: 8px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-card .product-price {
  font-size: 1rem;
  font-weight: bold;
  color: #e74c3c;
  margin-bottom: 8px;
}
</style> 