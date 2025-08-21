<template>
  <view class="checkout-container">
    <!-- 头部 -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text>←</text>
      </view>
      <view class="title">确认订单</view>
    </view>

    <!-- 收货地址 -->
    <view class="address-section" @click="selectAddress">
      <view class="section-title">收货地址</view>
      <view class="address-content" v-if="selectedAddress">
        <view class="address-info">
          <view class="receiver-info">
            <text class="receiver-name">{{ selectedAddress.receiver_name }}</text>
            <text class="receiver-phone">{{ selectedAddress.phone }}</text>
          </view>
          <view class="address-detail">
            {{ selectedAddress.full_address }}
          </view>
        </view>
        <view class="address-arrow">›</view>
      </view>
      <view class="no-address" v-else>
        <text>请选择收货地址</text>
        <view class="address-arrow">›</view>
      </view>
    </view>

    <!-- 商品信息 -->
    <view class="products-section">
      <view class="section-title">商品信息</view>
      <view class="product-list" v-if="products.length > 0">
        <view 
          class="product-item" 
          v-for="product in products" 
          :key="product.product_id"
        >
          <view class="product-image">
            <image 
              :src="product.product_image || '/static/default-product.png'" 
              @error="handleImageError"
              mode="aspectFill"
            />
          </view>
          <view class="product-info">
            <view class="product-name">{{ product.product_name }}</view>
            <view class="product-specs" v-if="product.spec_combination_id || product.spec_combination_name">
              <text class="spec-text">
                {{ product.spec_combination_name || `规格ID: ${product.spec_combination_id}` }}
              </text>
            </view>
            <view class="product-price">¥{{ formatPrice(product.price) }}</view>
          </view>
          <view class="product-right">
            <view class="product-quantity">×{{ product.quantity }}</view>
            <view class="product-subtotal">¥{{ formatPrice(product.subtotal || product.price * product.quantity) }}</view>
          </view>
        </view>
      </view>
      <view class="no-products" v-else>
        <text>暂无商品信息</text>
      </view>
    </view>

    <!-- 订单信息 -->
    <view class="order-info-section">
      <view class="section-title">订单信息</view>
      <view class="info-item">
        <text class="label">商品数量</text>
        <text class="value">{{ totalQuantity }}件</text>
      </view>
      <view class="info-item">
        <text class="label">商品总价</text>
        <text class="value">¥{{ formatPrice(totalAmount) }}</text>
      </view>
      <view class="info-item">
        <text class="label">运费</text>
        <text class="value">¥0.00</text>
      </view>
      <view class="info-item" v-if="discountAmount > 0">
        <text class="label">优惠减免</text>
        <text class="value discount">-¥{{ formatPrice(discountAmount) }}</text>
      </view>
      <view class="info-item total">
        <text class="label">实付金额</text>
        <text class="value">¥{{ formatPrice(finalAmount) }}</text>
      </view>
    </view>

    <!-- 支付方式 -->
    <view class="payment-method-section">
      <view class="section-title">选择支付方式</view>
      <view class="payment-methods">
        <view 
          class="payment-item"
          :class="{ selected: selectedMethod === 'alipay' }"
          @click="selectedMethod = 'alipay'"
        >
          <view class="method-left">
            <view class="brand-badge alipay">
              <text class="brand-icon">支</text>
            </view>
            <view class="method-info">
              <text class="method-name">支付宝</text>
              <text class="method-desc">推荐使用支付宝支付</text>
            </view>
          </view>
          <view class="method-right">
            <view class="checkmark" :class="{ active: selectedMethod === 'alipay' }"></view>
          </view>
        </view>
        <view 
          class="payment-item"
          :class="{ selected: selectedMethod === 'wechat' }"
          @click="selectedMethod = 'wechat'"
        >
          <view class="method-left">
            <view class="brand-badge wechat">
              <text class="brand-icon">微</text>
            </view>
            <view class="method-info">
              <text class="method-name">微信支付</text>
              <text class="method-desc">使用微信扫码支付</text>
            </view>
          </view>
          <view class="method-right">
            <view class="checkmark" :class="{ active: selectedMethod === 'wechat' }"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部提交按钮 -->
    <view class="bottom-bar">
      <view class="total-info">
        <text>合计：</text>
        <text class="total-price">¥{{ formatPrice(finalAmount) }}</text>
      </view>
      <view class="submit-btn" @click="handleCheckout" :class="{ disabled: !selectedAddress }">
        去结算
      </view>
    </view>

    <!-- 支付确认弹窗（模拟三方支付） -->
    <view class="payment-modal" v-if="showPaymentModal">
      <view class="modal-content">
        <view class="modal-header">
          <h3>确认支付</h3>
        </view>
        <view class="modal-body">
          <view class="payment-detail">
            <view class="detail-item">
              <text class="label">商品总价：</text>
              <text class="value">¥{{ formatPrice(totalAmount) }}</text>
            </view>
            <view class="detail-item" v-if="discountAmount > 0">
              <text class="label">优惠减免：</text>
              <text class="value discount">-¥{{ formatPrice(discountAmount) }}</text>
            </view>
            <view class="detail-item">
              <text class="label">运费：</text>
              <text class="value">¥0.00</text>
            </view>
            <view class="detail-item total">
              <text class="label">实付金额：</text>
              <text class="value">¥{{ formatPrice(currentTotalAmount) }}</text>
            </view>
          </view>
          <view class="payment-method-info">
            <text class="label">支付方式：</text>
            <text class="value">{{ selectedMethod === 'wechat' ? '微信支付' : '支付宝' }}</text>
          </view>
        </view>
        <view class="modal-footer">
          <button class="cancel-btn" @click="cancelPayment" :disabled="isProcessing">取消</button>
          <button class="confirm-btn" @click="processPayment" :disabled="isProcessing">确认支付</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '../../src/utils/request.js'
