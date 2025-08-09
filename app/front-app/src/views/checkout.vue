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
        <div class="address-arrow">›</div>
      </div>
      <div class="no-address" v-else>
        <span>请选择收货地址</span>
        <div class="address-arrow">›</div>
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
            <img :src="product.product_image || '/static/default-product.png'" />
          </div>
          <div class="product-info">
            <div class="product-name">{{ product.product_name }}</div>
            <div class="product-price">¥{{ formatPrice(product.price) }}</div>
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
        <span class="value">¥{{ formatPrice(totalAmount) }}</span>
      </div>
      <div class="info-item">
        <span class="label">运费</span>
        <span class="value">¥0.00</span>
      </div>
      <div class="info-item total">
        <span class="label">实付金额</span>
        <span class="value">¥{{ formatPrice(totalAmount) }}</span>
      </div>
    </div>

    <!-- 支付方式 -->
    <div class="payment-method-section">
      <div class="section-title">选择支付方式</div>
      <div class="payment-methods">
        <div 
          class="payment-item"
          :class="{ selected: selectedMethod === 'alipay' }"
          @click="selectedMethod = 'alipay'"
        >
          <div class="method-left">
            <span class="brand-badge alipay">A</span>
            <span class="method-name">支付宝</span>
          </div>
          <div class="method-right">
            <span class="checkmark" :class="{ active: selectedMethod === 'alipay' }"></span>
          </div>
        </div>
        <div 
          class="payment-item"
          :class="{ selected: selectedMethod === 'wechat' }"
          @click="selectedMethod = 'wechat'"
        >
          <div class="method-left">
            <span class="brand-badge wechat">W</span>
            <span class="method-name">微信支付</span>
          </div>
          <div class="method-right">
            <span class="checkmark" :class="{ active: selectedMethod === 'wechat' }"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部提交按钮 -->
    <div class="bottom-bar">
      <div class="total-info">
        <span>合计：</span>
        <span class="total-price">¥{{ formatPrice(totalAmount) }}</span>
      </div>
      <div class="submit-btn" @click="handleCheckout" :class="{ disabled: !selectedAddress }">
        去结算
      </div>
    </div>

    <!-- 支付确认弹窗（模拟三方支付） -->
    <div class="payment-modal" v-if="showPaymentModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>确认支付</h3>
        </div>
        <div class="modal-body">
          <p>支付金额：¥{{ formatPrice(currentTotalAmount) }}</p>
          <p>支付方式：{{ selectedMethod === 'wechat' ? '微信支付' : '支付宝' }}</p>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="cancelPayment" :disabled="isProcessing">取消</button>
          <button class="confirm-btn" @click="processPayment" :disabled="isProcessing">确认支付</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import request from '../utils/request.js'
import AddressService from '../services/addressService.js'
import { getUserId } from '@/utils/auth.js'

