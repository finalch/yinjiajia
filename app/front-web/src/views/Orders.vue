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
                <div class="order-meta">
                  <span class="order-id">订单ID: {{ row.order_number }}</span>
                  <span class="payment-time" v-if="row.paid_at">付款时间: {{ formatDateTime(row.paid_at) }}</span>
                </div>
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
                    <!-- <p class="item-price">¥{{ item.price }} × {{ item.quantity }}</p> -->
<!--                    <p class="item-status">状态：{{ getItemStatusText(item.item_status) }}</p>-->
                  </div>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="买家信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <p class="customer-phone">{{ row.user_phone }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="订单金额" width="120">
          <template #default="{ row }">
            <div class="order-amount">
              <p class="total-amount">¥{{ row.total_amount }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="支付状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getPaymentStatusType(row.status)" size="small">
              {{ getPaymentStatusText(row.status) }}
            </el-tag>
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
                v-if="row.ship_status === 'pending' && row.status === 'paid'"
            >
              发货
            </el-button>
            <el-button
                type="text"
                size="small"
                @click="viewLogistics(row)"
                v-if="row.ship_status !== 'pending'"
            >
              查看物流
            </el-button>
<!--            <el-button-->
<!--                type="text"-->
<!--                size="small"-->
<!--                @click="refundOrder(row)"-->
<!--                v-if="row.items && row.items.some(item => item.item_status === 'pending')"-->
<!--                style="color: #f56c6c;"-->
<!--            >-->
<!--              同意退款-->
<!--            </el-button>-->
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
        width="600px"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="发货仓库" required>
          <el-select 
            v-model="shipForm.warehouse_id" 
            placeholder="选择发货仓库"
            style="width: 100%"
            clearable
          >
            <el-option 
              v-for="warehouse in warehouseList" 
              :key="warehouse.id"
              :label="warehouse.name"
              :value="warehouse.id"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>{{ warehouse.name }}</span>
                <span style="color: #999; font-size: 12px;">{{ warehouse.address }}</span>
              </div>
            </el-option>
          </el-select>
          <div class="form-tip">请选择发货的仓库地址</div>
        </el-form-item>
        
        <el-form-item label="物流公司" required>
          <el-select 
            v-model="shipForm.company" 
            placeholder="选择物流公司"
            style="width: 100%"
            clearable
          >
            <el-option 
              v-for="company in logisticsCompanies" 
              :key="company.value"
              :label="company.label"
              :value="company.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="shipDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmShip" :loading="shipping">
            确认发货
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 物流查看对话框 -->
    <el-dialog
        v-model="logisticsDialogVisible"
        title="物流跟踪"
        width="800px"
    >
      <div v-if="logisticsLoading" class="logistics-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在查询物流信息...</span>
      </div>
      
      <div v-else-if="logisticsRoutes.length > 0" class="logistics-content">
        <div class="logistics-info">
          <div class="logistics-header">
            <div class="logistics-meta">
              <p class="logistics-company">
                <strong>物流公司：</strong>{{ getLogisticsCompanyName(currentLogisticsCompany) }}
              </p>
              <p class="logistics-tracking">
                <strong>运单号：</strong>
                <span class="shipping_no">{{ currentShippingNo }}</span>
                <el-button 
                  type="text" 
                  size="small" 
                  @click="copyTrackingNumber"
                  class="copy-btn"
                >
                  <el-icon><DocumentCopy /></el-icon>
                  复制
                </el-button>
              </p>
            </div>
          </div>
          
          <el-timeline>
            <el-timeline-item
              v-for="(route, index) in logisticsRoutes"
              :key="index"
              placement="top"
            >
              <div class="route-content">
                <span class="route-time">{{ route.time }}</span>
                <span class="route-address" v-if="route.address">{{ route.address }}</span>
                <span class="route-remark">{{ route.remark }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      
      <div v-else class="logistics-empty">
        <el-empty description="暂无物流信息" />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="logisticsDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="refreshLogistics" :loading="logisticsLoading">
            刷新
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {onMounted, reactive, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {CircleCheck, Clock, Download, RefreshLeft, Van, Loading, DocumentCopy} from '@element-plus/icons-vue'
import orderService from "@/services/orderService.js";
import request from "../api/request";
import warehouseService from '../services/warehouseService';
import logisticsService from '../services/logisticsService';

export default {
  name: 'Orders',
  components: {
    Download,
    Clock,
    Van,
    CircleCheck,
    RefreshLeft,
    Loading,
    DocumentCopy
  },
  setup() {
    // 初始化数据
    onMounted(() => {
      loadOrders()
      loadOrderStats()
      loadWarehouseList()
    })

    const loading = ref(false)
    const shipDialogVisible = ref(false)
    const shipping = ref(false)
    const selectedOrders = ref([])
    
    // 物流相关状态
    const logisticsDialogVisible = ref(false)
    const logisticsLoading = ref(false)
    const logisticsRoutes = ref([])
    const currentTrackingNumber = ref('')
    const currentShippingNo = ref('')
    const currentLogisticsCompany = ref('')
    const currentOrder = ref(null)

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
      order: null,
      company: '',
      number: '',
      warehouse_id: ''
    })
    
    // 仓库列表
    const warehouseList = ref([])
    
    // 物流公司列表
    const logisticsCompanies = ref([
      { label: '顺丰速运', value: 'SF', code: 'SF' },
      { label: '圆通速递', value: 'YTO', code: 'YTO' },
      { label: '中通快递', value: 'ZTO', code: 'ZTO' },
      { label: '申通快递', value: 'STO', code: 'STO' },
      { label: '韵达速递', value: 'YD', code: 'YD' },
      { label: '京东物流', value: 'JD', code: 'JD' },
      { label: '邮政EMS', value: 'EMS', code: 'EMS' },
      { label: '德邦快递', value: 'DBL', code: 'DBL' },
      { label: '百世快递', value: 'HTKY', code: 'HTKY' },
      { label: '天天快递', value: 'HHTT', code: 'HHTT' }
    ])

    // 订单列表
    const orders = ref([])

    // 方法
    // 加载仓库列表
    const loadWarehouseList = async () => {
      try {
        const result = await warehouseService.getWarehouseList({ status: 'active' })
        if (result.success) {
          warehouseList.value = result.data
        } else {
          console.error('加载仓库列表失败:', result.message)
        }
      } catch (error) {
        console.error('加载仓库列表失败:', error)
      }
    }
    
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
        refunding: 'danger',
        paid: 'success',
        pending: 'danger'
      }
      return types[status] || 'info'
    }

    const getStatusText = (status) => {
      const texts = {
        pending_payment: '待付款',
        paid: '已付款',
        pending_shipment: '待发货',
        shipped: '已发货',
        completed: '已完成',
        cancelled: '已取消',
        refunding: '退款中'
      }
      return texts[status] || '未知'
    }

    const getShipStatusText = (status) => {
      const texts = {
        pending: '待处理',
        shipped: '已发货',
        delivered: '已送达',
        refunded: '已退款'
      }
      return texts[status] || '未知'
    }
    
    const getPaymentStatusType = (status) => {
      const types = {
        pending_payment: 'warning',    // 待付款
        paid: 'success',              // 已付款
        pending_shipment: 'primary',  // 待发货
        shipped: 'success',           // 已发货
        completed: 'success',         // 已完成
        cancelled: 'info',            // 已取消
        refunding: 'danger'           // 退款中
      }
      return types[status] || 'info'
    }
    
    const getPaymentStatusText = (status) => {
      const texts = {
        pending_payment: '等待买家付款',
        paid: '已付款',
        completed: '已完成',
        refunding: '退款中',
        refunded: '已退款'
      }
      return texts[status] || '未知'
    }

    const viewOrder = (order) => {
      ElMessage.info('订单详情功能开发中...')
    }

    const shipOrder = (order) => {
      shipForm.order = order
      shipForm.company = ''
      shipForm.number = ''
      shipForm.warehouse_id = ''
      shipDialogVisible.value = true
    }

    const confirmShip = async () => {
      if (!shipForm.company || !shipForm.warehouse_id) {
        ElMessage.error('请填写完整的发货信息')
        return
      }

      shipping.value = true
      try {
        const response = await request.post(`/api/web/logistics/shipping`, {
            company: shipForm.company,
            order_id: shipForm.order.id,
            warehouse_id: shipForm.warehouse_id
        })
        if (response.data.code === 200) {
          ElMessage.success('发货成功')
          shipDialogVisible.value = false
          loadOrders() // 重新加载订单列表
        } else {
          ElMessage.error(response.data.message || '发货失败')
        }
      } catch (error) {
        console.error('发货失败:', error)
        ElMessage.error('发货失败')
      } finally {
        shipping.value = false
      }
    }

    const viewLogistics = async (order) => {
      // 检查订单是否有物流信息
      // const shippedItems = order.items?.filter(item => item.item_status === 'shipped' && item.tracking_number)
      
      // if (!shippedItems || shippedItems.length === 0) {
      //   ElMessage.warning('该订单暂无物流信息')
      //   return
      // }
      
      // 使用第一个已发货商品的物流信息
      // const firstShippedItem = shippedItems[0]
      currentTrackingNumber.value = order.tracking_number
      currentShippingNo.value = order.shipping_no
      currentLogisticsCompany.value = order.shipping_company
      currentOrder.value = order
      
      // 显示物流对话框
      logisticsDialogVisible.value = true
      
      // 查询物流信息
      await queryLogisticsInfo()
    }
    
    const queryLogisticsInfo = async () => {
      logisticsLoading.value = true
      try {
        const result = await logisticsService.queryLogisticsRoute(
          currentTrackingNumber.value,
          currentLogisticsCompany.value,
          currentShippingNo.value
        )
        
        if (result.success) {
          logisticsRoutes.value = result.data.routes || []

          if (logisticsRoutes.value.length === 0) {
            ElMessage.info('暂无物流跟踪信息')
          }
        } else {
          ElMessage.error(result.message || '查询物流信息失败')
          logisticsRoutes.value = []
        }
      } catch (error) {
        console.error('查询物流信息失败:', error)
        ElMessage.error('查询物流信息失败')
        logisticsRoutes.value = []
      } finally {
        logisticsLoading.value = false
      }
    }
    
    const refreshLogistics = async () => {
      await queryLogisticsInfo()
    }
    
    const getLogisticsCompanyName = (code) => {
      const company = logisticsCompanies.value.find(item => item.code === code)
      return company ? company.label : code
    }
    
    const copyTrackingNumber = async () => {
      try {
        await navigator.clipboard.writeText(currentShippingNo.value)
        ElMessage.success('运单号已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        // 备用方案：使用传统的复制方法
        const textArea = document.createElement('textarea')
        textArea.value = currentShippingNo.value
        document.body.appendChild(textArea)
        textArea.select()
        try {
          document.execCommand('copy')
          ElMessage.success('运单号已复制到剪贴板')
        } catch (fallbackError) {
          ElMessage.error('复制失败，请手动复制')
        }
        document.body.removeChild(textArea)
      }
    }
    
    
    // 格式化日期时间
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      const date = new Date(dateTime)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
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
      warehouseList,
      logisticsCompanies,
      // 物流相关
      logisticsDialogVisible,
      logisticsLoading,
      logisticsRoutes,
      currentTrackingNumber,
      currentShippingNo,
      currentLogisticsCompany,
      currentOrder,
      loadOrders,
      loadOrderStats,
      handleSearch,
      resetFilters,
      handleSelectionChange,
      getStatusType,
      getStatusText,
      getShipStatusText,
      getPaymentStatusType,
      getPaymentStatusText,
      viewOrder,
      shipOrder,
      confirmShip,
      viewLogistics,
      queryLogisticsInfo,
      refreshLogistics,
      getLogisticsCompanyName,
      copyTrackingNumber,
      refundOrder,
      exportOrders,
      formatDateTime,
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

/* 发货对话框样式 */
.form-tip {
  margin-top: 4px;
  color: #999;
  font-size: 12px;
  line-height: 1.4;
}

.order-info {
  padding: 12px;
}

.order-header {
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.order-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.order-id {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.payment-time {
  font-size: 12px;
  color: #666;
}

.order-info p {
  margin: 4px 0;
  font-size: 14px;
  color: #333;
}

.order-info strong {
  color: #666;
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 仓库选择器样式优化 */
:deep(.el-select-dropdown__item) {
  padding: 8px 20px;
}

:deep(.el-select-dropdown__item:hover) {
  background-color: #f5f7fa;
}

/* 响应式优化 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  .order-info {
    padding: 10px;
  }
  
  .order-info p {
    font-size: 13px;
  }
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
  color: #333;
  font-size: 0.8rem;
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
  font-size: 0.8rem;
}

.item-specs {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 0.7rem;
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

/* 物流对话框样式 */
.logistics-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.logistics-loading .el-icon {
  margin-right: 8px;
}

.logistics-content {
  padding: 20px 0;
}

.logistics-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.logistics-header h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.logistics-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.logistics-meta p {
  margin: 0;
  color: #666;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.logistics-company {
  font-weight: 500;
}

.logistics-tracking {
  display: flex;
  align-items: center;
  gap: 8px;
}

.shipping_no {
  font-family: 'Courier New', monospace;
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
}

.copy-btn {
  padding: 2px 6px !important;
  font-size: 12px !important;
  color: #409eff !important;
}

.copy-btn:hover {
  color: #66b1ff !important;
}

.route-content {
  padding: 1px 0;
  display: flex;
  align-items: center;
  gap: 1px;
  /* flex-wrap: wrap; */
}

.route-time {
  color: #666;
  font-size: 13px;
  font-weight: 500;
  min-width: 120px;
  flex-shrink: 0;
}

.route-address {
  color: #999;
  font-size: 12px;
  flex-shrink: 0;
}

.route-remark {
  color: #333;
  font-size: 14px;
  font-weight: 500;
  flex: 1;
}

.logistics-empty {
  padding: 40px 0;
  text-align: center;
}

/* Timeline 组件间距调整 */
:deep(.el-timeline) {
  padding-left: 0;
}

:deep(.el-timeline-item) {
  padding-bottom: 8px !important;
}

:deep(.el-timeline-item:last-child) {
  padding-bottom: 0 !important;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-timeline-item__content) {
  margin-top: -4px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  
  .logistics-meta p {
    font-size: 13px;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .logistics-tracking {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .shipping_no {
    font-size: 12px;
  }
  
  .copy-btn {
    font-size: 11px !important;
  }
  
  .route-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1px;
    padding: 3px 0;
  }
  
  .route-time {
    min-width: auto;
    font-size: 12px;
  }
  
  .route-address {
    font-size: 11px;
  }
  
  .route-remark {
    font-size: 13px;
  }
  
  /* 移动端 Timeline 间距进一步缩小 */
  :deep(.el-timeline-item) {
    padding-bottom: 4px !important;
  }
  
  :deep(.el-timeline-item__wrapper) {
    padding-left: 24px;
  }
  
  :deep(.el-timeline-item__content) {
    margin-top: -6px;
  }
}
</style> 