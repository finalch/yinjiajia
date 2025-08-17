<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <!--          <span class="merchant-info">-->
          <!--            <el-avatar :size="32" icon="UserFilled" />-->
          <!--            <span class="merchant-name">{{ merchantInfo?.merchant_number || '商家' }}</span>-->
          <!--            <el-icon><ArrowDown /></el-icon>-->
          <!--          </span>-->
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 数据卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sales">
              <el-icon size="24">
                <Money/>
              </el-icon>
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
              <el-icon size="24">
                <Document/>
              </el-icon>
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
              <el-icon size="24">
                <User/>
              </el-icon>
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
              <el-icon size="24">
                <Goods/>
              </el-icon>
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
<!--            <span>销售趋势</span>-->
            <el-radio-group v-model="salesPeriod" size="small" style="float: right;" @change="handlePeriodChange">
              <el-radio-button label="7">近7天</el-radio-button>
              <el-radio-button label="30">近30天</el-radio-button>
              <el-radio-button label="90">近90天</el-radio-button>
            </el-radio-group>
            <div class="chart-controls">
              <el-radio-group v-model="selectedMetric" size="small" @change="updateChart">
                <el-radio-button label="sales">销售额</el-radio-button>
                <el-radio-button label="orders">订单数</el-radio-button>
                <el-radio-button label="visitors">访客数</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container">
            <!-- 指标选择器 -->

            <!-- 图表容器 -->
            <div ref="chartRef" class="chart"></div>
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

    <!--    &lt;!&ndash; 快捷操作 &ndash;&gt;-->
    <!--    <el-row :gutter="20" class="quick-actions">-->
    <!--      <el-col :span="12">-->
    <!--        <el-card>-->
    <!--          <template #header>-->
    <!--            <span>快捷操作</span>-->
    <!--          </template>-->
    <!--          <div class="action-grid">-->
    <!--            <div class="action-item" @click="$router.push('/products/add')">-->
    <!--              <el-icon size="24"><Plus /></el-icon>-->
    <!--              <span>发布商品</span>-->
    <!--            </div>-->
    <!--            <div class="action-item" @click="$router.push('/orders')">-->
    <!--              <el-icon size="24"><Document /></el-icon>-->
    <!--              <span>处理订单</span>-->
    <!--            </div>-->
    <!--            <div class="action-item" @click="$router.push('/customer-service')">-->
    <!--              <el-icon size="24"><ChatDotRound /></el-icon>-->
    <!--              <span>客服咨询</span>-->
    <!--            </div>-->
    <!--            <div class="action-item" @click="$router.push('/finance')">-->
    <!--              <el-icon size="24"><Wallet /></el-icon>-->
    <!--              <span>资金提现</span>-->
    <!--            </div>-->
    <!--          </div>-->
    <!--        </el-card>-->
    <!--      </el-col>-->
    <!--      -->
    <!--      <el-col :span="12">-->
    <!--        <el-card>-->
    <!--          <template #header>-->
    <!--            <span>待处理事项</span>-->
    <!--          </template>-->
    <!--          <div class="todo-list">-->
    <!--            <div class="todo-item" v-for="todo in todoList" :key="todo.id">-->
    <!--              <div class="todo-content">-->
    <!--                <span class="todo-text">{{ todo.text }}</span>-->
    <!--                <el-tag :type="todo.type" size="small">{{ todo.count }}</el-tag>-->
    <!--              </div>-->
    <!--              <el-button type="text" size="small" @click="handleTodo(todo)">-->
    <!--                处理-->
    <!--              </el-button>-->
    <!--            </div>-->
    <!--          </div>-->
    <!--        </el-card>-->
    <!--      </el-col>-->
    <!--    </el-row>-->
  </div>
</template>

