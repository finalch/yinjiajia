<template>
  <div class="login-container">
    <div class="login-content">
      <!-- 左侧登录表单 -->
      <div class="login-form">
        <div class="login-header">
          <h1>商家登录</h1>
          <p>欢迎使用银家家商家后台管理系统</p>
        </div>

        <el-form
          ref="loginForm"
          :model="loginData"
          :rules="loginRules"
          class="login-form-content"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="phone">
            <el-input
              v-model="loginData.phone"
              placeholder="请输入手机号"
              size="large"
              :prefix-icon="Phone"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginData.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <div class="login-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" @click.prevent="forgotPassword">忘记密码？</a>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              class="login-button"
              :loading="loading"
              @click="handleLogin"
            >
              登录
            </el-button>
          </el-form-item>

          <div class="register-link">
            还没有账号？
            <router-link to="/register">立即注册</router-link>
          </div>
        </el-form>
      </div>

      <!-- 右侧介绍 -->
      <div class="login-intro">
        <div class="intro-content">
          <h2>银家家商家后台</h2>
          <p>专业的电商商家管理系统</p>
          
          <div class="features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>商品管理</span>
            </div>
            <div class="feature-item">
              <el-icon><Van /></el-icon>
              <span>极速发货</span>
            </div>
            <div class="feature-item">
              <el-icon><Refresh /></el-icon>
              <span>实时更新</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Lock, Check, Van, Refresh } from '@element-plus/icons-vue'
import authService from '../services/authService'

export default {
  name: 'Login',
  components: {
    Phone,
    Lock,
    Check,
    Van,
    Refresh
  },
  setup() {
    const router = useRouter()
    const loginForm = ref(null)
    const loading = ref(false)
    const rememberMe = ref(false)

    const loginData = reactive({
      phone: '',
      password: ''
    })

    const loginRules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ]
    }

    const handleLogin = async () => {
      if (!loginForm.value) return
      
      try {
        await loginForm.value.validate()
        loading.value = true
        
        // 使用认证服务登录
        const result = await authService.login(loginData.phone, loginData.password)
        
        if (result.success) {
          // 如果选择记住我，可以设置更长的过期时间
          if (rememberMe.value) {
            // 这里可以设置更长的过期时间或本地存储
            console.log('记住登录状态')
          }

          ElMessage.success('登录成功')
          router.push('/dashboard')
        } else {
          ElMessage.error(result.message || '登录失败')
        }
      } catch (error) {
        console.error('登录失败:', error)
        if (error.name === 'ValidationError') {
          ElMessage.error('请检查输入信息')
        } else {
          ElMessage.error('登录失败，请重试')
        }
      } finally {
        loading.value = false
      }
    }

    const forgotPassword = () => {
      ElMessage.info('忘记密码功能开发中...')
    }

    // 在组件挂载后检查登录状态
    onMounted(() => {
      console.log('🔐 Login组件挂载完成，检查登录状态')
      // 检查是否已登录，如果已登录则跳转到首页
      if (authService.isLoggedIn()) {
        console.log('✅ 检测到已登录状态，跳转到Dashboard')
        router.push('/dashboard')
      } else {
        console.log('❌ 未检测到登录状态，显示登录页面')
      }
    })

    return {
      loginForm,
      loginData,
      loginRules,
      loading,
      rememberMe,
      handleLogin,
      forgotPassword
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-content {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  max-width: 1000px;
  width: 100%;
  min-height: 600px;
}

.login-form {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  font-size: 16px;
}

.login-form-content {
  width: 100%;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-options a {
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
}

.login-options a:hover {
  text-decoration: underline;
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 500;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  text-decoration: underline;
}

.login-intro {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.intro-content h2 {
  font-size: 36px;
  margin-bottom: 20px;
  font-weight: 600;
}

.intro-content p {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 16px;
}

.feature-item .el-icon {
  font-size: 20px;
  color: #ffd700;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    max-width: 100%;
    border-radius: 0;
  }
  
  .login-form {
    padding: 40px 30px;
  }
  
  .login-intro {
    padding: 40px 30px;
  }
  
  .login-header h1 {
    font-size: 28px;
  }
  
  .intro-content h2 {
    font-size: 30px;
  }
}
</style> 