<script setup>
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边栏导航 -->
      <el-aside width="250px" class="sidebar">
        <div class="logo">
          <h2>银家家商家后台</h2>
        </div>
        
        <el-menu
          :default-active="$route.path"
          :router="true"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/">
            <el-icon><DataBoard /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          
          <el-sub-menu index="products">
            <template #title>
              <el-icon><Goods /></el-icon>
              <span>商品管理</span>
            </template>
            <el-menu-item index="/products">商品列表</el-menu-item>
            <el-menu-item index="/products/add">发布商品</el-menu-item>
            <el-menu-item index="/categories">商品分类</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="orders">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>订单管理</span>
            </template>
            <el-menu-item index="/orders">订单列表</el-menu-item>
            <el-menu-item index="/logistics">物流管理</el-menu-item>
            <el-menu-item index="/after-sales">售后处理</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/analytics">
            <el-icon><TrendCharts /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          
          <el-menu-item index="/finance">
            <el-icon><Money /></el-icon>
            <span>资金结算</span>
          </el-menu-item>
          
          <el-sub-menu index="service">
            <template #title>
              <el-icon><Service /></el-icon>
              <span>客户服务</span>
            </template>
            <el-menu-item index="/customer-service">客服咨询</el-menu-item>
            <el-menu-item index="/reviews">评价管理</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区域 -->
      <el-container>
        <!-- 顶部导航栏 -->
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path" :to="item.path">
                {{ item.name }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleUserCommand">
              <div class="user-info">
                <el-avatar :src="userAvatar" />
                <span class="username">{{ userName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主要内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  DataBoard, 
  Goods, 
  Document, 
  TrendCharts, 
  Money, 
  Service, 
  Setting,
  ArrowDown
} from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    DataBoard,
    Goods,
    Document,
    TrendCharts,
    Money,
    Service,
    Setting,
    ArrowDown
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // 用户信息
    const userName = ref('商家管理员')
    const userAvatar = ref('https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png')
    
    // 面包屑导航
    const breadcrumbs = computed(() => {
      const paths = route.path.split('/').filter(Boolean)
      const result = [{ path: '/', name: '首页' }]
      
      paths.forEach((path, index) => {
        const fullPath = '/' + paths.slice(0, index + 1).join('/')
        const name = getBreadcrumbName(path)
        result.push({ path: fullPath, name })
      })
      
      return result
    })
    
    const getBreadcrumbName = (path) => {
      const nameMap = {
        'products': '商品管理',
        'orders': '订单管理',
        'analytics': '数据分析',
        'finance': '资金结算',
        'customer-service': '客户服务',
        'settings': '系统设置',
        'add': '发布商品',
        'edit': '编辑商品',
        'categories': '商品分类',
        'logistics': '物流管理',
        'after-sales': '售后处理',
        'reviews': '评价管理'
      }
      return nameMap[path] || path
    }
    
    const handleUserCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/settings')
          break
        case 'settings':
          router.push('/settings')
          break
        case 'logout':
          router.push('/login')
          break
      }
    }
    
    return {
      userName,
      userAvatar,
      breadcrumbs,
      handleUserCommand
    }
  }
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
  background-color: #f0f2f5;
}

#app {
  height: 100vh;
}

.app-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #bfcbd9;
  overflow-y: auto;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #435266;
}

.logo h2 {
  color: #fff;
  font-size: 1.2rem;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.username {
  color: #333;
  font-weight: 500;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
