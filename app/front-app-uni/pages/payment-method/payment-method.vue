<template>
  <view class="payment-method-container">
    <!-- 头部 -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text>←</text>
      </view>
      <view class="title">选择支付方式</view>
    </view>

    <!-- 订单信息 -->
    <view class="order-info">
      <view class="info-item">
        <text class="label">订单金额</text>
        <text class="value price">¥{{ totalAmount }}</text>
      </view>
      <view class="info-item" v-if="orderType === 'direct'">
        <text class="label">商品数量</text>
        <text class="value">{{ quantity }}件</text>
      </view>
      <view class="info-item" v-if="orderType === 'cart'">
        <text class="label">商品数量</text>
        <text class="value">{{ cartItemCount }}件</text>
      </view>
    </view>

    <!-- 支付方式列表 -->
    <view class="payment-methods">
      <view class="section-title">选择支付方式</view>
      <view class="method-list">
        <view 
          class="method-item" 
          v-for="method in paymentMethods" 
          :key="method.id"
          :class="{ selected: selectedMethod === method.id }"
          @click="selectMethod(method.id)"
        >
          <view class="method-left">
            <view class="method-icon">
              <text :class="method.icon"></text>
            </view>
            <view class="method-info">
              <view class="method-name">{{ method.name }}</view>
              <view class="method-desc">{{ method.description }}</view>
            </view>
          </view>
          <view class="method-right">
            <view class="radio-btn" :class="{ active: selectedMethod === method.id }">
              <text class="radio-inner"></text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部确认按钮 -->
    <view class="bottom-bar">
      <view class="total-info">
        <text>应付金额：</text>
        <text class="total-price">¥{{ totalAmount }}</text>
      </view>
      <view class="confirm-btn" 
        @click="confirmPayment" 
        :class="{ disabled: !selectedMethod }">
        确认支付
      </view>
    </view>
  </view>
</template>

<script>
import { getUserId } from '@/src/utils/auth.js'
import request from '@/src/utils/request.js'

export default {
  name: 'PaymentMethod',
  data() {
    return {
      orderType: 'direct', // 'cart' 或 'direct'
      totalAmount: '0.00',
      quantity: 1,
      cartItemCount: 0,
      selectedMethod: 'wechat',
      pageOptions: {}, // 页面参数
      paymentMethods: [
        {
          id: 'wechat',
          name: '微信支付',
          description: '推荐使用微信支付',
          icon: 'wechat-icon'
        },
        {
          id: 'alipay',
          name: '支付宝',
          description: '安全便捷的支付方式',
          icon: 'alipay-icon'
        }
      ]
    }
  },
  onLoad(options) {
    // 获取页面参数
    this.pageOptions = options
    this.loadOrderInfo()
  },
  methods: {
    goBack() {
      uni.navigateBack({
        delta: 1
      })
    },

    loadOrderInfo() {
      const query = this.pageOptions
      
      // 判断订单类型
      if (query.cart_items) {
        this.orderType = 'cart'
        this.cartItemCount = query.cart_items.split(',').length
      } else {
        this.orderType = 'direct'
        this.quantity = parseInt(query.quantity) || 1
      }
      
      this.totalAmount = query.total_amount || '0.00'
    },

    selectMethod(methodId) {
      this.selectedMethod = methodId
    },

    async confirmPayment() {
      if (!this.selectedMethod) {
        uni.showToast({
          title: '请选择支付方式',
          icon: 'error'
        })
        return
      }

      try {
        const query = this.pageOptions
        
        // 获取默认地址
        let addressId = parseInt(query.address_id) || 1
        if (!query.address_id) {
          try {
            const addressResponse = await request.get('/api/app/address/default', {
              params: { user_id: getUserId() }
            })
            if (addressResponse.data.code === 200 && addressResponse.data.data) {
              addressId = addressResponse.data.data.id
            }
          } catch (error) {
            console.warn('获取默认地址失败，使用默认值:', error)
          }
        }
        
        // 创建订单
        const orderData = {
          user_id: getUserId(),
          payment_method: this.selectedMethod,
          address_id: addressId
        }
        
        if (this.orderType === 'cart') {
          orderData.cart_items = query.cart_items.split(',').map(id => parseInt(id))
        } else {
          orderData.direct_buy = {
            product_id: parseInt(query.product_id),
            quantity: parseInt(query.quantity),
          }
          
          if (query.spec_combination_id) {
            orderData.direct_buy.spec_combination_id = parseInt(query.spec_combination_id)
          }
        }

        console.log('创建订单数据:', orderData)
        const response = await request.post('/api/app/order/', orderData)
        
        if (response.data.code === 200) {
          console.log('订单创建成功:', response.data)
          // 跳转到支付页面
          uni.navigateTo({
            url: `/pages/payment/payment?order_id=${response.data.data.order_id}&order_number=${response.data.data.order_number}&total_amount=${response.data.data.total_amount}&payment_method=${this.selectedMethod}`
          })
        } else {
          console.error('创建订单失败:', response.data)
          uni.showToast({
            title: response.data.message || '创建订单失败',
            icon: 'error'
          })
        }
      } catch (error) {
        console.error('创建订单失败:', error)
        uni.showToast({
          title: '创建订单失败，请重试',
          icon: 'error'
        })
      }
    }
  }
}
</script>

<style scoped>
.payment-method-container {
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

.order-info {
  background: white;
  margin: 10px;
  border-radius: 8px;
  padding: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  font-size: 14px;
}

.value {
  color: #333;
  font-size: 14px;
}

.price {
  color: #ff4757;
  font-weight: bold;
  font-size: 18px;
}

.payment-methods {
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

.method-list {
  margin-top: 10px;
}

.method-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.method-item:last-child {
  border-bottom: none;
}

.method-item:hover {
  background-color: #f8f9fa;
}

.method-item.selected {
  background-color: #fff5f5;
}

.method-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.method-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 20px;
}

.wechat-icon {
  color: #07c160;
}

.alipay-icon {
  color: #1677ff;
}

.method-info {
  flex: 1;
}

.method-name {
  font-size: 16px;
  color: #333;
  margin-bottom: 4px;
  font-weight: 500;
}

.method-desc {
  font-size: 12px;
  color: #999;
}

.method-right {
  margin-left: 15px;
}

.radio-btn {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.radio-btn.active {
  border-color: #ff4757;
  background-color: #ff4757;
}

.radio-inner {
  width: 8px;
  height: 8px;
  background-color: white;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s;
}

.radio-btn.active .radio-inner {
  opacity: 1;
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

.confirm-btn {
  background: #ff4757;
  color: white;
  padding: 12px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.confirm-btn:hover {
  background: #ff3742;
}

.confirm-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
}

.confirm-btn.disabled:hover {
  background: #ccc;
}
</style> 