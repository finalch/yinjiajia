<template>
  <div class="checkout-container">
    <!-- 头部 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span>←</span>
      </div>
      <div class="title">确认订单</div>
    </div>

    <!-- 收货地址 -->
    <div class="address-section" @click="selectAddress">
      <div class="section-title">收货地址</div>
      <div class="address-content" v-if="selectedAddress">
        <div class="address-info">
          <div class="receiver-info">
            <span class="receiver-name">{{ selectedAddress.receiver_name }}</span>
            <span class="receiver-phone">{{ selectedAddress.phone }}</span>
          </div>
          <div class="address-detail">
            {{ selectedAddress.full_address }}
          </div>
        </div>
        <div class="address-arrow">></div>
      </div>
      <div class="no-address" v-else>
        <span>请选择收货地址</span>
        <div class="address-arrow">></div>
      </div>
    </div>

    <!-- 商品信息 -->
    <div class="products-section">
      <div class="section-title">商品信息</div>
      <div class="product-list">
        <div 
          class="product-item" 
          v-for="product in products" 
          :key="product.product_id"
        >
          <div class="product-image">
            <img :src="product.product_image || '/static/default-product.png'" :alt="product.product_name" />
          </div>
          <div class="product-info">
            <div class="product-name">{{ product.product_name }}</div>
            <div class="product-price">¥{{ product.price }}</div>
          </div>
          <div class="product-quantity">
            ×{{ product.quantity }}
          </div>
        </div>
      </div>
    </div>

    <!-- 订单信息 -->
    <div class="order-info-section">
      <div class="section-title">订单信息</div>
      <div class="info-item">
        <span class="label">商品总价</span>
        <span class="value">¥{{ totalAmount }}</span>
      </div>
      <div class="info-item">
        <span class="label">运费</span>
        <span class="value">¥0.00</span>
      </div>
      <div class="info-item total">
        <span class="label">实付金额</span>
        <span class="value">¥{{ totalAmount }}</span>
      </div>
    </div>

    <!-- 底部提交按钮 -->
    <div class="bottom-bar">
      <div class="total-info">
        <span>合计：</span>
        <span class="total-price">¥{{ totalAmount }}</span>
      </div>
      <div class="submit-btn" @click="submitOrder" :class="{ disabled: !selectedAddress }">
        提交订单
      </div>
    </div>
  </div>
</template>

<script>
import request from '../utils/request.js'
import AddressService from '../services/addressService.js'

export default {
  name: 'Checkout',
  data() {
    return {
      user_id: 1, // TODO: 从用户状态获取
      selectedAddress: null,
      products: [],
      totalAmount: 0,
      cartItemIds: [],
      directBuyProduct: null
    }
  },
  mounted() {
    this.loadCheckoutInfo()
  },
  activated() {
    // 当页面重新激活时（比如从地址选择页面返回），重新加载地址信息
    this.loadAddressInfo()
  },

  methods: {
    goBack() {
      this.$router.go(-1)
    },
    
    async loadCheckoutInfo() {
      try {
        // 从路由参数获取商品信息
        const { cart_items, product_id, quantity, spec_combination_id } = this.$route.query
        
        let params = {
          user_id: this.user_id
        }
        
        if (cart_items) {
          params.cart_items = cart_items
        }
        
        if (product_id) {
          params.product_id = product_id
          params.quantity = quantity || 1
          if (spec_combination_id) {
            params.spec_combination_id = spec_combination_id
          }
        }
        
        // 并行获取商品信息和默认地址
        const [checkoutResponse] = await Promise.all([
          request.get('/api/app/order/checkout', { params })
        ])
        
        if (checkoutResponse.data.code === 200) {
          const data = checkoutResponse.data.data
          this.products = data.products
          this.totalAmount = data.total_amount
        }
        
        // 使用AddressService获取默认地址
        this.selectedAddress = await AddressService.getDefaultAddress(this.user_id)
      } catch (error) {
        console.error('加载下单信息失败:', error)
      }
    },
    
    selectAddress() {
      this.$router.push({
        path: '/address-list',
        query: { from: 'checkout' }
      })
    },
    

    
    async loadAddressInfo() {
      // 使用AddressService获取默认地址
      this.selectedAddress = await AddressService.getDefaultAddress(this.user_id)
    },
    
    async submitOrder() {
      console.log('提交订单 - selectedAddress:', this.selectedAddress)
      
      if (!this.selectedAddress) {
        alert('请选择收货地址')
        return
      }
      
      if (!this.selectedAddress.id) {
        console.error('地址ID为空:', this.selectedAddress)
        alert('收货地址信息不完整，请重新选择')
        return
      }
      
      try {
        const orderData = {
          user_id: this.user_id,
          address_id: this.selectedAddress.id
        }
        
        // 判断是购物车商品还是直接购买
        const { cart_items, product_id, quantity, spec_combination_id } = this.$route.query
        
        if (cart_items) {
          orderData.cart_items = cart_items.split(',').map(id => parseInt(id))
        } else if (product_id) {
          orderData.direct_buy = {
            product_id: parseInt(product_id),
            quantity: parseInt(quantity) || 1
          }
          
          // 如果有规格组合ID，添加到直接购买数据中
          if (spec_combination_id) {
            orderData.direct_buy.spec_combination_id = parseInt(spec_combination_id)
          }
        }
        
        console.log('提交订单数据:', orderData)
        console.log('提交订单数据JSON:', JSON.stringify(orderData))
        
        const response = await request.post('/api/app/order/', orderData)
        
        if (response.data.code === 200) {
          // 跳转到支付页面
          this.$router.push({
            path: '/payment',
            query: {
              order_id: response.data.data.order_id,
              order_number: response.data.data.order_number,
              total_amount: response.data.data.total_amount
            }
          })
        }
      } catch (error) {
        console.error('提交订单失败:', error)
        alert('提交订单失败，请重试')
      }
    }
  }
}
</script>

<style scoped>
.checkout-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px;
}

.header {
  background: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
  margin-right: 10px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.address-section,
.products-section,
.order-info-section {
  background: white;
  margin: 10px;
  border-radius: 8px;
  padding: 15px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #333;
}

.address-content,
.no-address {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  cursor: pointer;
}

.address-info {
  flex: 1;
}

.receiver-info {
  margin-bottom: 5px;
}

.receiver-name {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.receiver-phone {
  color: #666;
}

.address-detail {
  color: #333;
  line-height: 1.4;
}

.address-arrow {
  color: #ccc;
  font-size: 16px;
}

.no-address {
  color: #999;
}

.product-list {
  margin-top: 10px;
}

.product-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 60px;
  height: 60px;
  margin-right: 15px;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.product-info {
  flex: 1;
}

.product-name {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  line-height: 1.3;
}

.product-price {
  font-size: 16px;
  color: #ff4757;
  font-weight: bold;
}

.product-quantity {
  color: #666;
  font-size: 14px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.info-item.total {
  border-top: 1px solid #f0f0f0;
  margin-top: 10px;
  padding-top: 15px;
  font-weight: bold;
  font-size: 16px;
}

.label {
  color: #666;
}

.value {
  color: #333;
}

.total .value {
  color: #ff4757;
  font-size: 18px;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #eee;
  z-index: 100;
}

.total-info {
  font-size: 14px;
  color: #666;
}

.total-price {
  font-size: 18px;
  color: #ff4757;
  font-weight: bold;
}

.submit-btn {
  background: #ff4757;
  color: white;
  padding: 12px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}

.submit-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style> 