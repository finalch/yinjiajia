<script setup>
import HelloWorld from './components/HelloWorld.vue'
import CustomTabbar from './components/custom-tabbar/custom-tabbar.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

// 获取当前页面的selected索引
const getSelectedIndex = computed(() => {
  const path = route.path
  if (path === '/') return 0
  if (path === '/cart') return 1
  if (path === '/profile') return 2
  if (path === '/customer-service') return 3
  return 0 // 默认选中商城
})

// 判断是否显示custom-tabbar（商品详情页和支付相关页面不显示）
const showCustomTabbar = computed(() => {
  const path = route.path
  // 商品详情页不显示custom-tabbar
  if (path.startsWith('/product/')) return false
  // 支付相关页面不显示custom-tabbar
  if (path === '/payment-method' || path === '/payment' || path === '/pay-result') return false
  return true
})
</script>

<template>
  <div id="app">
    <main class="main-content" :class="{ 'with-tabbar': showCustomTabbar }">
      <router-view />
    </main>
    <CustomTabbar v-if="showCustomTabbar" :selected="getSelectedIndex" />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 1rem;
}

.main-content.with-tabbar {
  padding-bottom: 80px; /* 为底部tabbar留出空间 */
}
</style>
