<template>
  <div class="product-detail">
    <div class="product-container">
      <!-- 商品图片 -->
      <div class="product-images">
        <el-image
          :src="currentImage"
          fit="cover"
          class="main-image"
          :preview-src-list="product.images"
        />
        <div class="image-thumbnails">
          <el-image
            v-for="(image, index) in product.images"
            :key="index"
            :src="image"
            fit="cover"
            class="thumbnail"
            @click="currentImage = image"
          />
        </div>
      </div>

      <!-- 商品信息 -->
      <div class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        <div class="product-rating">
          <el-rate :value="product.rating" disabled show-score />
          <span class="rating-text">{{ product.rating }}分</span>
          <span class="sales-count">已售 {{ product.sales }} 件</span>
        </div>

        <div class="product-price">
          <span class="current-price">¥{{ product.price }}</span>
          <span class="original-price" v-if="product.originalPrice">¥{{ product.originalPrice }}</span>
          <span class="discount" v-if="product.discount">{{ product.discount }}折</span>
        </div>

        <!-- 规格选择 -->
        <div class="product-specs">
          <div class="spec-item" v-for="spec in product.specs" :key="spec.name">
            <h3>{{ spec.name }}</h3>
            <div class="spec-options">
              <el-button
                v-for="option in spec.options"
                :key="option.value"
                :type="selectedSpecs[spec.name] === option.value ? 'primary' : 'default'"
                @click="selectSpec(spec.name, option.value)"
                :disabled="!option.available"
              >
                {{ option.label }}
              </el-button>
            </div>
          </div>
        </div>

        <!-- 数量选择 -->
        <div class="quantity-selector">
          <h3>数量</h3>
          <el-input-number
            v-model="quantity"
            :min="1"
            :max="product.stock"
            size="large"
          />
          <span class="stock-info">库存: {{ product.stock }} 件</span>
        </div>

        <!-- 购买按钮 -->
        <div class="purchase-actions">
          <el-button
            type="primary"
            size="large"
            @click="addToCart"
            :disabled="!canPurchase"
          >
            加入购物车
          </el-button>
          <el-button
            type="danger"
            size="large"
            @click="buyNow"
            :disabled="!canPurchase"
          >
            立即购买
          </el-button>
          <el-button
            size="large"
            @click="addToWishlist"
          >
            <el-icon><Star /></el-icon>
            收藏
          </el-button>
        </div>

        <!-- 服务保障 -->
        <div class="service-guarantee">
          <div class="guarantee-item">
            <el-icon><Check /></el-icon>
            <span>正品保证</span>
          </div>
          <div class="guarantee-item">
            <el-icon><Truck /></el-icon>
            <span>极速发货</span>
          </div>
          <div class="guarantee-item">
            <el-icon><Refresh /></el-icon>
            <span>7天无理由退货</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 商品详情 -->
    <div class="product-details">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品详情" name="detail">
          <div class="detail-content" v-html="product.description"></div>
        </el-tab-pane>
        <el-tab-pane label="规格参数" name="specs">
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="param in product.parameters"
              :key="param.name"
              :label="param.name"
            >
              {{ param.value }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
        <el-tab-pane label="用户评价" name="reviews">
          <div class="reviews-section">
            <div class="review-item" v-for="review in product.reviews" :key="review.id">
              <div class="review-header">
                <el-avatar :src="review.userAvatar" />
                <div class="review-info">
                  <span class="reviewer-name">{{ review.userName }}</span>
                  <el-rate :value="review.rating" disabled size="small" />
                </div>
                <span class="review-date">{{ review.date }}</span>
              </div>
              <div class="review-content">
                <p>{{ review.content }}</p>
                <div class="review-images" v-if="review.images">
                  <el-image
                    v-for="image in review.images"
                    :key="image"
                    :src="image"
                    fit="cover"
                    class="review-image"
                  />
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Star, Check, Truck, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'ProductDetail',
  components: {
    Star,
    Check,
    Truck,
    Refresh
  },
  setup() {
    const route = useRoute()
    const router = useRouter()

    const currentImage = ref('')
    const quantity = ref(1)
    const activeTab = ref('detail')
    const selectedSpecs = reactive({})

    // 商品数据
    const product = ref({
      id: 1001,
      name: 'Apple iPhone 15 Pro Max (A2896) 256GB 暗紫色 支持移动联通电信5G',
      price: 8999,
      originalPrice: 9999,
      discount: 9,
      rating: 4.8,
      sales: 2500,
      stock: 100,
      images: [
        'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      ],
      specs: [
        {
          name: '颜色',
          options: [
            { label: '暗紫色', value: 'purple', available: true },
            { label: '深空黑色', value: 'black', available: true },
            { label: '银色', value: 'silver', available: false },
            { label: '金色', value: 'gold', available: true }
          ]
        },
        {
          name: '存储容量',
          options: [
            { label: '128GB', value: '128', available: true },
            { label: '256GB', value: '256', available: true },
            { label: '512GB', value: '512', available: true },
            { label: '1TB', value: '1024', available: false }
          ]
        }
      ],
      parameters: [
        { name: '品牌', value: 'Apple' },
        { name: '型号', value: 'iPhone 15 Pro Max' },
        { name: '屏幕尺寸', value: '6.7英寸' },
        { name: '处理器', value: 'A17 Pro' },
        { name: '存储容量', value: '256GB' },
        { name: '电池容量', value: '4441mAh' },
        { name: '摄像头', value: '4800万像素主摄' },
        { name: '网络', value: '5G' }
      ],
      description: `
        <h3>产品特色</h3>
        <p>iPhone 15 Pro Max 采用钛金属设计，搭载 A17 Pro 芯片，性能更强大。</p>
        <h3>主要功能</h3>
        <ul>
          <li>6.7 英寸 Super Retina XDR 显示屏</li>
          <li>A17 Pro 芯片，性能提升 20%</li>
          <li>4800 万像素主摄，支持 5 倍光学变焦</li>
          <li>钛金属设计，更轻更坚固</li>
          <li>USB-C 接口，传输速度更快</li>
        </ul>
      `,
      reviews: [
        {
          id: 1,
          userName: '张三',
          userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          rating: 5,
          date: '2024-01-15',
          content: '手机非常好用，性能强劲，拍照效果很棒！',
          images: []
        },
        {
          id: 2,
          userName: '李四',
          userAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
          rating: 4,
          date: '2024-01-10',
          content: '整体不错，就是价格有点贵。',
          images: []
        }
      ]
    })

    // 计算属性
    const canPurchase = computed(() => {
      return product.value.stock > 0 && Object.keys(selectedSpecs).length === product.value.specs.length
    })

    // 选择规格
    const selectSpec = (specName, value) => {
      selectedSpecs[specName] = value
    }

    // 加入购物车
    const addToCart = () => {
      if (!canPurchase.value) {
        ElMessage.warning('请选择商品规格')
        return
      }
      ElMessage.success('已加入购物车')
    }

    // 立即购买
    const buyNow = () => {
      if (!canPurchase.value) {
        ElMessage.warning('请选择商品规格')
        return
      }
      router.push('/checkout')
    }

    // 添加到收藏
    const addToWishlist = () => {
      ElMessage.success('已添加到收藏')
    }

    onMounted(() => {
      // 设置默认图片
      currentImage.value = product.value.images[0]
      
      // 设置默认规格
      product.value.specs.forEach(spec => {
        const availableOption = spec.options.find(option => option.available)
        if (availableOption) {
          selectedSpecs[spec.name] = availableOption.value
        }
      })
    })

    return {
      product,
      currentImage,
      quantity,
      activeTab,
      selectedSpecs,
      canPurchase,
      selectSpec,
      addToCart,
      buyNow,
      addToWishlist
    }
  }
}
</script>

<style scoped>
.product-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.product-container {
  display: flex;
  gap: 40px;
  margin-bottom: 40px;
}

.product-images {
  flex: 0 0 400px;
}

.main-image {
  width: 400px;
  height: 400px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.image-thumbnails {
  display: flex;
  gap: 10px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.thumbnail:hover {
  border-color: #409eff;
}

.product-info {
  flex: 1;
}

.product-title {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: #333;
}

.product-rating {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.rating-text {
  color: #ff9500;
  font-weight: bold;
}

.sales-count {
  color: #666;
  font-size: 0.9rem;
}

.product-price {
  margin-bottom: 30px;
}

.current-price {
  font-size: 2rem;
  font-weight: bold;
  color: #e74c3c;
  margin-right: 10px;
}

.original-price {
  font-size: 1.2rem;
  color: #999;
  text-decoration: line-through;
  margin-right: 10px;
}

.discount {
  background: #e74c3c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}

.product-specs {
  margin-bottom: 30px;
}

.spec-item {
  margin-bottom: 20px;
}

.spec-item h3 {
  font-size: 1rem;
  margin-bottom: 10px;
  color: #333;
}

.spec-options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.quantity-selector {
  margin-bottom: 30px;
}

.quantity-selector h3 {
  font-size: 1rem;
  margin-bottom: 10px;
  color: #333;
}

.stock-info {
  margin-left: 15px;
  color: #666;
  font-size: 0.9rem;
}

.purchase-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.service-guarantee {
  display: flex;
  gap: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.guarantee-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 0.9rem;
}

.product-details {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.detail-content {
  line-height: 1.6;
  color: #333;
}

.reviews-section {
  max-height: 500px;
  overflow-y: auto;
}

.review-item {
  border-bottom: 1px solid #eee;
  padding: 20px 0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.review-info {
  flex: 1;
}

.reviewer-name {
  font-weight: bold;
  color: #333;
  margin-right: 10px;
}

.review-date {
  color: #999;
  font-size: 0.9rem;
}

.review-content p {
  margin-bottom: 10px;
  line-height: 1.6;
}

.review-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.review-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
}
</style> 