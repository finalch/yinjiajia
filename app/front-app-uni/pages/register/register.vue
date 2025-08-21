<template>
  <view class="register-container">
    <view class="header">
      <h1>注册</h1>
      <p>使用手机号与密码创建账户</p>
    </view>

    <form class="form" @submit.prevent="handleSubmit">
      <label class="field">
        <text>手机号</text>
        <input v-model.trim="phone" type="tel" placeholder="请输入手机号" maxlength="20" />
      </label>
      <label class="field">
        <text>密码</text>
        <input v-model="password" type="password" placeholder="请输入密码" maxlength="50" />
      </label>

      <button class="submit" :disabled="submitting" type="submit">{{ submitting ? '提交中...' : '注册' }}</button>
    </form>

    <view class="footer">
      <text>已有账号？</text>
      <a @click.prevent="goLogin" href="#">去登录</a>
    </view>
  </view>
  
</template>

<script>
import { authApi } from '@/src/utils/api.js'

export default {
  name: 'Register',
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
      // 简单校验；后端仍会二次校验
      if (!/^\+?\d[\d\s-]{5,}$/.test(this.phone)) {
        alert('手机号格式不正确')
        return false
      }
      if (this.password.length < 6) {
        alert('密码至少6位')
        return false
      }
      return true
    },
    async handleSubmit() {
      if (!this.validate()) return
      this.submitting = true
      try {
        const res = await authApi.register({ phone: this.phone, password: this.password })
        if (res.data.code === 200) {
          uni.showToast({
            title: '注册成功，请登录',
            icon: 'success'
          })
          // 跳转到登录页
          uni.redirectTo({
            url: '/pages/login/login'
          })
        } else {
          uni.showToast({
            title: res.data.message || '注册失败',
            icon: 'error'
          })
        }
      } catch (e) {
        console.error('注册失败:', e)
        uni.showToast({
          title: '网络错误，注册失败',
          icon: 'error'
        })
      } finally {
        this.submitting = false
      }
    },
    goLogin() {
      // 跳转到登录页
      uni.redirectTo({
        url: '/pages/login/login'
      })
    }
  }
}
</script>

<style scoped>
.register-container {
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