<script>
import {computed, onBeforeUnmount, onMounted, ref} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage} from 'element-plus'
import request from '@/api/request'
import authService from '../services/authService'
import analyticsService from '../services/analyticsService'
import * as echarts from 'echarts'
import {ArrowDown, ChatDotRound, Document, Goods, Money, PieChart, Plus, TrendCharts, User, UserFilled, Wallet} from '@element-plus/icons-vue'
import {clearAuth, getMerchantInfo} from '../router/auth'

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
    Wallet,
    ArrowDown,
    UserFilled
  },
  setup() {
    const router = useRouter()

    // 商家信息
    const merchantInfo = ref(getMerchantInfo())

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

    // 图表相关
    const chartRef = ref(null)
    const selectedMetric = ref('sales')
    let chartInstance = null

    // 待处理事项
    const todoList = ref([
      {id: 1, text: '待发货订单', count: 12, type: 'warning', path: '/orders'},
      {id: 2, text: '待审核商品', count: 3, type: 'info', path: '/products'},
      {id: 3, text: '待回复咨询', count: 8, type: 'primary', path: '/customer-service'},
      {id: 4, text: '待处理退款', count: 2, type: 'danger', path: '/after-sales'}
    ])

    // 从认证信息中获取商家ID
    const currentMerchantId = computed(() => {
      const userInfo = authService.getUserInfo()
      return userInfo?.merchant_id || userInfo?.id
    })
    const toPercent = (t, y) => {
      if (!y) return t > 0 ? 100 : 0
      return Math.round(((t - y) / y) * 1000) / 10
    }

    const generateData = async (days) => {
      try {
        // 将天数转换为对应的period参数
        let period = '7d'
        if (days === 30) period = '30d'
        else if (days === 90) period = '90d'
        
        const response = await analyticsService.getTrendsData(period)
        
        if (response.code === 200) {
          const data = response.data.trends.map(item => ({
            date: item.date,
            sales: item.sales || 0,
            orders: item.orders || 0,
            visitors: 0 // 暂时设为0，后续有访客数据时再更新
          }))
          return data.sort((a, b) => new Date(a.date) - new Date(b.date))
        } else {
          ElMessage.error('获取趋势数据失败')
          return generateMockData(days) // 失败时使用模拟数据
        }
      } catch (error) {
        console.error('获取趋势数据失败:', error)
        ElMessage.error('获取趋势数据失败，使用模拟数据')
        return generateMockData(days) // 失败时使用模拟数据
      }
    }
    // 生成模拟数据
    const generateMockData = (days) => {
      const data = []
      const today = new Date()

      // 基础值
      const baseSales = 35000    // 基础销售额
      const baseOrders = 80      // 基础订单数
      const baseVisitors = 800   // 基础访客数

      // 趋势系数（模拟上升趋势）
      const trendFactor = 0.02   // 每天增长2%

      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(date.getDate() - i)

        // 计算趋势值
        const trend = 1 + (trendFactor * (days - i))

        // 添加随机波动
        const randomFactor = 0.8 + Math.random() * 0.4 // 0.8-1.2

        // 周末效应（周末数据略低）
        const isWeekend = date.getDay() === 0 || date.getDay() === 6
        const weekendFactor = isWeekend ? 0.85 : 1.0

        // 生成数据
        const sales = Math.round((baseSales * trend * randomFactor * weekendFactor) / 1000) * 1000
        const orders = Math.round(baseOrders * trend * randomFactor * weekendFactor)
        const visitors = Math.round(baseVisitors * trend * randomFactor * weekendFactor)

        data.push({
          date: date.toISOString().split('T')[0],
          sales: sales,
          orders: orders,
          visitors: visitors
        })
      }

      return data
    }

    // 初始化图表
    const initChart = () => {
      console.log('🔍 开始初始化图表...')
      // 确保 DOM 元素存在且已渲染
      if (chartRef.value) {
        chartInstance = echarts.init(chartRef.value)
        console.log('✅ ECharts 实例创建成功:', chartInstance)
        updateChart() // 这里不需要await，因为initChart本身不是async
        // try {
        //   // 等待一下确保 DOM 完全渲染
        //   setTimeout(() => {
        //     if (chartRef.value && chartRef.value.offsetWidth > 0) {
        //       console.log('✅ DOM 元素准备就绪，开始创建 ECharts 实例')
        //       chartInstance = echarts.init(chartRef.value)
        //       console.log('✅ ECharts 实例创建成功:', chartInstance)
        //       updateChart()
        //     } else {
        //       console.log('❌ DOM 元素尺寸不足，offsetWidth:', chartRef.value?.offsetWidth)
        //     }
        //   }, 100)
        // } catch (error) {
        //   console.error('图表初始化失败:', error)
        // }
      } else {
        console.log('❌ chartRef 或 getBoundingClientRect 不存在')
      }
    }

    // 更新图表
    const updateChart = async () => {
      console.log('🔍 开始更新图表...')
      console.log('chartInstance:', chartInstance)

      if (!chartInstance) {
        console.log('❌ 图表实例不存在，无法更新')
        return
      }

      const days = parseInt(salesPeriod.value)
      const mockData = await generateData(days)
      console.log('📊 生成的模拟数据:', mockData)

      // 确保mockData是数组
      if (!Array.isArray(mockData)) {
        console.error('❌ 数据格式错误，mockData不是数组:', mockData)
        return
      }

      const option = {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e6e6e6',
          borderWidth: 1,
          textStyle: {
            color: '#333'
          },
          formatter: function (params) {
            const data = params[0]
            let value = data.value
            let unit = ''

            if (selectedMetric.value === 'sales') {
              value = '¥' + value.toLocaleString()
              unit = '销售额'
            } else if (selectedMetric.value === 'orders') {
              unit = '订单数'
            } else if (selectedMetric.value === 'visitors') {
              unit = '访客数'
            }

            return `
              <div style="padding: 8px;">
                <div style="font-weight: bold; margin-bottom: 8px;">${data.axisValue}</div>
                <div style="color: ${data.color}; font-size: 16px; font-weight: bold;">
                  ${unit}: ${value}
                </div>
              </div>
            `
          }
        },
        grid: {
          left: '5%',
          right: '5%',
          bottom: '0%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: mockData.map(item => item.date),
          axisLine: {
            lineStyle: {
              color: '#e6e6e6'
            },
            show: true
          },
          axisLabel: {
            color: '#666',
            fontSize: 12,
            margin: 8,
            interval: function(index, value) {
              // 根据时间周期智能显示标签
              const days = parseInt(salesPeriod.value)
              if (days <= 7) {
                // 7天内每天显示
                return true
              } else if (days <= 30) {
                // 30天内每3天显示一个
                return index % 3 === 0
              } else {
                // 90天内每7天显示一个
                return index % 7 === 0
              }
            },
            formatter: function (value) {
              return value.substring(5) // 只显示月-日
            }
          },
          axisTick: {
            show: true,
            length: 4,
            interval: 0 // 显示所有刻度线
          }
        },
        yAxis: {
          type: 'value',
          splitLine: {
            lineStyle: {
              color: '#f0f0f0',
              type: 'dashed'
            }
          },
          axisLine: {
            show: true
          },
          axisLabel: {
            color: '#666',
            fontSize: 12,
            formatter: function (value) {
              if (selectedMetric.value === 'sales') {
                return '¥' + (value / 10000).toFixed(1) + '万'
              }
              return value
            }
          }
        },
        series: [
          {
            name: selectedMetric.value === 'sales' ? '销售额' :
                selectedMetric.value === 'orders' ? '订单数' : '访客数',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 6,
            data: mockData.map(item => item[selectedMetric.value]),
            itemStyle: {
              color: selectedMetric.value === 'sales' ? '#1890ff' :
                  selectedMetric.value === 'orders' ? '#52c41a' : '#fa8c16'
            },
            lineStyle: {
              width: 3
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: selectedMetric.value === 'sales' ? 'rgba(24, 144, 255, 0.2)' :
                        selectedMetric.value === 'orders' ? 'rgba(82, 196, 26, 0.2)' : 'rgba(250, 140, 22, 0.2)'
                  },
                  {
                    offset: 1,
                    color: selectedMetric.value === 'sales' ? 'rgba(24, 144, 255, 0.05)' :
                        selectedMetric.value === 'orders' ? 'rgba(82, 196, 26, 0.05)' : 'rgba(250, 140, 22, 0.05)'
                  }
                ]
              }
            }
          }
        ]
      }

      console.log('📋 图表配置:', option)

      try {
        chartInstance.setOption(option)
        console.log('✅ 图表配置设置成功')
      } catch (error) {
        console.error('图表配置设置失败:', error)
      }
    }

    // 监听时间周期变化
    const handlePeriodChange = () => {
      updateChart() // 这里不需要await，因为handlePeriodChange本身不是async
    }

    const fetchDashboard = async () => {
      try {
        // 检查是否有商家ID
        if (!currentMerchantId.value) {
          console.error('❌ 无法获取商家ID，用户信息:', authService.getUserInfo())
          ElMessage.error('无法获取商家信息，请重新登录')
          return
        }

        console.log('🔍 请求仪表板数据，商家ID:', currentMerchantId.value)

        const res = await analyticsService.getDashboardData()

        console.log('📊 仪表板数据响应:', res)

        if (res.code === 200) {
          const d = res.data || {}
          const today = d.today || {}
          const yesterday = d.yesterday || {}
          const total = d.total || {}

          todaySales.value = Number(today.sales || 0)
          todayOrders.value = Number(today.orders || 0)
          totalProducts.value = Number(total.products || 0)

          salesChange.value = toPercent(today.sales || 0, yesterday.sales || 0)
          ordersChange.value = toPercent(today.orders || 0, yesterday.orders || 0)

          console.log('✅ 仪表板数据加载成功:', {
            todaySales: todaySales.value,
            todayOrders: todayOrders.value,
            totalProducts: totalProducts.value
          })
        } else {
          console.error('❌ 仪表板数据响应错误:', res)
          ElMessage.error(res?.message || '加载仪表板数据失败')
        }
      } catch (e) {
        console.error('❌ 加载仪表板数据失败:', e)
        ElMessage.error('加载仪表板数据失败，请重试')
      }
    }

    // 获取趋势对比数据
    const fetchTrendsComparison = async () => {
      try {
        const res = await analyticsService.getTrendsComparison()
        
        if (res.code === 200) {
          const data = res.data
          console.log('📊 趋势对比数据:', data)
          
          // 可以在这里处理趋势对比数据，比如显示在页面上
          // 或者用于计算更准确的增长率
        } else {
          console.error('❌ 趋势对比数据响应错误:', res)
        }
      } catch (e) {
        console.error('❌ 加载趋势对比数据失败:', e)
      }
    }

    onMounted(() => {
      console.log('🚀 组件挂载完成')
      fetchDashboard()
      fetchTrendsComparison() // 获取趋势对比数据
      initChart()
      // 等待 DOM 渲染完成后初始化图表
      // nextTick(() => {
      //   console.log('⏰ nextTick 回调执行')
      //   console.log('chartRef.value:', chartRef.value)
      //
      //   // 尝试初始化图表，如果失败则重试
      //   const tryInitChart = () => {
      //     console.log('🔄 尝试初始化图表...')
      //     if (chartRef.value && chartRef.value.offsetWidth > 0) {
      //       console.log('✅ DOM 元素准备就绪，调用 initChart')
      //       initChart()
      //     } else {
      //       console.log('⏳ DOM 还没准备好，延迟重试...')
      //       // 如果 DOM 还没准备好，延迟重试
      //       setTimeout(tryInitChart, 200)
      //     }
      //   }
      //
      //   tryInitChart()
      // })

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })

    onBeforeUnmount(() => {
      // 移除事件监听
      window.removeEventListener('resize', handleResize)
      // 销毁图表实例
      if (chartInstance) {
        chartInstance.dispose()
      }
    })

    // 处理窗口大小变化
    const handleResize = () => {
      if (chartInstance) {
        chartInstance.resize()
      }
    }

    // 格式化数字/处理待办保持不变
    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})
    }
    const handleTodo = (todo) => {
      router.push(todo.path)
    }

    const handleCommand = (command) => {
      switch (command) {
        case 'profile':
          router.push('/profile')
          break
        case 'settings':
          router.push('/settings')
          break
        case 'logout':
          clearAuth()
          router.push('/login')
          break
      }
    }

    return {
      merchantInfo,
      todaySales, salesChange, todayOrders, ordersChange,
      todayCustomers, customersChange, totalProducts, pendingReview,
      salesPeriod, todoList, formatNumber, handleTodo, handleCommand,
      chartRef, selectedMetric, updateChart, handlePeriodChange, handleResize
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
  height: 600px;
}

.chart-container {
  height: 400px;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.chart-controls {
  margin-bottom: 15px;
  text-align: left;
  padding: 0 10px;
}

.chart {
  flex: 1;
  min-height: 300px;
  width: 100%;
  height: 300px;
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

.analysis-card {
  height: 600px;
}
</style> 