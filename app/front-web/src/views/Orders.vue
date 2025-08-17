<template>
  <div class="orders">
    <div class="page-header">
      <h1>订单管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="exportOrders">
          <el-icon>
            <Download/>
          </el-icon>
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
              <el-icon size="24">
                <Clock/>
              </el-icon>
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
              <el-icon size="24">
                <Van/>
              </el-icon>
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
              <el-icon size="24">
                <CircleCheck/>
              </el-icon>
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
              <el-icon size="24">
                <RefreshLeft/>
              </el-icon>
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
          <el-input v-model="filters.orderNo" placeholder="请输入订单号" clearable/>
        </el-form-item>
        <el-form-item label="买家信息">
          <el-input v-model="filters.customer" placeholder="买家姓名/手机号" clearable/>
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="待付款" value="pending_payment"/>
            <el-option label="待发货" value="pending_shipment"/>
            <el-option label="已发货" value="shipped"/>
            <el-option label="已完成" value="completed"/>
            <el-option label="已取消" value="cancelled"/>
            <el-option label="退款中" value="refunding"/>
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
        <el-table-column type="selection" width="55"/>
        <el-table-column label="订单信息" min-width="300">
          <template #default="{ row }">
            <div class="order-info">
              <div class="order-header">
                <span class="order-no">订单号：{{ row.order_number }}</span>
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
                    <h4 class="item-name">{{ item.product_name }}</h4>
                    <p class="item-specs">{{ item.spec_combination_id ? '规格：' + item.spec_combination_id : '' }}</p>
                    <p class="item-price">¥{{ item.price }} × {{ item.quantity }}</p>
                    <p class="item-status">状态：{{ getItemStatusText(item.item_status) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="买家信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <p class="customer-name">{{ row.user_name }}</p>
              <p class="customer-phone">{{ row.user_phone }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="订单金额" width="120">
          <template #default="{ row }">
            <div class="order-amount">
              <p class="total-amount">¥{{ row.total_amount }}</p>
              <p class="payment-method">商家金额</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="物流信息" width="150">
          <template #default="{ row }">
            <div class="logistics-info" v-if="row.items && row.items.length > 0">
              <div v-for="item in row.items" :key="item.id" class="logistics-item">
                <p v-if="item.shipping_company" class="logistics-company">{{ item.shipping_company }}</p>
                <p v-if="item.tracking_number" class="logistics-number">{{ item.tracking_number }}</p>
                <p v-else class="no-logistics">暂无物流</p>
              </div>
            </div>
            <span v-else class="no-logistics">暂无物流</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="下单时间" width="180"/>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewOrder(row)">
              查看详情
            </el-button>
            <el-button
                type="text"
                size="small"
                @click="shipOrder(row)"
                v-if="row.items && row.items.some(item => item.item_status === 'pending')"
            >
              发货
            </el-button>
            <el-button
                type="text"
                size="small"
                @click="viewLogistics(row)"
                v-if="row.items && row.items.some(item => item.shipping_company)"
            >
              查看物流
            </el-button>
            <el-button
                type="text"
                size="small"
                @click="refundOrder(row)"
                v-if="row.items && row.items.some(item => item.item_status === 'pending')"
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
            <el-option label="顺丰速运" value="SF"/>
            <el-option label="圆通速递" value="YTO"/>
            <el-option label="中通快递" value="ZTO"/>
            <el-option label="申通快递" value="STO"/>
            <el-option label="韵达速递" value="YD"/>
            <el-option label="京东物流" value="JD"/>
          </el-select>
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.number" placeholder="请输入物流单号"/>
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
import {onMounted, reactive, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {CircleCheck, Clock, Download, RefreshLeft, Van} from '@element-plus/icons-vue'
import orderService from "@/services/orderService.js";

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
    // 初始化数据
    onMounted(() => {
      loadOrders()
      loadOrderStats()
    })

    const loading = ref(false)
    const shipDialogVisible = ref(false)
    const shipping = ref(false)
    const selectedOrders = ref([])

    // 订单统计
    const orderStats = ref({
      pending: 0,
      shipped: 0,
      completed: 0,
      refund: 0
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
      orderItemId: null,
      company: '',
      number: ''
    })

    // 订单列表
    const orders = ref([])

    // 方法
    const loadOrders = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          per_page: pageSize.value
        }

        if (filters.status) {
          params.status = filters.status
        }
        const response = await orderService.getOrders(params)
        orders.value = response.data.list
        total.value = response.data.pagination.total
      } catch (error) {
        console.error('获取订单列表失败:', error)
        ElMessage.error('获取订单列表失败')
      } finally {
        loading.value = false
      }
    }

    const loadOrderStats = async () => {
      try {
        const response = await orderService.getOrderStatistics()
        // console.log(response.data)
        // ElMessage.success(response)
        orderStats.value = {
            pending: response.data.status_counts.pending || 0,
            shipped: response.data.status_counts.shipped || 0,
            completed: response.data.status_counts.delivered || 0,
            refund: response.data.status_counts.refunded || 0
          }
      } catch (error) {
        console.error('获取订单统计失败:', error)
      }
    }

    const handleSearch = () => {
      currentPage.value = 1
      loadOrders()
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

    const getItemStatusText = (status) => {
      const texts = {
        pending: '待处理',
        shipped: '已发货',
        delivered: '已送达',
        refunded: '已退款'
      }
      return texts[status] || '未知'
    }

    const viewOrder = (order) => {
      ElMessage.info('订单详情功能开发中...')
    }

    const shipOrder = (order) => {
      // 找到第一个待发货的商品
      const pendingItem = order.items.find(item => item.item_status === 'pending')
      if (!pendingItem) {
        ElMessage.warning('该订单没有待发货的商品')
        return
      }

      shipForm.orderItemId = pendingItem.id
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
      try {
        const response = await fetch(`/api/web/order/${shipForm.orderItemId}/ship`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            company: shipForm.company,
            tracking_number: shipForm.number
          })
        })

        const result = await response.json()

        if (result.code === 200) {
          ElMessage.success('发货成功')
          shipDialogVisible.value = false
          loadOrders() // 重新加载订单列表
        } else {
          ElMessage.error(result.message || '发货失败')
        }
      } catch (error) {
        console.error('发货失败:', error)
        ElMessage.error('发货失败')
      } finally {
        shipping.value = false
      }
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
      loadOrders()
    }

    const handleCurrentChange = (val) => {
      currentPage.value = val
      loadOrders()
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
      loadOrders,
      loadOrderStats,
      handleSearch,
      resetFilters,
      handleSelectionChange,
      getStatusType,
      getStatusText,
      getItemStatusText,
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