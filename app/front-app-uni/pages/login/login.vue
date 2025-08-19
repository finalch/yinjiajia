<template>
  <view class="login-container">
    <view class="header">
      <text class="title">登录</text>
    </view>

    <view class="form">
      <view class="field">
        <text class="label">手机号</text>
        <input 
          v-model="phone" 
          type="text" 
          placeholder="请输入手机号" 
          class="input"
        />
      </view>
      
      <view class="field">
        <text class="label">密码</text>
        <input 
          v-model="password" 
          type="text" 
          placeholder="请输入密码" 
          class="input"
        />
      </view>

      <button class="submit" @click="handleSubmit">
        登录
      </button>
    </view>
  </view>
</template>

<script>
import { authApi } from '@/src/utils/api.js'
import { setToken, setUser } from '@/src/utils/auth.js'

export default {
  name: 'Login',
  data() {
    return {
      phone: '',
      password: ''
    }
  },
  methods: {
    handleSubmit() {
      authApi.login({
    phone: this.phone,
    password: this.password
  }).then(res => {
    console.log('登录响应:', res) // 添加调试日志
    if (res.data.code === 200) {
	  const { token, expires_at, user_id, user_number, phone } = res.data.data
	  setUser({ user_id, user_number, phone })
      setToken(token, expires_at)
      // 尝试跳转
      uni.switchTab({
        url: '/pages/shop/shop',
        fail: (err) => {
          uni.showToast({
            title: '跳转失败',
            icon: 'none'
          })
		}
      })
    } else {
      uni.showToast({
        title: res.data.message || '登录失败',
        icon: 'none'
      })
    }
  }).catch(err => {
    console.error('登录请求失败:', err)
    uni.showToast({
      title: '网络错误',
      icon: 'none'
    })
  })
    }
  }
}
</script>

<style scoped>
.login-container {
  padding: 100rpx 50rpx;
}

.header {
  text-align: center;
  margin-bottom: 100rpx;
}

.title {
  font-size: 60rpx;
  font-weight: bold;
}

.form {
  margin-bottom: 100rpx;
}

.field {
  margin-bottom: 50rpx;
}

.label {
  display: block;
  font-size: 32rpx;
  margin-bottom: 20rpx;
}

.input {
  width: 100%;
  height: 80rpx;
  border: 2rpx solid #ccc;
  border-radius: 10rpx;
  padding: 0 20rpx;
  font-size: 32rpx;
  background-color: #fff;
}

.submit {
  width: 100%;
  height: 80rpx;
  background-color: #007aff;
  color: #fff;
  border: none;
  border-radius: 10rpx;
  font-size: 32rpx;
}

.debug {
  background-color: #f0f0f0;
  padding: 30rpx;
  border-radius: 10rpx;
}

.debug text {
  display: block;
  font-size: 28rpx;
  margin-bottom: 10rpx;
}
</style>


