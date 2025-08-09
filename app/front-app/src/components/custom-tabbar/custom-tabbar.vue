<template>
  <div class="custom-tabbar">
    <div 
      class="tabbar-item" 
      :class="{ active: selected === 0 }"
      @click="navigateTo('/')"
    >
      <div class="icon">🏪</div>
      <div class="label">商城</div>
    </div>
    <div 
      class="tabbar-item" 
      :class="{ active: selected === 1 }"
      @click="navigateTo('/cart')"
    >
      <div class="icon">
        🛒
        <span v-if="cartCount > 0" class="badge">{{ cartCount > 99 ? '99+' : cartCount }}</span>
      </div>
      <div class="label">购物车</div>
    </div>
    <div 
      class="tabbar-item" 
      :class="{ active: selected === 2 }"
      @click="navigateTo('/profile')"
    >
      <div class="icon">👤</div>
      <div class="label">我的</div>
    </div>
    <div 
      class="tabbar-item" 
      :class="{ active: selected === 3 }"
      @click="navigateTo('/customer-service')"
    >
      <div class="icon">💬</div>
      <div class="label">客服</div>
    </div>
  </div>
</template>

<script>
import { cartApi } from '@/utils/api.js'

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
      userId: 1
    }
  },
  methods: {
    navigateTo(path) {
      this.$router.push(path);
    },
    async fetchCartCount() {
      try {
        const response = await cartApi.getCart(this.userId)
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
    window.addEventListener('focus', this.fetchCartCount)
  },
  beforeUnmount() {
    window.removeEventListener('focus', this.fetchCartCount)
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