<template>
  <view class="review-container">
    <!-- 头部 -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text>←</text>
      </view>
      <view class="title">商品评价</view>
    </view>

    <!-- 订单信息 -->
    <view class="order-info" v-if="order">
      <view class="order-header">
        <text class="order-number">订单号：{{ order.order_number }}</text>
        <text class="order-status">{{ order.status_text }}</text>
      </view>
    </view>

    <!-- 商品列表 -->
    <view class="product-list" v-if="orderItems.length > 0">
      <view 
        class="product-item" 
        v-for="item in orderItems" 
        :key="item.id"
      >
        <view class="product-info">
          <image 
            class="product-image" 
            :src="item.product_image || '/static/default-product.png'" 
          />
          <view class="product-details">
            <view class="product-name">{{ item.product_name }}</view>
            <view class="product-spec">{{ getSpecText(item.spec_combination_id) }}</view>
            <view class="product-quantity">×{{ item.quantity }}</view>
          </view>
        </view>

        <!-- 评价区域 -->
        <view class="review-section" v-if="!item.is_reviewed">
          <view class="rating-section">
            <view class="rating-label">评分：</view>
            <view class="star-rating">
              <text 
                v-for="star in 5" 
                :key="star"
                class="star"
                :class="{ active: star <= (item.rating || 0) }"
                @click="setRating(item, star)"
              >
                ★
              </text>
            </view>
            <view class="rating-text">{{ getRatingText(item.rating || 0) }}</view>
          </view>

          <view class="comment-section">
            <view class="comment-label">评价内容：</view>
            <textarea 
              class="comment-input"
              v-model="item.comment"
              placeholder="请输入您的评价内容..."
              maxlength="500"
              :show-count="true"
            ></textarea>
          </view>

          <button 
            class="submit-btn"
            :disabled="!item.rating"
            @click="submitReview(item)"
          >
            提交评价
          </button>
        </view>

        <!-- 已评价状态 -->
        <view class="reviewed-section" v-else>
          <view class="reviewed-info">
            <view class="reviewed-rating">
              <text class="rating-label">已评价：</text>
              <view class="star-rating">
                <text 
                  v-for="star in 5" 
                  :key="star"
                  class="star"
                  :class="{ active: star <= item.review_rating }"
                >
                  ★
                </text>
              </view>
            </view>
            <view class="reviewed-content" v-if="item.review_content">
              {{ item.review_content }}
            </view>
            <view class="reviewed-time">
              {{ formatDate(item.review_created_at) }}
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-text">暂无商品信息</view>
    </view>
  </view>
</template>

<script>
import { getUserId } from '@/src/utils/auth.js'
import { orderApi, reviewApi } from '@/src/utils/api.js'

