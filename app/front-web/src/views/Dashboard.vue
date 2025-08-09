<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>数据概览</h1>
      <p>实时监控店铺经营数据</p>
    </div>

    <!-- 数据卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sales">
              <el-icon size="24"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ formatNumber(todaySales) }}</div>
              <div class="stat-label">今日销售额</div>
              <div class="stat-change" :class="{ positive: salesChange > 0, negative: salesChange < 0 }">
                {{ salesChange > 0 ? '+' : '' }}{{ salesChange }}% 较昨日
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orders">
              <el-icon size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayOrders }}</div>
              <div class="stat-label">今日订单数</div>
              <div class="stat-change" :class="{ positive: ordersChange > 0, negative: ordersChange < 0 }">
                {{ ordersChange > 0 ? '+' : '' }}{{ ordersChange }}% 较昨日
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon customers">
              <el-icon size="24"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ todayCustomers }}</div>
              <div class="stat-label">今日访客数</div>
              <div class="stat-change" :class="{ positive: customersChange > 0, negative: customersChange < 0 }">
                {{ customersChange > 0 ? '+' : '' }}{{ customersChange }}% 较昨日
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon products">
              <el-icon size="24"><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalProducts }}</div>
              <div class="stat-label">在售商品</div>
              <div class="stat-change">
                {{ pendingReview }} 待审核
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <span>销售趋势</span>
            <el-radio-group v-model="salesPeriod" size="small" style="float: right;">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
              <el-radio-button label="90">近90天</el-radio-button>
            </el-radio-group>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              <el-icon size="48" color="#ddd"><TrendCharts /></el-icon>
              <p>销售趋势图表</p>
              <p class="chart-desc">展示销售额、订单量等关键指标的变化趋势</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>商品分类销售占比</span>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              <el-icon size="48" color="#ddd"><PieChart /></el-icon>
              <p>饼图</p>
              <p class="chart-desc">展示各商品分类的销售占比</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" class="quick-actions">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="action-grid">
            <div class="action-item" @click="$router.push('/products/add')">
              <el-icon size="24"><Plus /></el-icon>
              <span>发布商品</span>
            </div>
            <div class="action-item" @click="$router.push('/orders')">
              <el-icon size="24"><Document /></el-icon>
              <span>处理订单</span>
            </div>
            <div class="action-item" @click="$router.push('/customer-service')">
              <el-icon size="24"><ChatDotRound /></el-icon>
              <span>客服咨询</span>
            </div>
            <div class="action-item" @click="$router.push('/finance')">
              <el-icon size="24"><Wallet /></el-icon>
              <span>资金提现</span>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待处理事项</span>
          </template>
          <div class="todo-list">
            <div class="todo-item" v-for="todo in todoList" :key="todo.id">
              <div class="todo-content">
                <span class="todo-text">{{ todo.text }}</span>
                <el-tag :type="todo.type" size="small">{{ todo.count }}</el-tag>
              </div>
              <el-button type="text" size="small" @click="handleTodo(todo)">
                处理
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'
import {
  Money,
  Document,
  User,
  Goods,
  TrendCharts,
  PieChart,
  Plus,
  ChatDotRound,
  Wallet
} from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    Money,
    Document,
    User,
    Goods,
    TrendCharts,
    PieChart,
    Plus,
    ChatDotRound,
    Wallet
  },
  setup() {
    const router = useRouter()

    // 统计数据
    const todaySales = ref(0)
    const salesChange = ref(0)
    const todayOrders = ref(0)
    const ordersChange = ref(0)
    const todayCustomers = ref(0)      // 访客暂用0，后续对接埋点或UV接口
    const customersChange = ref(0)
    const totalProducts = ref(0)
    const pendingReview = ref(0)       // 待审核暂用0，后续对接分类/商品审核统计

    // 图表周期
    const salesPeriod = ref('7')

    // 待处理事项
    const todoList = ref([
      { id: 1, text: '待发货订单', count: 12, type: 'warning', path: '/orders' },
      { id: 2, text: '待审核商品', count: 3, type: 'info', path: '/products' },
      { id: 3, text: '待回复咨询', count: 8, type: 'primary', path: '/customer-service' },
      { id: 4, text: '待处理退款', count: 2, type: 'danger', path: '/after-sales' }
    ])

    const currentMerchantId = 1
    const toPercent = (t, y) => {
      if (!y) return t > 0 ? 100 : 0
      return Math.round(((t - y) / y) * 1000) / 10
    }

    const fetchDashboard = async () => {
      try {
        const res = await request.get('/api/web/analytics/dashboard', {
          params: { merchant_id: currentMerchantId }
        })
        if (res.data?.code === 200) {
          const d = res.data.data || {}
          const today = d.today || {}
          const yesterday = d.yesterday || {}
          const total = d.total || {}

          todaySales.value = Number(today.sales || 0)
          todayOrders.value = Number(today.orders || 0)
          totalProducts.value = Number(total.products || 0)

          salesChange.value = toPercent(today.sales || 0, yesterday.sales || 0)
          ordersChange.value = toPercent(today.orders || 0, yesterday.orders || 0)
        }
      } catch (e) {
        console.error('加载仪表板数据失败', e)
      }
    }

    onMounted(() => {
      fetchDashboard()
    })

    // 格式化数字/处理待办保持不变
    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    const handleTodo = (todo) => { router.push(todo.path) }

    return {
      todaySales, salesChange, todayOrders, ordersChange,
      todayCustomers, customersChange, totalProducts, pendingReview,
      salesPeriod, todoList, formatNumber, handleTodo
    }
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  font-size: 1rem;
}

.stats-cards {
  margin-bottom: 30px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon.sales {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-icon.orders {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.customers {
  background-color: #fff7e6;
  color: #fa8c16;
}

.stat-icon.products {
  background-color: #f9f0ff;
  color: #722ed1;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.stat-change {
  font-size: 0.8rem;
}

.stat-change.positive {
  color: #52c41a;
}

.stat-change.negative {
  color: #ff4d4f;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 400px;
}

.chart-container {
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  text-align: center;
  color: #999;
}

.chart-placeholder p {
  margin: 10px 0 0 0;
}

.chart-desc {
  font-size: 0.9rem;
  color: #ccc;
}

.quick-actions {
  margin-bottom: 30px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.action-item .el-icon {
  color: #409eff;
  margin-bottom: 10px;
}

.action-item span {
  color: #333;
  font-weight: 500;
}

.todo-list {
  max-height: 300px;
  overflow-y: auto;
}

.todo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.todo-item:last-child {
  border-bottom: none;
}

.todo-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.todo-text {
  color: #333;
  font-weight: 500;
}
</style> 