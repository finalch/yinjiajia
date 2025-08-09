<template>
  <div class="login-container">
    <div class="header">
      <h1>登录</h1>
      <p>使用手机号与密码登录</p>
    </div>

    <form class="form" @submit.prevent="handleSubmit">
      <label class="field">
        <span>手机号</span>
        <input v-model.trim="phone" type="tel" placeholder="请输入手机号" maxlength="20" />
      </label>
      <label class="field">
        <span>密码</span>
        <input v-model="password" type="password" placeholder="请输入密码" maxlength="50" />
      </label>

      <button class="submit" :disabled="submitting" type="submit">{{ submitting ? '登录中...' : '登录' }}</button>
    </form>

    <div class="footer">
      <span>没有账号？</span>
      <a @click.prevent="goRegister" href="#">去注册</a>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/utils/api.js'
import { setToken, setUser } from '@/utils/auth.js'

export default {
  name: 'Login',
  data() {
    return {
      phone: '',
      password: '',
      submitting: false
    }
  },
  methods: {
    validate() {
      if (!this.phone || !this.password) {
        alert('请输入手机号和密码')
        return false
      }
      return true
    },
    async handleSubmit() {
      if (!this.validate()) return
      this.submitting = true
      try {
        const res = await authApi.login({ phone: this.phone, password: this.password })
        if (res.data.code === 200) {
          const { token, expires_at, user_id, user_number, phone } = res.data.data
          setToken(token, expires_at)
          setUser({ user_id, user_number, phone })
          this.$router.replace('/')
        } else {
          alert(res.data.message || '登录失败')
        }
      } catch (e) {
        console.error('登录失败:', e)
        alert('网络错误，登录失败')
      } finally {
        this.submitting = false
      }
    },
    goRegister() {
      this.$router.replace('/register')
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 24px 16px 60px;
}
.header h1 {
  font-size: 24px;
  margin: 8px 0 4px;
}
.header p {
  color: #666;
  font-size: 14px;
}
.form {
  margin-top: 24px;
  display: grid;
  gap: 16px;
}
.field {
  display: grid;
  gap: 8px;
}
.field span {
  font-size: 14px;
  color: #333;
}
.field input {
  padding: 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
}
.submit {
  margin-top: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  background: #e93b3d;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}
.submit:disabled {
  opacity: .6;
  cursor: not-allowed;
}
.footer {
  margin-top: 16px;
  font-size: 14px;
  color: #666;
}
.footer a {
  color: #e93b3d;
  cursor: pointer;
}
</style>


