<template>
  <div class="orders">
    <div class="page-header">
      <h1>订单管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="exportOrders">
          <el-icon><Download /></el-icon>
          导出订单
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ orderStats.pending }}</div>
              <div class="stat-label">待发货</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon shipped">
              <el-icon size="24"><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ orderStats.shipped }}</div>
              <div class="stat-label">已发货</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ orderStats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon refund">
              <el-icon size="24"><RefreshLeft /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ orderStats.refund }}</div>
              <div class="stat-label">退款中</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="订单号">
          <el-input v-model="filters.orderNo" placeholder="请输入订单号" clearable />
        </el-form-item>
        <el-form-item label="买家信息">
          <el-input v-model="filters.customer" placeholder="买家姓名/手机号" clearable />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="待付款" value="pending_payment" />
            <el-option label="待发货" value="pending_shipment" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="退款中" value="refunding" />
          </el-select>
        </el-form-item>
        <el-form-item label="下单时间">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card>
      <el-table
        :data="orders"
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="订单信息" min-width="300">
          <template #default="{ row }">
            <div class="order-info">
              <div class="order-header">
                <span class="order-no">订单号：{{ row.orderNo }}</span>
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </div>
              <div class="order-items">
                <div 
                  v-for="item in row.items" 
                  :key="item.id"
                  class="order-item"
                >
                  <el-image
                    :src="item.image"
                    class="item-image"
                    fit="cover"
                  />
                  <div class="item-info">
                    <h4 class="item-name">{{ item.name }}</h4>
                    <p class="item-specs">{{ item.specs }}</p>
                    <p class="item-price">¥{{ item.price }} × {{ item.quantity }}</p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="买家信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <p class="customer-name">{{ row.customerName }}</p>
              <p class="customer-phone">{{ row.customerPhone }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="订单金额" width="120">
          <template #default="{ row }">
            <div class="order-amount">
              <p class="total-amount">¥{{ row.totalAmount }}</p>
              <p class="payment-method">{{ row.paymentMethod }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="物流信息" width="150">
          <template #default="{ row }">
            <div class="logistics-info" v-if="row.logistics">
              <p class="logistics-company">{{ row.logistics.company }}</p>
              <p class="logistics-number">{{ row.logistics.number }}</p>
            </div>
            <span v-else class="no-logistics">暂无物流</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="下单时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewOrder(row)">
              查看详情
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="shipOrder(row)"
              v-if="row.status === 'pending_shipment'"
            >
              发货
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="viewLogistics(row)"
              v-if="row.logistics"
            >
              查看物流
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="refundOrder(row)"
              v-if="row.status === 'pending_shipment'"
              style="color: #f56c6c;"
            >
              同意退款
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 发货对话框 -->
    <el-dialog
      v-model="shipDialogVisible"
      title="订单发货"
      width="500px"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司">
          <el-select v-model="shipForm.company" placeholder="选择物流公司">
            <el-option label="顺丰速运" value="SF" />
            <el-option label="圆通速递" value="YTO" />
            <el-option label="中通快递" value="ZTO" />
            <el-option label="申通快递" value="STO" />
            <el-option label="韵达速递" value="YD" />
            <el-option label="京东物流" value="JD" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.number" placeholder="请输入物流单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShip" :loading="shipping">
          确认发货
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Download, 
  Clock, 
  Van, 
  CircleCheck, 
  RefreshLeft 
} from '@element-plus/icons-vue'

export default {
  name: 'Orders',
  components: {
    Download,
    Clock,
    Van,
    CircleCheck,
    RefreshLeft
  },
  setup() {
    const loading = ref(false)
    const shipDialogVisible = ref(false)
    const shipping = ref(false)
    const selectedOrders = ref([])
    
    // 订单统计
    const orderStats = ref({
      pending: 12,
      shipped: 8,
      completed: 156,
      refund: 3
    })
    
    // 筛选条件
    const filters = reactive({
      orderNo: '',
      customer: '',
      status: '',
      dateRange: []
    })
    
    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(189)
    
    // 发货表单
    const shipForm = reactive({
      company: '',
      number: ''
    })
    
    // 订单列表
    const orders = ref([
      {
        id: 1,
        orderNo: 'DD202401150001',
        status: 'pending_shipment',
        customerName: '张三',
        customerPhone: '138****8888',
        totalAmount: 7999,
        paymentMethod: '微信支付',
        createTime: '2024-01-15 14:30:00',
        items: [
          {
            id: 1,
            name: 'Apple iPhone 15 Pro',
            specs: '暗紫色 256GB',
            price: 7999,
            quantity: 1,
            image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
          }
        ]
      },
      {
        id: 2,
        orderNo: 'DD202401150002',
        status: 'shipped',
        customerName: '李四',
        customerPhone: '139****9999',
        totalAmount: 14999,
        paymentMethod: '支付宝',
        createTime: '2024-01-15 13:20:00',
        logistics: {
          company: '顺丰速运',
          number: 'SF1234567890'
        },
        items: [
          {
            id: 2,
            name: 'MacBook Pro 14英寸',
            specs: 'M2 Pro芯片 16G 512G',
            price: 14999,
            quantity: 1,
            image: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
          }
        ]
      },
      {
        id: 3,
        orderNo: 'DD202401150003',
        status: 'completed',
        customerName: '王五',
        customerPhone: '137****7777',
        totalAmount: 1899,
        paymentMethod: '微信支付',
        createTime: '2024-01-15 12:15:00',
        logistics: {
          company: '圆通速递',
          number: 'YT9876543210'
        },
        items: [
          {
            id: 3,
            name: 'AirPods Pro',
            specs: '白色',
            price: 1899,
            quantity: 1,
            image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
          }
        ]
      }
    ])
    
    // 方法
    const handleSearch = () => {
      loading.value = true
      setTimeout(() => {
        loading.value = false
        ElMessage.success('搜索完成')
      }, 1000)
    }
    
    const resetFilters = () => {
      filters.orderNo = ''
      filters.customer = ''
      filters.status = ''
      filters.dateRange = []
      handleSearch()
    }
    
    const handleSelectionChange = (selection) => {
      selectedOrders.value = selection
    }
    
    const getStatusType = (status) => {
      const types = {
        pending_payment: 'warning',
        pending_shipment: 'primary',
        shipped: 'success',
        completed: 'success',
        cancelled: 'info',
        refunding: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const texts = {
        pending_payment: '待付款',
        pending_shipment: '待发货',
        shipped: '已发货',
        completed: '已完成',
        cancelled: '已取消',
        refunding: '退款中'
      }
      return texts[status] || '未知'
    }
    
    const viewOrder = (order) => {
      ElMessage.info('订单详情功能开发中...')
    }
    
    const shipOrder = (order) => {
      shipForm.company = ''
      shipForm.number = ''
      shipDialogVisible.value = true
    }
    
    const confirmShip = async () => {
      if (!shipForm.company || !shipForm.number) {
        ElMessage.error('请填写完整的物流信息')
        return
      }
      
      shipping.value = true
      setTimeout(() => {
        ElMessage.success('发货成功')
        shipDialogVisible.value = false
        shipping.value = false
      }, 1000)
    }
    
    const viewLogistics = (order) => {
      ElMessage.info('物流跟踪功能开发中...')
    }
    
    const refundOrder = async (order) => {
      try {
        await ElMessageBox.confirm(`确定要同意订单"${order.orderNo}"的退款申请吗？`, '确认退款')
        ElMessage.success('退款处理成功')
      } catch {
        // 用户取消
      }
    }
    
    const exportOrders = () => {
      ElMessage.success('订单导出功能开发中...')
    }
    
    const handleSizeChange = (val) => {
      pageSize.value = val
      // 重新加载数据
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
      // 重新加载数据
    }
    
    return {
      loading,
      orderStats,
      filters,
      orders,
      selectedOrders,
      currentPage,
      pageSize,
      total,
      shipDialogVisible,
      shipForm,
      shipping,
      handleSearch,
      resetFilters,
      handleSelectionChange,
      getStatusType,
      getStatusText,
      viewOrder,
      shipOrder,
      confirmShip,
      viewLogistics,
      refundOrder,
      exportOrders,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.orders {
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

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon.pending {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-icon.shipped {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.completed {
  background-color: #f0f9ff;
  color: #409eff;
}

.stat-icon.refund {
  background-color: #fff2e8;
  color: #fa8c16;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.filter-card {
  margin-bottom: 20px;
}

.order-info {
  padding: 10px 0;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.order-no {
  font-weight: bold;
  color: #333;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.item-info {
  flex: 1;
}

.item-name {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 0.9rem;
}

.item-specs {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 0.8rem;
}

.item-price {
  margin: 0;
  color: #999;
  font-size: 0.8rem;
}

.customer-info {
  text-align: center;
}

.customer-name {
  margin: 0 0 5px 0;
  color: #333;
  font-weight: 500;
}

.customer-phone {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.order-amount {
  text-align: center;
}

.total-amount {
  margin: 0 0 5px 0;
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.1rem;
}

.payment-method {
  margin: 0;
  color: #666;
  font-size: 0.8rem;
}

.logistics-info {
  text-align: center;
}

.logistics-company {
  margin: 0 0 5px 0;
  color: #333;
  font-weight: 500;
}

.logistics-number {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.no-logistics {
  color: #999;
  font-size: 0.9rem;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style> 