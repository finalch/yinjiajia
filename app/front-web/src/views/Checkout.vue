<template>
  <div class="checkout">
    <h1 class="page-title">订单结算</h1>
    
    <el-row :gutter="20">
      <el-col :span="16">
        <!-- 收货地址 -->
        <el-card class="address-section">
          <template #header>
            <span>收货地址</span>
            <el-button type="primary" size="small" style="float: right;">添加新地址</el-button>
          </template>
          <div class="address-list">
            <div class="address-item" v-for="address in addresses" :key="address.id">
              <el-radio v-model="selectedAddress" :label="address.id">
                <div class="address-info">
                  <p><strong>{{ address.name }}</strong> {{ address.phone }}</p>
                  <p>{{ address.province }} {{ address.city }} {{ address.district }} {{ address.detail }}</p>
                </div>
              </el-radio>
            </div>
          </div>
        </el-card>
        
        <!-- 商品清单 -->
        <el-card class="order-items">
          <template #header>
            <span>商品清单</span>
          </template>
          <div class="item-list">
            <div class="item" v-for="item in orderItems" :key="item.id">
              <el-image :src="item.image" class="item-image" />
              <div class="item-info">
                <h4>{{ item.name }}</h4>
                <p class="item-specs">{{ item.specs }}</p>
              </div>
              <div class="item-price">¥{{ item.price }}</div>
              <div class="item-quantity">x{{ item.quantity }}</div>
              <div class="item-subtotal">¥{{ (item.price * item.quantity).toFixed(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- 订单摘要 -->
        <el-card class="order-summary">
          <template #header>
            <span>订单摘要</span>
          </template>
          <div class="summary-item">
            <span>商品总额</span>
            <span>¥{{ subtotal.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span>运费</span>
            <span>¥{{ shipping.toFixed(2) }}</span>
          </div>
          <div class="summary-item total">
            <span>应付总额</span>
            <span class="total-price">¥{{ total.toFixed(2) }}</span>
          </div>
          
          <el-button type="primary" size="large" @click="submitOrder" class="submit-btn">
            提交订单
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Checkout',
  setup() {
    const router = useRouter()
    const selectedAddress = ref(1)
    
    const addresses = ref([
      {
        id: 1,
        name: '张三',
        phone: '13800138000',
        province: '北京市',
        city: '北京市',
        district: '朝阳区',
        detail: '三里屯街道1号'
      },
      {
        id: 2,
        name: '李四',
        phone: '13900139000',
        province: '上海市',
        city: '上海市',
        district: '浦东新区',
        detail: '陆家嘴街道2号'
      }
    ])
    
    const orderItems = ref([
      {
        id: 1,
        name: 'Apple iPhone 15 Pro',
        specs: '暗紫色 256GB',
        price: 7999,
        quantity: 1,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2,
        name: 'AirPods Pro',
        specs: '白色',
        price: 1899,
        quantity: 2,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      }
    ])
    
    const subtotal = computed(() => {
      return orderItems.value.reduce((total, item) => total + (item.price * item.quantity), 0)
    })
    
    const shipping = computed(() => {
      return subtotal.value > 99 ? 0 : 10
    })
    
    const total = computed(() => {
      return subtotal.value + shipping.value
    })
    
    const submitOrder = () => {
      ElMessage.success('订单提交成功')
      router.push('/order-success')
    }
    
    return {
      selectedAddress,
      addresses,
      orderItems,
      subtotal,
      shipping,
      total,
      submitOrder
    }
  }
}
</script>

<style scoped>
.checkout {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: #333;
}

.address-section,
.order-items,
.order-summary {
  margin-bottom: 20px;
}

.address-item {
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.address-info p {
  margin: 5px 0;
  color: #666;
}

.item-list .item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.item-image {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  margin-right: 15px;
}

.item-info {
  flex: 1;
}

.item-info h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.item-specs {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.item-price,
.item-quantity,
.item-subtotal {
  margin: 0 20px;
  color: #333;
}

.item-subtotal {
  font-weight: bold;
  color: #e74c3c;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px 0;
}

.summary-item.total {
  border-top: 1px solid #eee;
  padding-top: 15px;
  font-weight: bold;
}

.total-price {
  color: #e74c3c;
  font-size: 1.2rem;
}

.submit-btn {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
  margin-top: 20px;
}
</style> 