export default {
  name: 'Review',
  data() {
    return {
      user_id: getUserId(),
      order_id: null,
      order: null,
      orderItems: [],
      loading: false
    }
  },
  onLoad(options) {
    if (options.order_id) {
      this.order_id = parseInt(options.order_id)
      this.loadOrderDetail()
    }
  },
  methods: {
    // 返回上一页
    goBack() {
      uni.navigateBack({
        delta: 1
      })
    },

    // 加载订单详情
    async loadOrderDetail() {
      if (!this.order_id) return

      this.loading = true
      try {
        const res = await orderApi.getOrderDetail(this.order_id, this.user_id)
        if (res.data && res.data.code === 200) {
          this.order = res.data.data
          await this.loadOrderItemsReviewStatus()
        } else {
          uni.showToast({
            title: res.data?.message || '获取订单信息失败',
            icon: 'error'
          })
        }
      } catch (error) {
        console.error('获取订单详情失败:', error)
        uni.showToast({
          title: '获取订单信息失败',
          icon: 'error'
        })
      } finally {
        this.loading = false
      }
    },

    // 加载订单项的评价状态
    async loadOrderItemsReviewStatus() {
      if (!this.order || !this.order.items) return

      this.orderItems = []
      for (const item of this.order.items) {
        // 直接使用订单项中的is_reviewed字段
        this.orderItems.push({
          ...item,
          rating: 0,
          comment: ''
        })

        // 如果已评价，获取评价详情
        if (item.is_reviewed) {
          try {
            const res = await reviewApi.checkReviewStatus(item.id)
            if (res.data && res.data.code === 200) {
              const reviewData = res.data.data
              const lastItem = this.orderItems[this.orderItems.length - 1]
              lastItem.review_rating = reviewData.review_rating || 0
              lastItem.review_content = reviewData.review_content || ''
              lastItem.review_created_at = reviewData.review_created_at
            }
          } catch (error) {
            console.error('获取评价详情失败:', error)
          }
        }
      }
    },

    // 设置评分
    setRating(item, rating) {
      item.rating = rating
    },

    // 获取评分文本
    getRatingText(rating) {
      const texts = {
        0: '请评分',
        1: '很差',
        2: '一般',
        3: '还行',
        4: '满意',
        5: '非常满意'
      }
      return texts[rating] || '请评分'
    },

    // 获取规格文本
    getSpecText(specCombinationId) {
      // 这里可以根据spec_combination_id获取规格信息
      // 暂时返回默认文本
      return '默认规格'
    },

    // 提交评价
    async submitReview(item) {
      if (!item.rating) {
        uni.showToast({
          title: '请选择评分',
          icon: 'none'
        })
        return
      }

      try {
        uni.showLoading({
          title: '提交中...'
        })

        const reviewData = {
          order_item_id: item.id,
          rating: item.rating,
          content: item.comment || ''
        }

        const res = await reviewApi.addReview(reviewData)
        uni.hideLoading()

        if (res.data && res.data.code === 200) {
          uni.showToast({
            title: '评价成功',
            icon: 'success'
          })
          
          // 更新本地状态
          item.is_reviewed = true
          item.review_rating = item.rating
          item.review_content = item.comment
          item.review_created_at = new Date().toISOString()
          
          // 清空输入
          item.rating = 0
          item.comment = ''
        } else {
          uni.showToast({
            title: res.data?.message || '评价失败',
            icon: 'error'
          })
        }
      } catch (error) {
        uni.hideLoading()
        console.error('提交评价失败:', error)
        uni.showToast({
          title: '评价失败',
          icon: 'error'
        })
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
    }
  }
}
</script>

<style scoped>
.review-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #fff;
  border-bottom: 1rpx solid #eee;
}

.back-btn {
  margin-right: 20rpx;
  font-size: 36rpx;
  color: #333;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.order-info {
  background-color: #fff;
  margin: 20rpx;
  padding: 30rpx;
  border-radius: 10rpx;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-number {
  font-size: 28rpx;
  color: #666;
}

.order-status {
  font-size: 28rpx;
  color: #ff6b35;
}

.product-list {
  margin: 20rpx;
}

.product-item {
  background-color: #fff;
  margin-bottom: 20rpx;
  border-radius: 10rpx;
  overflow: hidden;
}

.product-info {
  display: flex;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.product-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 10rpx;
  margin-right: 20rpx;
}

.product-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 10rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.product-spec {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 10rpx;
}

.product-quantity {
  font-size: 24rpx;
  color: #999;
}

.review-section {
  padding: 30rpx;
}

.rating-section {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.rating-label {
  font-size: 28rpx;
  color: #333;
  margin-right: 20rpx;
}

.star-rating {
  display: flex;
  margin-right: 20rpx;
}

.star {
  font-size: 40rpx;
  color: #ddd;
  margin-right: 10rpx;
  cursor: pointer;
}

.star.active {
  color: #ffd700;
}

.rating-text {
  font-size: 24rpx;
  color: #ff6b35;
}

.comment-section {
  margin-bottom: 30rpx;
}

.comment-label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 20rpx;
}

.comment-input {
  width: 100%;
  min-height: 120rpx;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 10rpx;
  font-size: 28rpx;
  background-color: #fafafa;
}

.submit-btn {
  width: 100%;
  height: 80rpx;
  background-color: #ff6b35;
  color: #fff;
  border: none;
  border-radius: 10rpx;
  font-size: 30rpx;
}

.submit-btn:disabled {
  background-color: #ccc;
}

.reviewed-section {
  padding: 30rpx;
  background-color: #f8f8f8;
}

.reviewed-info {
  display: flex;
  flex-direction: column;
}

.reviewed-rating {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.reviewed-content {
  font-size: 28rpx;
  color: #333;
  line-height: 1.5;
  margin-bottom: 20rpx;
}

.reviewed-time {
  font-size: 24rpx;
  color: #999;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}
</style>
