<template>
  <view class="order-list-container">
    <!-- 头部 -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text>←</text>
      </view>
      <view class="title">我的订单</view>
    </view>

    <!-- 状态筛选 -->
    <view class="status-filter">
      <view 
        class="filter-item" 
        v-for="status in statusOptions" 
        :key="status.value"
        :class="{ active: currentStatus === status.value }"
        @click="selectStatus(status.value)"
      >
        {{ status.label }}
      </view>
    </view>

    <!-- 订单列表 -->
    <view class="order-list" v-if="orders.length > 0">
      <view 
        class="order-item" 
        v-for="order in orders" 
        :key="order.id"
        @click="viewOrderDetail(order.id)"
      >
        <!-- 商家分组列表（每个商家显示前2张图 + 件数 + 小计） -->
        <view class="merchant-groups">
          <view class="merchant-card" v-for="group in groupItemsByMerchant(order.items)" :key="group.key">
            <view class="merchant-header">
              <view class="row-top">
                <view class="merchant-name">{{ group.merchantName }}</view>
                <view class="order-status" :class="getStatusClass(order.status)">{{ order.status_text }}</view>
              </view>
              <view class="merchant-meta">
                <text>共{{ group.totalCount }}件</text>
                <text class="split">|</text>
                <text>小计 ¥{{ formatPrice(group.totalAmount) }}</text>
              </view>
            </view>
            <view class="merchant-body">
              <view class="row-preview">
                <view class="preview-left">
                <template v-if="group.items.length === 1">
                  <view class="preview single">
                    <image :src="group.items[0].product_image || '/static/default-product.png'" />
                  </view>
                  <view class="single-info">
                    <view class="single-name">{{ group.items[0].product_name }}</view>
                    <view class="single-quantity">×{{ group.items[0].quantity }}</view>
                  </view>
                </template>
                <template v-else>
                  <view class="preview-images">
                    <view class="preview" v-for="(img, idx) in group.previewImages" :key="idx">
                      <image :src="img" />
                    </view>
                  </view>
                </template>
                </view>
                <view class="summary">
                  <view class="count">共{{ group.totalCount }}件</view>
                  <view class="amount">合计 ¥{{ formatPrice(group.totalAmount) }}</view>
                </view>
              </view>
              <view class="row-actions">
                <view class="order-actions">
                  <button v-if="order.status === 'pending'" class="action-btn primary" @click.stop="goPay(order)">去支付</button>
                  <button v-if="order.status === 'pending' || order.status === 'paid'" class="action-btn secondary" @click.stop="cancelOrder(order)">取消订单</button>
                  <button v-if="order.status === 'shipped' || order.status === 'delivered'" class="action-btn secondary" @click.stop="viewLogistics(order)">查看物流</button>
                  <button v-if="order.status === 'shipped' || order.status === 'delivered'" class="action-btn primary" @click.stop="confirmReceipt(order)">确认收货</button>
                  <button v-if="order.status === 'delivered' || order.status === 'completed'" class="action-btn secondary" @click.stop="afterSales(order)">售后</button>
                </view>
              </view>
            </view>
          </view>
        </view>

        <!-- 订单底部 -->
        <!-- <view class="order-footer">
          <view class="order-total">
            <text>共{{ getTotalQuantity(order.items) }}件商品</text>
            <text class="total-price">合计：¥{{ order.total_amount }}</text>
          </view>
        </view> -->
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-text">暂无订单</view>
      <button class="go-shop-btn" @click="goShop">去购物</button>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasNextPage && orders.length > 0">
      <button class="load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </view>
  </view>
</template>

<script>
import { getUserId } from '@/src/utils/auth.js'
import request from '@/src/utils/request.js'

