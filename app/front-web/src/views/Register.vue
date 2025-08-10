<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-form">
        <div class="form-header">
          <h2>商家注册</h2>
          <p>创建您的商家账户，开始经营之旅</p>
        </div>
        
        <el-form
          ref="registerForm"
          :model="registerData"
          :rules="registerRules"
        >
          <el-form-item prop="phone">
            <el-input
              v-model="registerData.phone"
              placeholder="手机号"
              size="large"
              :prefix-icon="Phone"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="registerData.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="registerData.confirmPassword"
              type="password"
              placeholder="确认密码"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-checkbox v-model="agreeTerms">
              我已阅读并同意
              <el-link type="primary">用户协议</el-link>
              和
              <el-link type="primary">隐私政策</el-link>
            </el-checkbox>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              @click="handleRegister"
              class="register-button"
              :disabled="!agreeTerms"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-link">
          <span>已有账户？</span>
          <el-link type="primary" @click="$router.push('/login')">
            立即登录
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Phone, Lock } from '@element-plus/icons-vue'
import authService from '../services/authService'

export default {
  name: 'Register',
  components: {
    Phone,
    Lock
  },
  setup() {
    const router = useRouter()
    const registerForm = ref(null)
    const loading = ref(false)
    const agreeTerms = ref(false)

    // 在组件挂载后检查登录状态
    onMounted(() => {
      console.log('🔐 Register组件挂载完成，检查登录状态')
      // 检查是否已登录，如果已登录则跳转到首页
      if (authService.isLoggedIn()) {
        console.log('✅ 检测到已登录状态，跳转到Dashboard')
        router.push('/dashboard')
      } else {
        console.log('❌ 未检测到登录状态，显示注册页面')
      }
    })

    const registerData = reactive({
      phone: '',
      password: '',
      confirmPassword: ''
    })

    const registerRules = {
      phone: [
        { required: true, message: '请输入手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== registerData.password) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    const handleRegister = async () => {
      if (!registerForm.value) return
      
      try {
        await registerForm.value.validate()
        loading.value = true
        
        // 调用商家注册API
        const response = await fetch('/api/web/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            phone: registerData.phone,
            password: registerData.password
          })
        })
        
        const result = await response.json()
        
        if (result.code === 200) {
          ElMessage.success('注册成功，请登录')
          router.push('/login')
        } else {
          ElMessage.error(result.message || '注册失败')
        }
      } catch (error) {
        console.error('注册失败:', error)
        ElMessage.error('注册失败，请重试')
      } finally {
        loading.value = false
      }
    }

    return {
      registerForm,
      registerData,
      registerRules,
      loading,
      agreeTerms,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  padding: 40px;
  max-width: 500px;
  width: 100%;
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

.register-button {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #666;
}
</style> 