import AddressService from '../../src/services/addressService.js'
import { getUserId } from '../../src/utils/auth.js'

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
      currentTotalAmount: 0,
      // 页面参数
      pageParams: {},
      // 优惠信息
      discountAmount: 0
    }
  },
  computed: {
    // 计算商品总数量
    totalQuantity() {
      const total = this.products.reduce((total, product) => total + (product.quantity || 0), 0)
      return total
    },
    // 计算最终实付金额
    finalAmount() {
      const final = Math.max(0, this.totalAmount - this.discountAmount)
      return final
    }
  },
  onLoad(options) {
    this.pageParams = options
    this.loadCheckoutInfo()
  },
  onShow() {
    // 当页面显示时（比如从地址选择页面返回），重新加载地址信息
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
      uni.navigateBack()
    },
    
    async loadCheckoutInfo() {
      try {
        // 从页面参数获取商品信息
        const { cart_items, product_id, quantity, spec_combination_id } = this.pageParams
        console.log(" ------ >>>>>>>   ", product_id, quantity, spec_combination_id)
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
        const { address_id } = this.pageParams
        if (address_id) {
          params.address_id = address_id
        }
        
        // 优先使用 checkout API 获取商品信息（支持购物车和直接购买）
        try {
          const checkoutResponse = await request.get('/api/app/order/checkout', params)
          
          if (checkoutResponse.data.code === 200) {
            const data = checkoutResponse.data.data
            this.products = data.products || []
            this.totalAmount = data.total_amount || 0
          }
        } catch (checkoutError) {
          console.error('从checkout API加载失败:', checkoutError)
          
          // 如果 checkout API 失败，尝试从购物车API获取商品信息
          if (cart_items) {
            try {
              const cartResponse = await request.get('/api/app/cart/', {
                params: { 
                  user_id: this.user_id
                }
              })
              
              if (cartResponse.data.code === 200) {
                const cartData = cartResponse.data.data
                if (cartData && cartData.items) {
                  // 根据传递的cart_item_ids过滤购物车商品
                  const cartItemIds = cart_items.split(',').map(id => parseInt(id))
                  const selectedItems = cartData.items.filter(item => 
                    cartItemIds.includes(item.id)
                  )
                  
                  this.products = selectedItems.map(item => ({
                    product_id: item.product_id,
                    product_name: item.product_name,
                    product_image: item.product_image,
                    price: item.price,
                    quantity: item.quantity,
                    spec_combination_id: item.spec_combination_id,
                    spec_combination_name: item.spec_combination_name,
                    item_total: item.item_total
                  }))
                  
                  // 计算总金额
                  this.totalAmount = this.products.reduce((total, item) => {
                    return total + (item.item_total || 0)
                  }, 0)
                }
              }
            } catch (cartError) {
              console.error('从购物车加载商品失败:', cartError)
            }
          }
        }

        // 加载地址信息
        await this.loadAddressInfo()
      } catch (error) {
        console.error('加载下单信息失败:', error)
        // 显示错误提示
        uni.showToast({
          title: '加载商品信息失败，请重试',
          icon: 'none'
        })
      }
    },
    
    selectAddress() {
      uni.navigateTo({
        url: '/pages/address-list/address-list?from=checkout'
      })
    },
    

    
    async loadAddressInfo() {
      try {
        // 优先使用从 eventChannel 传递的地址信息
        const { address_id } = this.pageParams
        if (address_id) {
          // 透传仅带了 id，这里仍从缓存/后端加载完整对象
          const cached = AddressService.getSelectedAddress()
          if (cached && String(cached.id) === String(address_id)) {
            this.selectedAddress = cached
            return
          } else {
            // 尝试从后端加载地址详情
            try {
              // 这里可以调用地址详情API
              // const addressResponse = await request.get(`/api/app/address/${address_id}`)
              // if (addressResponse.data.code === 200) {
              //   this.selectedAddress = addressResponse.data.data
              //   return
              // }
            } catch (error) {
              console.error('加载地址详情失败:', error)
            }
          }
        }
        
        // 如果没有指定地址，使用默认地址
        this.selectedAddress = await AddressService.getDefaultAddress(this.user_id)
      } catch (error) {
        console.error('加载地址信息失败:', error)
      }
    },
    
    // 去结算：创建订单 -> 弹窗模拟支付
    async handleCheckout() {
      if (!this.selectedAddress) {
        uni.showToast({
          title: '请选择收货地址',
          icon: 'none'
        })
        return
      }

      try {
        const orderData = {
          user_id: this.user_id,
          address_id: this.selectedAddress.id,
          payment_method: this.selectedMethod
        }

        const { cart_items, product_id, quantity, spec_combination_id } = this.pageParams
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
        
        // 使用最终实付金额
        this.currentTotalAmount = this.finalAmount
        this.showPaymentModal = true
      } catch (error) {
        console.error('去结算失败:', error)
        uni.showToast({
          title: '去结算失败：' + (error.message || '请稍后重试'),
          icon: 'none'
        })
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
                  uni.navigateTo({
          url: `/pages/pay-result/pay-result?status=success&order_number=${this.currentOrderNumbers.join(',')}&total_amount=${this.currentTotalAmount}`
        })
        }
      } catch (err) {
        console.error('支付失败:', err)
        uni.showToast({
          title: '支付失败：' + (err.message || '请稍后重试'),
          icon: 'none'
        })
      } finally {
        this.isProcessing = false
      }
    },

    handleImageError(e) {
      console.error('商品图片加载失败:', e.detail.message);
      // 可以在这里设置一个默认图片或提示
      e.target.src = '/static/default-product.png';
    }
  }
}
</script>

