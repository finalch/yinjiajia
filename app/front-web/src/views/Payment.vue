<template>
  <div class="payment">
    <h1 class="page-title">订单支付</h1>
    
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>选择支付方式</span>
          </template>
          
          <el-radio-group v-model="paymentMethod">
            <div class="payment-method" v-for="method in paymentMethods" :key="method.id">
              <el-radio :label="method.id">
                <div class="method-info">
                  <img :src="method.icon" :alt="method.name" class="method-icon">
                  <span class="method-name">{{ method.name }}</span>
                  <span class="method-desc">{{ method.description }}</span>
                </div>
              </el-radio>
            </div>
          </el-radio-group>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="order-info">
          <template #header>
            <span>订单信息</span>
          </template>
          
          <div class="info-item">
            <span>订单号：</span>
            <span>{{ orderInfo.orderNo }}</span>
          </div>
          <div class="info-item">
            <span>支付金额：</span>
            <span class="amount">¥{{ orderInfo.amount }}</span>
          </div>
          
          <el-button type="primary" size="large" @click="handlePayment" class="pay-btn">
            立即支付
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Payment',
  setup() {
    const router = useRouter()
    const paymentMethod = ref('alipay')
    
    const paymentMethods = ref([
      {
        id: 'alipay',
        name: '支付宝',
        description: '推荐有支付宝账户的用户使用',
        icon: 'https://img.alicdn.com/tfs/TB1Ly5oS3HqK1RjSZFPXXcwapXa-238-54.png'
      },
      {
        id: 'wechat',
        name: '微信支付',
        description: '推荐有微信账户的用户使用',
        icon: 'https://res.wx.qq.com/a/wx_fed/assets/res/OTE0YTAw.png'
      },
      {
        id: 'unionpay',
        name: '银联支付',
        description: '支持各大银行储蓄卡和信用卡',
        icon: 'https://www.unionpay.com/images/logo.png'
      }
    ])
    
    const orderInfo = ref({
      orderNo: 'YJJ202401150001',
      amount: 11797.00
    })
    
    const handlePayment = () => {
      ElMessage.success('支付成功')
      router.push('/order-success')
    }
    
    return {
      paymentMethod,
      paymentMethods,
      orderInfo,
      handlePayment
    }
  }
}
</script>

<style scoped>
.payment {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 30px;
  color: #333;
}

.payment-method {
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.method-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.method-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.method-name {
  font-weight: bold;
  color: #333;
}

.method-desc {
  color: #666;
  font-size: 0.9rem;
}

.order-info {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  padding: 10px 0;
}

.amount {
  font-weight: bold;
  color: #e74c3c;
  font-size: 1.2rem;
}

.pay-btn {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
  margin-top: 20px;
}
</style> 