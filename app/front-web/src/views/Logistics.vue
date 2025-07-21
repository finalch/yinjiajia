<template>
  <div class="logistics">
    <div class="page-header">
      <h1>物流管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showBatchShipDialog">
          <el-icon><Van /></el-icon>
          批量发货
        </el-button>
      </div>
    </div>

    <!-- 物流统计 -->
    <el-row :gutter="20" class="logistics-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
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
              <div class="stat-value">{{ stats.shipped }}</div>
              <div class="stat-label">已发货</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon delivered">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.delivered }}</div>
              <div class="stat-label">已签收</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon exception">
              <el-icon size="24"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.exception }}</div>
              <div class="stat-label">异常件</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 物流公司管理 -->
    <el-card class="company-management">
      <template #header>
        <span>物流公司管理</span>
        <el-button type="text" @click="showCompanyDialog" style="float: right;">
          <el-icon><Plus /></el-icon>
          添加物流公司
        </el-button>
      </template>
      
      <el-table :data="logisticsCompanies" border>
        <el-table-column prop="name" label="公司名称" width="150" />
        <el-table-column prop="code" label="公司代码" width="120" />
        <el-table-column prop="contact" label="联系方式" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="备注" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="editCompany(row)">
              编辑
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleCompanyStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteCompany(row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 物流订单列表 -->
    <el-card class="logistics-orders">
      <template #header>
        <span>物流订单</span>
        <div style="float: right;">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索订单号/物流单号"
            style="width: 200px; margin-right: 10px;"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
        </div>
      </template>
      
      <el-table :data="logisticsOrders" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="orderNo" label="订单号" width="180" />
        <el-table-column prop="trackingNo" label="物流单号" width="180" />
        <el-table-column prop="company" label="物流公司" width="120" />
        <el-table-column prop="status" label="物流状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getLogisticsStatusType(row.status)">
              {{ getLogisticsStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="customerName" label="收件人" width="120" />
        <el-table-column prop="customerPhone" label="联系电话" width="150" />
        <el-table-column prop="address" label="收货地址" min-width="200" />
        <el-table-column prop="createTime" label="发货时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="viewTracking(row)">
              查看物流
            </el-button>
            <el-button type="text" size="small" @click="editTracking(row)">
              修改物流
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="resendTracking(row)"
              v-if="row.status === 'exception'"
            >
              重新发货
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

    <!-- 物流公司对话框 -->
    <el-dialog
      v-model="companyDialogVisible"
      :title="editingCompany ? '编辑物流公司' : '添加物流公司'"
      width="500px"
    >
      <el-form :model="companyForm" :rules="companyRules" ref="companyFormRef" label-width="100px">
        <el-form-item label="公司名称" prop="name">
          <el-input v-model="companyForm.name" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="公司代码" prop="code">
          <el-input v-model="companyForm.code" placeholder="请输入公司代码" />
        </el-form-item>
        <el-form-item label="联系方式" prop="contact">
          <el-input v-model="companyForm.contact" placeholder="请输入联系方式" />
        </el-form-item>
        <el-form-item label="公司状态" prop="status">
          <el-radio-group v-model="companyForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="companyForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="companyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCompany" :loading="submitting">
          {{ editingCompany ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量发货对话框 -->
    <el-dialog
      v-model="batchShipDialogVisible"
      title="批量发货"
      width="800px"
    >
      <el-form :model="batchShipForm" :rules="batchShipRules" ref="batchShipFormRef" label-width="100px">
        <el-form-item label="物流公司" prop="companyId">
          <el-select v-model="batchShipForm.companyId" placeholder="选择物流公司" style="width: 100%">
            <el-option
              v-for="company in activeCompanies"
              :key="company.id"
              :label="company.name"
              :value="company.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="发货订单">
          <el-table :data="batchShipForm.orders" border>
            <el-table-column prop="orderNo" label="订单号" width="180" />
            <el-table-column prop="customerName" label="收件人" width="120" />
            <el-table-column prop="customerPhone" label="联系电话" width="150" />
            <el-table-column prop="address" label="收货地址" />
            <el-table-column label="物流单号" width="180">
              <template #default="{ row }">
                <el-input v-model="row.trackingNo" placeholder="请输入物流单号" />
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchShipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBatchShip" :loading="batchShipping">
          确认发货
        </el-button>
      </template>
    </el-dialog>

    <!-- 物流跟踪对话框 -->
    <el-dialog
      v-model="trackingDialogVisible"
      title="物流跟踪"
      width="600px"
    >
      <div class="tracking-info">
        <div class="tracking-header">
          <div class="tracking-number">物流单号：{{ selectedOrder.trackingNo }}</div>
          <div class="tracking-company">物流公司：{{ selectedOrder.company }}</div>
        </div>
        <div class="tracking-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in trackingActivities"
              :key="index"
              :timestamp="activity.time"
              :type="activity.type"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Van, 
  Clock, 
  CircleCheck, 
  Warning, 
  Plus, 
  Search 
} from '@element-plus/icons-vue'

export default {
  name: 'Logistics',
  components: {
    Van,
    Clock,
    CircleCheck,
    Warning,
    Plus,
    Search
  },
  setup() {
    const loading = ref(false)
    const companyDialogVisible = ref(false)
    const batchShipDialogVisible = ref(false)
    const trackingDialogVisible = ref(false)
    const submitting = ref(false)
    const batchShipping = ref(false)
    const editingCompany = ref(false)
    const companyFormRef = ref()
    const batchShipFormRef = ref()
    const searchKeyword = ref('')
    const selectedOrder = ref({})
    
    // 统计数据
    const stats = ref({
      pending: 12,
      shipped: 8,
      delivered: 156,
      exception: 3
    })
    
    // 物流公司列表
    const logisticsCompanies = ref([
      {
        id: 1,
        name: '顺丰速运',
        code: 'SF',
        contact: '95338',
        status: 'active',
        description: '全国知名快递公司'
      },
      {
        id: 2,
        name: '圆通速递',
        code: 'YTO',
        contact: '95554',
        status: 'active',
        description: '性价比高的快递公司'
      },
      {
        id: 3,
        name: '中通快递',
        code: 'ZTO',
        contact: '95311',
        status: 'active',
        description: '服务网点覆盖广泛'
      },
      {
        id: 4,
        name: '申通快递',
        code: 'STO',
        contact: '95543',
        status: 'inactive',
        description: '暂停合作'
      }
    ])
    
    // 物流订单列表
    const logisticsOrders = ref([
      {
        id: 1,
        orderNo: 'DD202401150001',
        trackingNo: 'SF1234567890',
        company: '顺丰速运',
        status: 'shipped',
        customerName: '张三',
        customerPhone: '138****8888',
        address: '北京市朝阳区xxx街道xxx小区',
        createTime: '2024-01-15 14:30:00'
      },
      {
        id: 2,
        orderNo: 'DD202401150002',
        trackingNo: 'YT9876543210',
        company: '圆通速递',
        status: 'delivered',
        customerName: '李四',
        customerPhone: '139****9999',
        address: '上海市浦东新区xxx路xxx号',
        createTime: '2024-01-15 13:20:00'
      },
      {
        id: 3,
        orderNo: 'DD202401150003',
        trackingNo: 'ZT1234567890',
        company: '中通快递',
        status: 'exception',
        customerName: '王五',
        customerPhone: '137****7777',
        address: '广州市天河区xxx大道xxx号',
        createTime: '2024-01-15 12:15:00'
      }
    ])
    
    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(189)
    
    // 物流公司表单
    const companyForm = reactive({
      name: '',
      code: '',
      contact: '',
      status: 'active',
      description: ''
    })
    
    const companyRules = {
      name: [
        { required: true, message: '请输入公司名称', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入公司代码', trigger: 'blur' }
      ],
      contact: [
        { required: true, message: '请输入联系方式', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择公司状态', trigger: 'change' }
      ]
    }
    
    // 批量发货表单
    const batchShipForm = reactive({
      companyId: '',
      orders: [
        {
          orderNo: 'DD202401150004',
          customerName: '赵六',
          customerPhone: '136****6666',
          address: '深圳市南山区xxx路xxx号',
          trackingNo: ''
        },
        {
          orderNo: 'DD202401150005',
          customerName: '钱七',
          customerPhone: '135****5555',
          address: '杭州市西湖区xxx街xxx号',
          trackingNo: ''
        }
      ]
    })
    
    const batchShipRules = {
      companyId: [
        { required: true, message: '请选择物流公司', trigger: 'change' }
      ]
    }
    
    // 物流跟踪信息
    const trackingActivities = ref([
      {
        content: '快件已签收，签收人：门卫',
        time: '2024-01-16 10:30:00',
        type: 'success'
      },
      {
        content: '快件正在派送中，派送员：李师傅',
        time: '2024-01-16 08:15:00',
        type: 'primary'
      },
      {
        content: '快件已到达派送点',
        time: '2024-01-15 20:30:00',
        type: 'info'
      },
      {
        content: '快件运输中',
        time: '2024-01-15 16:45:00',
        type: 'info'
      },
      {
        content: '快件已发出',
        time: '2024-01-15 14:30:00',
        type: 'info'
      }
    ])
    
    // 计算属性
    const activeCompanies = computed(() => {
      return logisticsCompanies.value.filter(company => company.status === 'active')
    })
    
    // 方法
    const getLogisticsStatusType = (status) => {
      const types = {
        pending: 'warning',
        shipped: 'primary',
        delivered: 'success',
        exception: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getLogisticsStatusText = (status) => {
      const texts = {
        pending: '待发货',
        shipped: '已发货',
        delivered: '已签收',
        exception: '异常件'
      }
      return texts[status] || '未知'
    }
    
    const handleSearch = () => {
      loading.value = true
      setTimeout(() => {
        loading.value = false
        ElMessage.success('搜索完成')
      }, 1000)
    }
    
    const showCompanyDialog = () => {
      editingCompany.value = false
      companyForm.name = ''
      companyForm.code = ''
      companyForm.contact = ''
      companyForm.status = 'active'
      companyForm.description = ''
      companyDialogVisible.value = true
    }
    
    const editCompany = (company) => {
      editingCompany.value = true
      companyForm.name = company.name
      companyForm.code = company.code
      companyForm.contact = company.contact
      companyForm.status = company.status
      companyForm.description = company.description
      companyDialogVisible.value = true
    }
    
    const submitCompany = async () => {
      try {
        await companyFormRef.value.validate()
        submitting.value = true
        
        setTimeout(() => {
          if (editingCompany.value) {
            ElMessage.success('物流公司更新成功')
          } else {
            ElMessage.success('物流公司添加成功')
          }
          companyDialogVisible.value = false
          submitting.value = false
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善物流公司信息')
      }
    }
    
    const toggleCompanyStatus = async (company) => {
      const action = company.status === 'active' ? '禁用' : '启用'
      try {
        await ElMessageBox.confirm(`确定要${action}物流公司"${company.name}"吗？`, '确认操作')
        company.status = company.status === 'active' ? 'inactive' : 'active'
        ElMessage.success(`${action}成功`)
      } catch {
        // 用户取消
      }
    }
    
    const deleteCompany = async (company) => {
      try {
        await ElMessageBox.confirm(`确定要删除物流公司"${company.name}"吗？此操作不可恢复！`, '确认删除', {
          type: 'warning'
        })
        ElMessage.success('删除成功')
      } catch {
        // 用户取消
      }
    }
    
    const showBatchShipDialog = () => {
      batchShipForm.companyId = ''
      batchShipForm.orders.forEach(order => {
        order.trackingNo = ''
      })
      batchShipDialogVisible.value = true
    }
    
    const submitBatchShip = async () => {
      try {
        await batchShipFormRef.value.validate()
        batchShipping.value = true
        
        setTimeout(() => {
          ElMessage.success('批量发货成功')
          batchShipDialogVisible.value = false
          batchShipping.value = false
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善发货信息')
      }
    }
    
    const viewTracking = (order) => {
      selectedOrder.value = order
      trackingDialogVisible.value = true
    }
    
    const editTracking = (order) => {
      ElMessage.info('修改物流功能开发中...')
    }
    
    const resendTracking = (order) => {
      ElMessage.info('重新发货功能开发中...')
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
      companyDialogVisible,
      batchShipDialogVisible,
      trackingDialogVisible,
      submitting,
      batchShipping,
      editingCompany,
      companyFormRef,
      batchShipFormRef,
      searchKeyword,
      selectedOrder,
      stats,
      logisticsCompanies,
      logisticsOrders,
      currentPage,
      pageSize,
      total,
      companyForm,
      companyRules,
      batchShipForm,
      batchShipRules,
      trackingActivities,
      activeCompanies,
      getLogisticsStatusType,
      getLogisticsStatusText,
      handleSearch,
      showCompanyDialog,
      editCompany,
      submitCompany,
      toggleCompanyStatus,
      deleteCompany,
      showBatchShipDialog,
      submitBatchShip,
      viewTracking,
      editTracking,
      resendTracking,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.logistics {
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

.logistics-stats {
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
  background-color: #fff7e6;
  color: #fa8c16;
}

.stat-icon.shipped {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-icon.delivered {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.exception {
  background-color: #fff2e8;
  color: #ff4d4f;
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

.company-management {
  margin-bottom: 20px;
}

.logistics-orders {
  margin-bottom: 30px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.tracking-info {
  padding: 20px 0;
}

.tracking-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.tracking-number {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.tracking-company {
  color: #666;
  font-size: 0.9rem;
}

.tracking-timeline {
  max-height: 400px;
  overflow-y: auto;
}
</style> 