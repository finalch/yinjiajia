<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-form">
        <div class="form-header">
          <h2>登录银家家</h2>
          <p>欢迎回来，请登录您的账户</p>
        </div>
        
        <el-form
          ref="loginForm"
          :model="loginData"
          :rules="loginRules"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginData.username"
              placeholder="用户名/手机号/邮箱"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginData.password"
              type="password"
              placeholder="密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" @click="forgotPassword">忘记密码？</el-link>
          </div>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="divider">
          <span>或</span>
        </div>
        
        <div class="social-login">
          <el-button
            v-for="social in socialLogins"
            :key="social.name"
            :icon="social.icon"
            @click="socialLogin(social.name)"
            class="social-button"
          >
            {{ social.label }}
          </el-button>
        </div>
        
        <div class="register-link">
          <span>还没有账户？</span>
          <el-link type="primary" @click="$router.push('/register')">
            立即注册
          </el-link>
        </div>
      </div>
      
      <div class="login-banner">
        <div class="banner-content">
          <h3>银家家购物平台</h3>
          <p>享受便捷的购物体验</p>
          <div class="banner-features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>正品保证</span>
            </div>
            <div class="feature-item">
              <el-icon><Truck /></el-icon>
              <span>极速发货</span>
            </div>
            <div class="feature-item">
              <el-icon><Refresh /></el-icon>
              <span>7天无理由退货</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Check, Truck, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'Login',
  components: {
    User,
    Lock,
    Check,
    Truck,
    Refresh
  },
  setup() {
    const router = useRouter()
    const loginForm = ref(null)
    const loading = ref(false)
    const rememberMe = ref(false)

    const loginData = reactive({
      username: '',
      password: ''
    })

    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ]
    }

    const socialLogins = [
      {
        name: 'wechat',
        label: '微信登录',
        icon: 'ChatDotRound'
      },
      {
        name: 'qq',
        label: 'QQ登录',
        icon: 'ChatDotRound'
      },
      {
        name: 'weibo',
        label: '微博登录',
        icon: 'ChatDotRound'
      }
    ]

    const handleLogin = async () => {
      if (!loginForm.value) return
      
      try {
        await loginForm.value.validate()
        loading.value = true
        
        // 模拟登录请求
        setTimeout(() => {
          loading.value = false
          ElMessage.success('登录成功')
          router.push('/')
        }, 1500)
      } catch (error) {
        console.log('表单验证失败:', error)
      }
    }

    const socialLogin = (platform) => {
      ElMessage.info(`${platform} 登录功能开发中...`)
    }

    const forgotPassword = () => {
      ElMessage.info('忘记密码功能开发中...')
    }

    return {
      loginForm,
      loginData,
      loginRules,
      loading,
      rememberMe,
      socialLogins,
      handleLogin,
      socialLogin,
      forgotPassword
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  display: flex;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  overflow: hidden;
  max-width: 900px;
  width: 100%;
}

.login-form {
  flex: 1;
  padding: 40px;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 10px;
}

.form-header p {
  color: #666;
  font-size: 1rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
}

.divider {
  text-align: center;
  margin: 30px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #eee;
}

.divider span {
  background: white;
  padding: 0 20px;
  color: #999;
  font-size: 0.9rem;
}

.social-login {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.social-button {
  flex: 1;
  height: 45px;
}

.register-link {
  text-align: center;
  color: #666;
}

.login-banner {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 60px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.banner-content {
  text-align: center;
}

.banner-content h3 {
  font-size: 2.5rem;
  margin-bottom: 20px;
}

.banner-content p {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.banner-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 1.1rem;
}

.feature-item .el-icon {
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-banner {
    display: none;
  }
  
  .login-form {
    max-width: none;
  }
}
</style> 