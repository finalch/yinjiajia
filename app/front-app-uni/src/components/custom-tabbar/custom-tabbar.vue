<template>
  <view class="custom-tabbar">
    <view 
      class="tabbar-item" 
      :class="{ active: selected === 0 }"
      @click="navigateTo('/')"
    >
      <view class="icon">🏪</view>
      <view class="label">商城</view>
    </view>
    <view 
      class="tabbar-item" 
      :class="{ active: selected === 1 }"
      @click="navigateTo('/cart')"
    >
      <view class="icon">
        🛒
        <text v-if="cartCount > 0" class="badge">{{ cartCount > 99 ? '99+' : cartCount }}</text>
      </view>
      <view class="label">购物车</view>
    </view>
    <view 
      class="tabbar-item" 
      :class="{ active: selected === 2 }"
      @click="navigateTo('/profile')"
    >
      <view class="icon">👤</view>
      <view class="label">我的</view>
    </view>
    <view 
      class="tabbar-item" 
      :class="{ active: selected === 3 }"
      @click="navigateTo('/customer-service')"
    >
      <view class="icon">💬</view>
      <view class="label">客服</view>
    </view>
  </view>
</template>

<script>
import { cartApi } from '@/src/utils/api.js'
import { getUserId } from '@/src/utils/auth.js'

export default {
  name: 'CustomTabbar',
  props: {
    selected: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      cartCount: 0,
      userId: getUserId()
    }
  },
  methods: {
    navigateTo(path) {
      this.$router.push(path);
    },
    async fetchCartCount() {
      // 避免与购物车页重复请求
      if (this.$route.path === '/cart') return
      // 获取最新用户ID；未登录则不请求
      const uid = getUserId()
      if (!uid) {
        this.cartCount = 0
        return
      }
      try {
        const response = await cartApi.getCart(uid)
        if (response.data && response.data.code === 200) {
          const count = response.data.data?.item_count ?? 0
          this.cartCount = Number.isFinite(count) ? count : 0
        }
      } catch (e) {
        // 忽略错误，保持现有数量
      }
    }
  },
  watch: {
    $route() {
      this.fetchCartCount()
    }
  },
  mounted() {
    this.fetchCartCount()
    // 去掉焦点触发，避免切回详情页与详情页自身拉取产生并发
    // window.addEventListener('focus', this.fetchCartCount)
  },
  beforeUnmount() {
    // window.removeEventListener('focus', this.fetchCartCount)
  }
}
</script>

<style scoped>
.custom-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  z-index: 1000;
}

.tabbar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}

.tabbar-item:hover {
  background-color: #f5f5f5;
}

.tabbar-item.active {
  background-color: #fff3f3;
}

.tabbar-item.active .icon {
  color: #e93b3d;
}

.tabbar-item.active .label {
  color: #e93b3d;
  font-weight: bold;
}

.icon {
  font-size: 20px;
  margin-bottom: 2px;
  transition: color 0.2s;
  position: relative;
}

.label {
  font-size: 12px;
  color: #666;
  transition: color 0.2s;
}

.badge {
  position: absolute;
  top: -4px;
  right: -10px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background-color: #e93b3d;
  color: #fff;
  font-size: 10px;
  line-height: 16px;
  text-align: center;
  font-weight: 700;
}
</style> 