<template>
  <div class="order-list-container">
    <!-- 头部 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span>←</span>
      </div>
      <div class="title">我的订单</div>
    </div>

    <!-- 状态筛选 -->
    <div class="status-filter">
      <div 
        class="filter-item" 
        v-for="status in statusOptions" 
        :key="status.value"
        :class="{ active: currentStatus === status.value }"
        @click="selectStatus(status.value)"
      >
        {{ status.label }}
      </div>
    </div>

    <!-- 订单列表 -->
    <div class="order-list" v-if="orders.length > 0">
      <div 
        class="order-item" 
        v-for="order in orders" 
        :key="order.id"
        @click="viewOrderDetail(order.id)"
      >
        <!-- 订单头部 -->
        <div class="order-header">
          <div class="order-info">
            <span class="order-number">订单号：{{ order.order_number }}</span>
            <span class="order-time">{{ formatDate(order.created_at) }}</span>
          </div>
          <div class="order-status" :class="getStatusClass(order.status)">
            {{ order.status_text }}
          </div>
        </div>

        <!-- 商品列表 -->
        <div class="product-list">
          <div 
            class="product-item" 
            v-for="item in order.items" 
            :key="item.id"
          >
            <div class="product-image">
              <img :src="item.product_image || '/static/default-product.png'" :alt="item.product_name" />
            </div>
            <div class="product-info">
              <div class="product-name">{{ item.product_name }}</div>
              <div class="product-spec" v-if="item.spec_combination_id">
                规格：{{ getSpecText(item.spec_combination_id) }}
              </div>
              <div class="product-price">
                <span class="price">¥{{ item.price }}</span>
                <span class="quantity">×{{ item.quantity }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 订单底部 -->
        <div class="order-footer">
          <div class="order-total">
            <span>共{{ getTotalQuantity(order.items) }}件商品</span>
            <span class="total-price">合计：¥{{ order.total_amount }}</span>
          </div>
          <div class="order-actions">
            <button 
              v-if="order.status === 'pending'" 
              class="action-btn primary"
              @click.stop="goPay(order)"
            >
              去支付
            </button>
            <button 
              v-if="order.status === 'shipped' || order.status === 'delivered'" 
              class="action-btn secondary"
              @click.stop="viewLogistics(order)"
            >
              查看物流
            </button>
            <button 
              class="action-btn secondary"
              @click.stop="viewOrderDetail(order.id)"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <div class="empty-icon">📦</div>
      <div class="empty-text">暂无订单</div>
      <button class="go-shop-btn" @click="goShop">去购物</button>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasNextPage && orders.length > 0">
      <button class="load-more-btn" @click="loadMore" :disabled="loading">
        {{ loading ? '加载中...' : '加载更多' }}
      </button>
    </div>
  </div>
</template>

<script>
import request from '../utils/request.js'

export default {
  name: 'MyOrder',
  data() {
    return {
      user_id: 1, // TODO: 从用户状态获取
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
        { label: '已取消', value: 'cancelled' }
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
    // 返回上一页
    goBack() {
      this.$router.go(-1)
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
        alert('加载订单列表失败')
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
        'cancelled': 'status-cancelled'
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
      this.$router.push({
        path: `/order-detail/${orderId}`
      })
    },

    // 去支付
    goPay(order) {
      this.$router.push({
        path: '/payment',
        query: {
          order_number: order.order_number,
          total_amount: order.total_amount
        }
      })
    },

    // 查看物流
    viewLogistics(order) {
      if (order.logistics) {
        const logistics = order.logistics
        const message = `物流公司：${logistics.carrier}\n物流单号：${logistics.tracking_number}\n物流状态：${logistics.status_text || logistics.status}`
        alert(message)
      } else {
        alert('暂无物流信息')
      }
    },

    // 去购物
    goShop() {
      this.$router.push('/')
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

/* 商品列表样式 */
.product-list {
  padding: 15px;
}

.product-item {
  display: flex;
  margin-bottom: 15px;
}

.product-item:last-child {
  margin-bottom: 0;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 10px;
  flex-shrink: 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 4px;
}

.product-spec {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.product-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  color: #ff4757;
  font-weight: bold;
  font-size: 14px;
}

.quantity {
  color: #999;
  font-size: 12px;
}

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