export default {
  name: 'Checkout',
  data() {
    return {
      user_id: getUserId(),
      selectedAddress: null,
      products: [],
      totalAmount: 0,
      cartItemIds: [],
      directBuyProduct: null,
      selectedMethod: 'wechat',
      // 模拟三方支付
      showPaymentModal: false,
      isProcessing: false,
      currentOrderNumbers: [],
      currentTotalAmount: 0
    }
  },
  mounted() {
    this.loadCheckoutInfo()
  },
  activated() {
    // 当页面重新激活时（比如从地址选择页面返回），重新加载地址信息
    this.loadAddressInfo()
    // 若地址选择页选中即返回，这里优先从本地读取回显
    const cached = AddressService.getSelectedAddress()
    if (cached) {
      this.selectedAddress = cached
    }
  },

  methods: {
    orderNumbersPreview() {
      if (!this.currentOrderNumbers || this.currentOrderNumbers.length <= 1) return ''
      const list = this.currentOrderNumbers.slice(0, 2)
      const more = this.currentOrderNumbers.length - list.length
      return `${list.join(', ')}${more > 0 ? ` 等${this.currentOrderNumbers.length}单` : ''}`
    },
    formatPrice(value) {
      const num = Number(value || 0)
      return num.toFixed(2)
    },
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
        // 透传地址（若商品详情弹窗中已选择地址）
        const { address_id } = this.$route.query
        if (address_id) {
          params.address_id = address_id
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
        
        // 如果路由透传了地址，则优先使用；否则取默认地址
        if (address_id) {
          // 透传仅带了 id，这里仍从缓存/后端加载完整对象
          const cached = AddressService.getSelectedAddress()
          if (cached && String(cached.id) === String(address_id)) {
            this.selectedAddress = cached
          } else {
            this.selectedAddress = await AddressService.getDefaultAddress(this.user_id)
          }
        } else {
          this.selectedAddress = await AddressService.getDefaultAddress(this.user_id)
        }
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
    
    // 去结算：创建订单 -> 弹窗模拟支付
    async handleCheckout() {
      if (!this.selectedAddress) {
        alert('请选择收货地址')
        return
      }

      try {
        const orderData = {
          user_id: this.user_id,
          address_id: this.selectedAddress.id,
          payment_method: this.selectedMethod
        }

        const { cart_items, product_id, quantity, spec_combination_id } = this.$route.query
        if (cart_items) {
          orderData.cart_items = cart_items.split(',').map(id => parseInt(id))
        } else if (product_id) {
          orderData.direct_buy = {
            product_id: parseInt(product_id),
            quantity: parseInt(quantity) || 1
          }
          if (spec_combination_id) {
            orderData.direct_buy.spec_combination_id = parseInt(spec_combination_id)
          }
        }

        const res = await request.post('/api/app/order/', orderData)
        if (res.data.code !== 200) {
          throw new Error(res.data.message || '下单失败')
        }

        const payload = res.data.data
        // 兼容老结构与新结构
        if (payload.orders && Array.isArray(payload.orders)) {
          this.currentOrderNumbers = payload.orders.map(o => o.order_number)
          this.currentTotalAmount = payload.total_amount || payload.orders.reduce((s,o)=>s+Number(o.total_amount||0),0)
        } else {
          this.currentOrderNumbers = [payload.order_number]
          this.currentTotalAmount = payload.total_amount
        }
        this.showPaymentModal = true
      } catch (error) {
        console.error('去结算失败:', error)
        alert('去结算失败：' + (error.message || '请稍后重试'))
      }
    },

    cancelPayment() {
      if (this.isProcessing) return
      this.showPaymentModal = false
    },

    async processPayment() {
      if (this.isProcessing) return
      if (!this.currentOrderNumbers || this.currentOrderNumbers.length === 0) return

      this.isProcessing = true
      try {
        // 逐单支付成功回调（模拟统一支付拆单）
        for (const on of this.currentOrderNumbers) {
          const payRes = await request.post(`/api/app/order/${on}/pay-success`, {
            user_id: this.user_id,
            payment_method: this.selectedMethod
          })
          if (payRes.data.code !== 200) {
            throw new Error(payRes.data.message || '支付失败')
          }
        }
        {
          this.showPaymentModal = false
          this.$router.push({
            path: '/pay-result',
            query: {
              status: 'success',
              order_number: this.currentOrderNumbers.join(','),
              total_amount: this.currentTotalAmount
            }
          })
        }
      } catch (err) {
        console.error('支付失败:', err)
        alert('支付失败：' + (err.message || '请稍后重试'))
      } finally {
        this.isProcessing = false
      }
    }
  }
}
</script>

<style scoped>
.checkout-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: constant(safe-area-inset-bottom, 80px);
  padding-bottom: env(safe-area-inset-bottom, 80px);
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
.order-info-section,
.payment-method-section {
  background: #fff;
  margin: 12px;
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #222;
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
  color: #cbd5e1;
  font-size: 14px;
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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
  padding: 12px 0;
  border-bottom: 1px dashed #eee;
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 64px;
  height: 64px;
  margin-right: 12px;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.product-info {
  flex: 1;
  min-width: 0; /* 关键：允许子元素在 flex 容器中收缩，ellipsis 才能生效 */
}

.product-name {
  font-size: 14px;
  color: #1f2d3d;
  margin-bottom: 4px;
  line-height: 1.35;
  display: block; /* 让 ellipsis 更稳定生效 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.product-price {
  font-size: 15px;
  color: #ff4d4f;
  font-weight: 600;
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
  border-top: 1px solid #f5f5f5;
  margin-top: 8px;
  padding-top: 12px;
  font-weight: 700;
  font-size: 16px;
}

.label {
  color: #6b7280;
}

.value {
  color: #111827;
}

.total .value {
  color: #ff4d4f;
  font-size: 18px;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 12px 16px;
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
  font-size: 20px;
  color: #ff4d4f;
  font-weight: 700;
}

.submit-btn {
  background: linear-gradient(135deg, #ff7a45, #ff4d4f);
  color: white;
  padding: 12px 20px;
  border-radius: 24px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 6px 12px rgba(255,77,79,0.24);
  transition: transform .06s ease-in-out;
}

.submit-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 支付确认弹窗样式（与 payment.vue 保持一致风格） */
.payment-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  overflow: hidden;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  text-align: center;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-body p {
  margin: 10px 0;
  color: #666;
}

.modal-footer {
  display: flex;
  border-top: 1px solid #eee;
}

.cancel-btn, .confirm-btn {
  flex: 1;
  padding: 15px;
  border: none;
  font-size: 16px;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.confirm-btn {
  background: #ff4757;
  color: white;
}

/* 支付方式视觉优化 */
.payment-methods {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.payment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 12px 14px;
  transition: border-color .15s ease, box-shadow .15s ease;
}

.payment-item.selected {
  border-color: #ff4d4f;
  box-shadow: 0 0 0 2px rgba(255,77,79,0.12);
}

.method-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-badge {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #fff;
  font-weight: 700;
  font-size: 14px;
}

.brand-badge.alipay { background: linear-gradient(135deg, #2e7cf6, #1f6fe5); }
.brand-badge.wechat { background: linear-gradient(135deg, #20c997, #16a34a); }

.method-name {
  font-size: 14px;
  color: #111827;
}

.radio {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #d1d5db;
  position: relative;
}

.radio.active {
  border-color: #ff4d4f;
}

.radio.active::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background: #ff4d4f;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.submit-btn:active {
  transform: scale(0.98);
}
</style> 