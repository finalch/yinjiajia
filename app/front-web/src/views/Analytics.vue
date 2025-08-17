<template>
  <div class="analytics">
    <div class="page-header">
      <h1>数据分析</h1>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          @change="handleDateChange"
        />
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
      </div>
    </div>

    <!-- 核心指标 -->
    <el-row :gutter="20" class="metrics-cards">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-content">
            <div class="metric-icon revenue">
              <el-icon size="24"><Money /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">¥{{ formatNumber(totalRevenue) }}</div>
              <div class="metric-label">总销售额</div>
              <div class="metric-change" :class="{ positive: revenueChange > 0, negative: revenueChange < 0 }">
                {{ revenueChange > 0 ? '+' : '' }}{{ revenueChange }}% 较上期
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-content">
            <div class="metric-icon orders">
              <el-icon size="24"><Document /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ totalOrders }}</div>
              <div class="metric-label">订单总数</div>
              <div class="metric-change" :class="{ positive: ordersChange > 0, negative: ordersChange < 0 }">
                {{ ordersChange > 0 ? '+' : '' }}{{ ordersChange }}% 较上期
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-content">
            <div class="metric-icon customers">
              <el-icon size="24"><User /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ totalCustomers }}</div>
              <div class="metric-label">新增客户</div>
              <div class="metric-change" :class="{ positive: customersChange > 0, negative: customersChange < 0 }">
                {{ customersChange > 0 ? '+' : '' }}{{ customersChange }}% 较上期
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-content">
            <div class="metric-icon conversion">
              <el-icon size="24"><TrendCharts /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ conversionRate }}%</div>
              <div class="metric-label">转化率</div>
              <div class="metric-change" :class="{ positive: conversionChange > 0, negative: conversionChange < 0 }">
                {{ conversionChange > 0 ? '+' : '' }}{{ conversionChange }}% 较上期
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
            <el-radio-group v-model="salesChartType" size="small" style="float: right;">
              <el-radio-button label="revenue">销售额</el-radio-button>
              <el-radio-button label="orders">订单量</el-radio-button>
            </el-radio-group>
          </template>
          <div class="chart-container">
            <div class="chart-placeholder">
              <el-icon size="48" color="#ddd"><TrendCharts /></el-icon>
              <p>销售趋势图表</p>
              <p class="chart-desc">展示{{ salesChartType === 'revenue' ? '销售额' : '订单量' }}的变化趋势</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="analysis-card">
          <template #header>
            <span>热销商品 TOP 10</span>
          </template>
          <div class="product-list">
            <div
              v-for="(product, index) in hotProducts"
              :key="product.id"
              class="product-item"
            >
              <div class="product-rank">{{ index + 1 }}</div>
              <el-image
                :src="product.image"
                class="product-image"
                fit="cover"
              />
              <div class="product-info">
                <h4 class="product-name">{{ product.name }}</h4>
                <p class="product-sales">销量：{{ product.sales }}件</p>
                <p class="product-revenue">销售额：¥{{ formatNumber(product.revenue) }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Download, 
  Money, 
  Document, 
  User, 
  TrendCharts, 
  PieChart 
} from '@element-plus/icons-vue'

export default {
  name: 'Analytics',
  components: {
    Download,
    Money,
    Document,
    User,
    TrendCharts,
    PieChart
  },
  setup() {
    // 日期范围
    const dateRange = ref([])
    
    // 销售图表类型
    const salesChartType = ref('revenue')
    
    // 核心指标
    const totalRevenue = ref(0)
    const revenueChange = ref(0)
    const totalOrders = ref(0)
    const ordersChange = ref(0)
    const totalCustomers = ref(0)
    const customersChange = ref(0)
    const conversionRate = ref(0)
    const conversionChange = ref(0)
    
    // 客户分析
    const newCustomers = ref(0)
    const activeCustomers = ref(0)
    const repeatCustomers = ref(0)
    const avgOrderValue = ref(0)
    
    // 热销商品
    const hotProducts = ref([
      {
        id: 1,
        name: 'Apple iPhone 15 Pro',
        sales: 25,
        revenue: 199975,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2,
        name: 'MacBook Pro 14英寸',
        sales: 8,
        revenue: 119992,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 3,
        name: 'AirPods Pro',
        sales: 45,
        revenue: 85455,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 4,
        name: 'Nike Air Max 270',
        sales: 12,
        revenue: 10788,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 5,
        name: '小米手环8',
        sales: 38,
        revenue: 7600,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      }
    ])

    // 方法
    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    
    const handleDateChange = (dates) => {
      ElMessage.success('数据已更新')
    }
    
    const exportReport = () => {
      ElMessage.success('报告导出功能开发中...')
    }
    
    return {
      dateRange,
      salesChartType,
      totalRevenue,
      revenueChange,
      totalOrders,
      ordersChange,
      totalCustomers,
      customersChange,
      conversionRate,
      conversionChange,
      newCustomers,
      activeCustomers,
      repeatCustomers,
      avgOrderValue,
      hotProducts,
      // regionData,
      formatNumber,
      handleDateChange,
      exportReport
    }
  }
}
</script>

<style scoped>
.analytics {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.metrics-cards {
  margin-bottom: 30px;
}

.metric-card {
  height: 120px;
}

.metric-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.metric-icon.revenue {
  background-color: #e6f7ff;
  color: #1890ff;
}

.metric-icon.orders {
  background-color: #f6ffed;
  color: #52c41a;
}

.metric-icon.customers {
  background-color: #fff7e6;
  color: #fa8c16;
}

.metric-icon.conversion {
  background-color: #f9f0ff;
  color: #722ed1;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.metric-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.metric-change {
  font-size: 0.8rem;
}

.metric-change.positive {
  color: #52c41a;
}

.metric-change.negative {
  color: #ff4d4f;
}

.charts-section {
  margin-bottom: 30px;
}

.chart-card {
  height: 500px;
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

.product-analysis {
  margin-bottom: 30px;
}

.analysis-card {
  height: 500px;
}

.product-list {
  max-height: 400px;
  overflow-y: auto;
}

.product-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.product-item:last-child {
  border-bottom: none;
}

.product-rank {
  width: 30px;
  height: 30px;
  background-color: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #666;
  margin-right: 15px;
}

.product-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-right: 15px;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 0.9rem;
}

.product-sales {
  margin: 0 0 3px 0;
  color: #666;
  font-size: 0.8rem;
}

.product-revenue {
  margin: 0;
  color: #e74c3c;
  font-size: 0.8rem;
  font-weight: bold;
}

.customer-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.customer-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.region-analysis {
  margin-bottom: 30px;
}

.positive {
  color: #52c41a;
}

.negative {
  color: #ff4d4f;
}
</style> 