<template>
  <div class="order-success">
    <div class="success-container">
      <div class="success-icon">
        <el-icon size="80" color="#67c23a"><CircleCheckFilled /></el-icon>
      </div>
      <h1>订单提交成功！</h1>
      <p class="order-no">订单号：{{ orderNo }}</p>
      <p class="amount">支付金额：¥{{ amount }}</p>
      
      <div class="actions">
        <el-button type="primary" @click="$router.push('/orders')">查看订单</el-button>
        <el-button @click="$router.push('/')">继续购物</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { CircleCheckFilled } from '@element-plus/icons-vue'

export default {
  name: 'OrderSuccess',
  components: {
    CircleCheckFilled
  },
  setup() {
    const orderNo = ref('YJJ202401150001')
    const amount = ref('11797.00')
    
    return {
      orderNo,
      amount
    }
  }
}
</script>

<style scoped>
.order-success {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.success-container {
  text-align: center;
  padding: 40px;
}

.success-icon {
  margin-bottom: 20px;
}

.success-container h1 {
  color: #67c23a;
  margin-bottom: 20px;
}

.order-no,
.amount {
  font-size: 1.1rem;
  color: #666;
  margin-bottom: 10px;
}

.actions {
  margin-top: 30px;
}

.actions .el-button {
  margin: 0 10px;
}
</style> 