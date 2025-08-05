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
      <div class="icon">🛒</div>
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
export default {
  name: 'CustomTabbar',
  props: {
    selected: {
      type: Number,
      default: 0
    }
  },
  methods: {
    navigateTo(path) {
      this.$router.push(path);
    }
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
}

.label {
  font-size: 12px;
  color: #666;
  transition: color 0.2s;
}
</style> 