export default {
  name: 'MyOrder',
  data() {
    return {
      user_id: getUserId(),
      currentStatus: '',
      currentPage: 1,
      perPage: 10,
      orders: [],
      loading: false,
      hasNextPage: false,
      statusOptions: [
        { label: '全部', value: '' },
        { label: '待付款', value: 'pending' },
        { label: '已付款', value: 'paid' },
        { label: '已发货', value: 'shipped' },
        { label: '已完成', value: 'completed' },
        { label: '已取消', value: 'cancelled' },
        { label: '已退款', value: 'refunded' }
      ]
    }
  },
  mounted() {
    this.loadOrders()
  },
  activated() {
    // 当页面重新激活时（比如从支付页面返回），刷新订单列表
    this.loadOrders()
  },
  methods: {
    // 金额格式化
    formatPrice(val) {
      const n = Number(val || 0)
      return n.toFixed(2)
    },

    // 根据商家分组；若后端暂未返回商家信息，则聚合为单组
    groupItemsByMerchant(items = []) {
      if (!items || items.length === 0) return []
      const groupsMap = new Map()
      items.forEach(it => {
        const key = it.merchant_id || 'unknown'
        const name = it.merchant_name || '商家'
        if (!groupsMap.has(key)) {
          groupsMap.set(key, {
            key,
            merchantName: name,
            items: [],
            totalAmount: 0,
            totalCount: 0
          })
        }
        const g = groupsMap.get(key)
        g.items.push(it)
        g.totalAmount += Number(it.subtotal || (it.price || 0) * (it.quantity || 0))
        g.totalCount += Number(it.quantity || 0)
      })
      const groups = Array.from(groupsMap.values()).map(g => {
        const preview = g.items.slice(0, 2).map(x => x.product_image || '/static/default-product.png')
        return { ...g, previewImages: preview }
      })
      return groups
    },
    // 返回上一页
    goBack() {
      uni.navigateBack({
        delta: 1
      })
    },

    // 选择状态筛选
    selectStatus(status) {
      this.currentStatus = status
      this.currentPage = 1
      this.orders = []
      this.loadOrders()
    },

    // 加载订单列表
    async loadOrders() {
      if (this.loading) return
      
      this.loading = true
      try {
        const params = {
          user_id: this.user_id,
          page: this.currentPage,
          per_page: this.perPage
        }
        
        if (this.currentStatus) {
          params.status = this.currentStatus
        }

        const response = await request.get('/api/app/order/', { params })
        
        if (response.data.code === 200) {
          const data = response.data.data
          if (this.currentPage === 1) {
            this.orders = data.list
          } else {
            this.orders = [...this.orders, ...data.list]
          }
          
          this.hasNextPage = data.pagination.has_next
        }
      } catch (error) {
        console.error('加载订单列表失败:', error)
        uni.showToast({
          title: '加载订单列表失败',
          icon: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    // 加载更多
    loadMore() {
      if (this.hasNextPage && !this.loading) {
        this.currentPage++
        this.loadOrders()
      }
    },

    // 格式化日期
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      
      return `${year}-${month}-${day} ${hours}:${minutes}`
    },

    // 获取状态样式类
    getStatusClass(status) {
      const statusClassMap = {
        'pending': 'status-pending',
        'paid': 'status-paid',
        'shipped': 'status-shipped',
        'completed': 'status-completed',
        'cancelled': 'status-cancelled',
        'refunded': 'status-refunded'
      }
      return statusClassMap[status] || 'status-default'
    },

    // 获取商品总数量
    getTotalQuantity(items) {
      return items.reduce((total, item) => total + item.quantity, 0)
    },

    // 获取规格文本（简化处理）
    getSpecText(specCombinationId) {
      // 这里可以根据spec_combination_id获取规格信息
      // 暂时返回默认文本
      return '默认规格'
    },

    // 查看订单详情
    viewOrderDetail(orderId) {
      uni.navigateTo({
        url: `/pages/order-detail/order-detail?id=${orderId}`
      })
    },

    // 去支付
    goPay(order) {
      uni.navigateTo({
        url: `/pages/payment/payment?order_number=${order.order_number}&total_amount=${order.total_amount}`
      })
    },

    // 取消订单
    async cancelOrder(order) {
      uni.showModal({
        title: '确认取消',
        content: '确定取消该订单吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              const res = await request.post(`/api/app/order/${order.id}/cancel`, null, { params: { user_id: this.user_id } })
              if (res.data && res.data.code === 200) {
                uni.showToast({
                  title: '订单已取消',
                  icon: 'success'
                })
                this.currentPage = 1
                this.orders = []
                await this.loadOrders()
              } else {
                uni.showToast({
                  title: res.data?.message || '取消失败',
                  icon: 'error'
                })
              }
            } catch (e) {
              console.error('取消订单失败', e)
              uni.showToast({
                title: '取消失败',
                icon: 'error'
              })
            }
          }
        }
      })
    },

    // 售后（占位）
    afterSales(order) {
      uni.showToast({
        title: '售后功能开发中...',
        icon: 'none'
      })
    },

    // 查看物流
    viewLogistics(order) {
      if (order.logistics) {
        const logistics = order.logistics
        const message = `物流公司：${logistics.carrier}\n物流单号：${logistics.tracking_number}\n物流状态：${logistics.status_text || logistics.status}`
        uni.showModal({
          title: '物流信息',
          content: message,
          showCancel: false
        })
      } else {
        uni.showToast({
          title: '暂无物流信息',
          icon: 'none'
        })
      }
    },

    // 确认收货
    async confirmReceipt(order) {
      uni.showModal({
        title: '确认收货',
        content: '确认已收到货物吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              const res = await request.post(`/api/app/order/${order.id}/confirm-receipt`, {
                user_id: this.user_id
              })
              if (res.data && res.data.code === 200) {
                uni.showToast({
                  title: '确认收货成功',
                  icon: 'success'
                })
                // 刷新订单列表
                this.currentPage = 1
                this.orders = []
                await this.loadOrders()
              } else {
                uni.showToast({
                  title: res.data?.message || '确认收货失败',
                  icon: 'error'
                })
              }
            } catch (e) {
              console.error('确认收货失败', e)
              uni.showToast({
                title: '确认收货失败',
                icon: 'error'
              })
            }
          }
        }
      })
    },

    // 去购物
    goShop() {
      uni.switchTab({
        url: '/pages/index/index'
      })
    }
  }
}
</script>

