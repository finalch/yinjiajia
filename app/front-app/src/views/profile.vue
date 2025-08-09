<template>
    <div class="profile-container">
      <!-- 用户信息区域 -->
      <div class="user-info-section">
        <div class="user-avatar">
          <div class="avatar-placeholder">👤</div>
        </div>
        <div class="user-details">
          <div class="username">{{ displayName }}</div>
          <div class="user-id">ID: {{ userIdDisplay }}</div>
        </div>
        <div class="settings-btn" @click="goToSettings">
          <span>⚙️</span>
        </div>
      </div>
  
      <!-- 功能菜单 -->
      <div class="menu-section">
        <!-- 订单相关 -->
        <div class="menu-group">
          <div class="menu-item" @click="goToOrders">
            <div class="menu-icon">📋</div>
            <div class="menu-content">
              <div class="menu-title">我的订单</div>
              <div class="menu-desc">查看所有订单状态</div>
            </div>
            <div class="menu-arrow">></div>
          </div>
          
          <div class="menu-item" @click="goToAddress">
            <div class="menu-icon">📍</div>
            <div class="menu-content">
              <div class="menu-title">收货地址</div>
              <div class="menu-desc">管理收货地址</div>
            </div>
            <div class="menu-arrow">></div>
          </div>
        </div>
  
        <!-- 其他功能 -->
        <div class="menu-group">
          <div class="menu-item" @click="goToCustomerService">
            <div class="menu-icon">💬</div>
            <div class="menu-content">
              <div class="menu-title">客服中心</div>
              <div class="menu-desc">联系客服解决问题</div>
            </div>
            <div class="menu-arrow">></div>
          </div>
          
          <div class="menu-item" @click="goToAbout">
            <div class="menu-icon">ℹ️</div>
            <div class="menu-content">
              <div class="menu-title">关于我们</div>
              <div class="menu-desc">了解更多信息</div>
            </div>
            <div class="menu-arrow">></div>
          </div>
        </div>
  
        <!-- 退出登录 -->
        <div class="menu-group">
          <div class="menu-item logout-item" @click="logout">
            <div class="menu-icon">🚪</div>
            <div class="menu-content">
              <div class="menu-title">退出登录</div>
              <div class="menu-desc">安全退出当前账号</div>
            </div>
            <div class="menu-arrow">></div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { getUser, clearToken, clearUser } from '@/utils/auth.js'
  export default {
    name: 'Profile',
    data() {
      return {
        userInfo: getUser()
      }
    },
    computed: {
      displayName() {
        if (this.userInfo && (this.userInfo.phone || this.userInfo.user_number)) {
          return this.userInfo.phone || `用户${this.userInfo.user_number}`
        }
        return '未登录'
      },
      userIdDisplay() {
        if (this.userInfo && (this.userInfo.user_number || this.userInfo.user_id)) {
          return this.userInfo.user_number || this.userInfo.user_id
        }
        return '--'
      }
    },
    methods: {
      goToOrders() {
        this.$router.push('/my-order');
      },
      goToAddress() {
        this.$router.push('/address');
      },
      goToCustomerService() {
        this.$router.push('/customer-service');
      },
      goToSettings() {
        // TODO: 实现设置页面
        alert('设置功能开发中...');
      },
      goToAbout() {
        // TODO: 实现关于页面
        alert('关于我们功能开发中...');
      },
      logout() {
        if (confirm('确定要退出登录吗？')) {
          clearToken()
          clearUser()
          this.userInfo = {}
          this.$router.replace('/login')
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .profile-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 80px; /* 为底部tabbar留出空间 */
  }
  
  .user-info-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px 30px;
    display: flex;
    align-items: center;
    color: white;
  }
  
  .user-avatar {
    margin-right: 15px;
  }
  
  .avatar-placeholder {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }
  
  .user-details {
    flex: 1;
  }
  
  .username {
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 5px;
  }
  
  .user-id {
    font-size: 14px;
    opacity: 0.8;
  }
  
  .settings-btn {
    padding: 8px;
    cursor: pointer;
  }
  
  .menu-section {
    padding: 20px;
  }
  
  .menu-group {
    background: white;
    border-radius: 12px;
    margin-bottom: 15px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .menu-item {
    display: flex;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .menu-item:last-child {
    border-bottom: none;
  }
  
  .menu-item:hover {
    background-color: #f8f9fa;
  }
  
  .menu-icon {
    font-size: 20px;
    margin-right: 15px;
    width: 24px;
    text-align: center;
  }
  
  .menu-content {
    flex: 1;
  }
  
  .menu-title {
    font-size: 16px;
    font-weight: 500;
    color: #333;
    margin-bottom: 2px;
  }
  
  .menu-desc {
    font-size: 12px;
    color: #999;
  }
  
  .menu-arrow {
    color: #ccc;
    font-size: 16px;
  }
  
  .logout-item {
    color: #ff4757;
  }
  
  .logout-item .menu-title {
    color: #ff4757;
  }
  
  .logout-item .menu-desc {
    color: #ff6b7a;
  }
</style>