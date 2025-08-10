<template>
  <div class="test-auth">
    <div class="container">
      <h1>认证功能测试</h1>
      
      <div class="auth-status">
        <h3>当前认证状态</h3>
        <p><strong>已登录:</strong> {{ isLoggedIn ? '是' : '否' }}</p>
        <p><strong>Token:</strong> {{ token ? '已设置' : '未设置' }}</p>
        <p><strong>用户信息:</strong> {{ userInfo ? JSON.stringify(userInfo, null, 2) : '无' }}</p>
      </div>

      <div class="actions">
        <el-button @click="checkAuthStatus">检查认证状态</el-button>
        <el-button @click="validateToken">验证Token</el-button>
        <el-button @click="getProfile">获取用户资料</el-button>
        <el-button @click="clearAuth">清除认证</el-button>
        <el-button @click="goToDashboard">跳转Dashboard</el-button>
        <el-button @click="goToLogin">跳转登录页</el-button>
        <el-button @click="testRouteGuard">测试路由守卫</el-button>
        <el-button @click="goToRoot">访问根路径</el-button>
        <el-button @click="clearLocalStorage" type="danger">清除localStorage</el-button>
      </div>

      <div class="logs">
        <h3>操作日志</h3>
        <div v-for="(log, index) in logs" :key="index" class="log-item">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from '../services/authService'
import { isAuthenticated, getMerchantInfo, clearAuth } from '../router/auth'

export default {
  name: 'TestAuth',
  setup() {
    const router = useRouter()
    const isLoggedIn = ref(false)
    const token = ref('')
    const userInfo = ref(null)
    const logs = ref([])

    const addLog = (message) => {
      const time = new Date().toLocaleTimeString()
      logs.value.unshift({ time, message })
      if (logs.value.length > 20) {
        logs.value = logs.value.slice(0, 20)
      }
    }

    const checkAuthStatus = () => {
      const status = authService.isLoggedIn()
      isLoggedIn.value = status
      token.value = authService.getToken()
      userInfo.value = authService.getUserInfo()
      addLog(`检查认证状态: ${status ? '已登录' : '未登录'}`)
    }

    const validateToken = async () => {
      try {
        addLog('开始验证Token...')
        const isValid = await authService.validateToken()
        addLog(`Token验证结果: ${isValid ? '有效' : '无效'}`)
        checkAuthStatus()
      } catch (error) {
        addLog(`Token验证失败: ${error.message}`)
      }
    }

    const getProfile = async () => {
      try {
        addLog('开始获取用户资料...')
        const result = await authService.getProfile()
        if (result.success) {
          addLog('获取用户资料成功')
          userInfo.value = result.data
        } else {
          addLog(`获取用户资料失败: ${result.message}`)
        }
      } catch (error) {
        addLog(`获取用户资料异常: ${error.message}`)
      }
    }

    const clearAuthData = () => {
      clearAuth()
      addLog('已清除认证信息')
      checkAuthStatus()
    }

    const goToDashboard = () => {
      addLog('尝试跳转到Dashboard...')
      router.push('/dashboard')
    }

    const goToLogin = () => {
      addLog('跳转到登录页...')
      router.push('/login')
    }

    const testRouteGuard = () => {
      addLog('测试路由守卫...')
      addLog('当前路径: ' + router.currentRoute.value.path)
      addLog('尝试访问受保护路由...')
      router.push('/dashboard')
    }

    const goToRoot = () => {
      addLog('访问根路径...')
      router.push('/')
    }

    const clearLocalStorage = () => {
      addLog('开始清除localStorage...')
      localStorage.clear()
      addLog('localStorage已清除')
      checkAuthStatus() // Re-check status after clearing
    }

    onMounted(() => {
      addLog('页面加载完成')
      checkAuthStatus()
    })

    return {
      isLoggedIn,
      token,
      userInfo,
      logs,
      checkAuthStatus,
      validateToken,
      getProfile,
      clearAuth: clearAuthData,
      goToDashboard,
      goToLogin,
      testRouteGuard,
      goToRoot,
      clearLocalStorage
    }
  }
}
</script>

<style scoped>
.test-auth {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.auth-status {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.auth-status h3 {
  margin-top: 0;
  color: #666;
}

.actions {
  margin-bottom: 20px;
}

.actions .el-button {
  margin-right: 10px;
  margin-bottom: 10px;
}

.logs {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
}

.logs h3 {
  margin-top: 0;
  color: #666;
}

.log-item {
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}

.log-time {
  color: #999;
  font-size: 0.9em;
  margin-right: 10px;
}

.log-message {
  color: #333;
}
</style>