<style scoped>
.order-list-container {
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

/* 状态筛选样式 */
.status-filter {
  background: white;
  display: flex;
  padding: 15px;
  overflow-x: auto;
  border-bottom: 1px solid #eee;
}

.filter-item {
  padding: 8px 16px;
  margin-right: 10px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s;
  border: 1px solid #ddd;
  color: #666;
}

.filter-item.active {
  background: #ff4757;
  color: white;
  border-color: #ff4757;
}

/* 订单列表样式 */
.order-list {
  padding: 10px;
}

.order-item {
  background: white;
  border-radius: 8px;
  margin-bottom: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.3s;
}

.order-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.order-info {
  display: flex;
  flex-direction: column;
}

.order-number {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.order-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.order-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-paid {
  background: #d1ecf1;
  color: #0c5460;
}

.status-shipped {
  background: #d4edda;
  color: #155724;
}

.status-completed {
  background: #d1ecf1;
  color: #0c5460;
}

.status-cancelled {
  background: #f8d7da;
  color: #721c24;
}

.status-refunded {
  background: #e2e3e5;
  color: #6c757d;
}

/* 商家分组卡片 */
.merchant-groups { padding: 10px 15px 15px; }
.merchant-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 10px;
}
.merchant-header { padding: 12px 12px 8px; }
.merchant-header .row-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.merchant-name { font-weight: 600; color: #333; }
.merchant-meta { color: #666; font-size: 12px; }
.merchant-meta .split { margin: 0 6px; color: #ddd; }
.merchant-body { display: flex; flex-direction: column; gap: 8px; padding: 0 12px 12px; }
.row-preview { display: flex; align-items: center; gap: 12px; }
.preview-left { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.preview-images { display: flex; gap: 8px; }
.preview { width: 48px; height: 48px; border-radius: 6px; overflow: hidden; background: #f5f5f5; }
.preview img { width: 100%; height: 100%; object-fit: cover; }
.single-info { display: flex; flex-direction: column; gap: 6px; }
.single-name { font-size: 14px; color: #333; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.single-quantity { font-size: 12px; color: #999; }
.summary { margin-left: auto; text-align: right; }
.summary .count { font-size: 12px; color: #666; }
.summary .amount { font-size: 14px; font-weight: 600; color: #ff4757; }
.row-actions { display: flex; }
.order-actions { display: flex; gap: 8px; margin-left: auto; }

/* 订单底部样式 */
.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.order-total {
  font-size: 14px;
  color: #666;
}

.total-price {
  color: #ff4757;
  font-weight: bold;
  margin-left: 10px;
}

.order-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.primary {
  background: #ff4757;
  color: white;
}

.action-btn.primary:hover {
  background: #ff3742;
}

.action-btn.secondary {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.action-btn.secondary:hover {
  background: #f5f5f5;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.empty-text {
  font-size: 16px;
  color: #999;
  margin-bottom: 30px;
}

.go-shop-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.go-shop-btn:hover {
  background: #ff3742;
}

/* 加载更多样式 */
.load-more {
  text-align: center;
  padding: 20px;
}

.load-more-btn {
  background: white;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>