<style scoped>
.checkout-container {
  padding-bottom: 80px; /* 为固定底部栏留出空间 */
  min-height: 100vh;
  background: #f5f5f5;
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
  align-items: flex-start;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s ease;
}

.product-item:hover {
  background-color: #fafafa;
}

.product-item:last-child {
  border-bottom: none;
}

.product-image {
  width: 80px;
  height: 80px;
  margin-right: 16px;
  flex-shrink: 0;
}

.product-image image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.product-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 80px;
}

.product-name {
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 6px;
  line-height: 1.4;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-specs {
  margin: 6px 0;
}

.spec-text {
  font-size: 13px;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  display: inline-block;
}

.product-price {
  font-size: 16px;
  color: #ef4444;
  font-weight: 600;
  margin-top: auto;
}

.product-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  height: 80px;
  margin-left: 12px;
  flex-shrink: 0;
}

.product-quantity {
  color: #6b7280;
  font-size: 14px;
  background-color: #f9fafb;
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.product-subtotal {
  color: #ef4444;
  font-size: 18px;
  font-weight: 700;
  margin-top: auto;
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

.value.discount {
  color: #52c41a;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px)); /* 支持安全区域 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid #eee;
  z-index: 100;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1); /* 添加顶部阴影 */
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

.payment-detail {
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item.total {
  border-top: 2px solid #f0f0f0;
  margin-top: 10px;
  padding-top: 15px;
  font-weight: 700;
  font-size: 16px;
}

.detail-item .label {
  color: #666;
  font-size: 14px;
}

.detail-item .value {
  color: #333;
  font-size: 14px;
}

.detail-item.total .value {
  color: #ff4d4f;
  font-size: 18px;
}

.detail-item .value.discount {
  color: #52c41a;
}

.payment-method-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-top: 1px solid #f0f0f0;
}

.payment-method-info .label {
  color: #666;
  font-size: 14px;
}

.payment-method-info .value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
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
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 0; /* 移除之前的底部边距，因为已经在section上设置了 */
}

.payment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.payment-item:hover {
  border-color: #d1d5db;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.payment-item.selected {
  border-color: #ff4d4f;
  box-shadow: 0 0 0 2px rgba(255,77,79,0.12);
  background: #fff5f5;
}

.method-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.brand-badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  flex-shrink: 0;
}

.brand-icon {
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.brand-badge.alipay { 
  background: linear-gradient(135deg, #1677ff, #0958d9); 
}

.brand-badge.wechat { 
  background: linear-gradient(135deg, #07c160, #06ad56); 
}

.method-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.method-name {
  font-size: 16px;
  color: #111827;
  font-weight: 500;
}

.method-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.method-right {
  display: flex;
  align-items: center;
  margin-left: 16px;
}

.checkmark {
  width: 22px;
  height: 22px;
  border: 2px solid #d1d5db;
  border-radius: 50%;
  position: relative;
  transition: all 0.2s ease;
}

.checkmark.active {
  border-color: #ff4d4f;
  background-color: #ff4d4f;
}

.checkmark.active::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
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

.no-products {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-size: 14px;
}
</style> 