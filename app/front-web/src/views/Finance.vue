<template>
  <div class="finance">
    <div class="page-header">
      <h1>资金结算</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showWithdrawDialog">
          <el-icon><Wallet /></el-icon>
          申请提现
        </el-button>
      </div>
    </div>

    <!-- 账户概览 -->
    <el-row :gutter="20" class="account-overview">
      <el-col :span="8">
        <el-card class="balance-card">
          <div class="balance-content">
            <div class="balance-icon">
              <el-icon size="32"><Money /></el-icon>
            </div>
            <div class="balance-info">
              <div class="balance-label">可提现余额</div>
              <div class="balance-amount">¥{{ formatNumber(accountInfo.availableBalance) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="balance-card">
          <div class="balance-content">
            <div class="balance-icon frozen">
              <el-icon size="32"><Lock /></el-icon>
            </div>
            <div class="balance-info">
              <div class="balance-label">冻结金额</div>
              <div class="balance-amount">¥{{ formatNumber(accountInfo.frozenBalance) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="balance-card">
          <div class="balance-content">
            <div class="balance-icon total">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="balance-info">
              <div class="balance-label">累计收入</div>
              <div class="balance-amount">¥{{ formatNumber(accountInfo.totalIncome) }}</div>
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
            <span>银行卡管理</span>
            <el-button type="text" @click="showBankCardDialog" style="float: right;">
              <el-icon><Plus /></el-icon>
              添加银行卡
            </el-button>
          </template>
          <div class="bank-cards">
            <div 
              v-for="card in bankCards" 
              :key="card.id"
              class="bank-card-item"
              :class="{ active: selectedCard?.id === card.id }"
              @click="selectCard(card)"
            >
              <div class="card-info">
                <div class="bank-name">{{ card.bankName }}</div>
                <div class="card-number">**** **** **** {{ card.lastFourDigits }}</div>
                <div class="card-holder">{{ card.holderName }}</div>
              </div>
              <div class="card-actions">
                <el-button type="text" size="small" @click.stop="deleteCard(card)">
                  删除
                </el-button>
              </div>
            </div>
            <div v-if="bankCards.length === 0" class="no-cards">
              <el-icon size="48" color="#ddd"><CreditCard /></el-icon>
              <p>暂无银行卡，请添加银行卡</p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近提现记录</span>
          </template>
          <div class="withdraw-history">
            <div 
              v-for="record in withdrawHistory" 
              :key="record.id"
              class="withdraw-item"
            >
              <div class="withdraw-info">
                <div class="withdraw-amount">¥{{ formatNumber(record.amount) }}</div>
                <div class="withdraw-status">
                  <el-tag :type="getWithdrawStatusType(record.status)" size="small">
                    {{ getWithdrawStatusText(record.status) }}
                  </el-tag>
                </div>
              </div>
              <div class="withdraw-details">
                <div class="withdraw-time">{{ record.createTime }}</div>
                <div class="withdraw-bank">{{ record.bankName }} ****{{ record.lastFourDigits }}</div>
              </div>
            </div>
            <div v-if="withdrawHistory.length === 0" class="no-history">
              <p>暂无提现记录</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 账单明细 -->
    <el-card class="bill-details">
      <template #header>
        <span>账单明细</span>
        <div style="float: right;">
          <el-date-picker
            v-model="billDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleBillDateChange"
          />
          <el-button type="primary" @click="exportBills" style="margin-left: 10px;">
            导出账单
          </el-button>
        </div>
      </template>
      
      <el-table :data="billList" v-loading="billLoading">
        <el-table-column prop="orderNo" label="订单号" width="180" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getBillTypeType(row.type)">
              {{ getBillTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="150">
          <template #default="{ row }">
            <span :class="{ income: row.type === 'income', expense: row.type === 'expense' }">
              {{ row.type === 'income' ? '+' : '-' }}¥{{ formatNumber(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="createTime" label="时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getBillStatusType(row.status)" size="small">
              {{ getBillStatusText(row.status) }}
            </el-tag>
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

    <!-- 提现对话框 -->
    <el-dialog
      v-model="withdrawDialogVisible"
      title="申请提现"
      width="500px"
    >
      <el-form :model="withdrawForm" :rules="withdrawRules" ref="withdrawFormRef" label-width="100px">
        <el-form-item label="提现金额" prop="amount">
          <el-input-number 
            v-model="withdrawForm.amount" 
            :min="100" 
            :max="accountInfo.availableBalance"
            :precision="2"
            style="width: 100%"
          />
          <div class="form-tip">最低提现金额：¥100</div>
        </el-form-item>
        <el-form-item label="提现到" prop="cardId">
          <el-select v-model="withdrawForm.cardId" placeholder="选择银行卡" style="width: 100%">
            <el-option
              v-for="card in bankCards"
              :key="card.id"
              :label="`${card.bankName} ****${card.lastFourDigits}`"
              :value="card.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="withdrawForm.remark" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="withdrawDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitWithdraw" :loading="withdrawing">
          确认提现
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加银行卡对话框 -->
    <el-dialog
      v-model="bankCardDialogVisible"
      title="添加银行卡"
      width="500px"
    >
      <el-form :model="bankCardForm" :rules="bankCardRules" ref="bankCardFormRef" label-width="100px">
        <el-form-item label="持卡人" prop="holderName">
          <el-input v-model="bankCardForm.holderName" placeholder="请输入持卡人姓名" />
        </el-form-item>
        <el-form-item label="银行卡号" prop="cardNumber">
          <el-input v-model="bankCardForm.cardNumber" placeholder="请输入银行卡号" />
        </el-form-item>
        <el-form-item label="开户银行" prop="bankName">
          <el-select v-model="bankCardForm.bankName" placeholder="选择开户银行" style="width: 100%">
            <el-option label="中国工商银行" value="ICBC" />
            <el-option label="中国农业银行" value="ABC" />
            <el-option label="中国银行" value="BOC" />
            <el-option label="中国建设银行" value="CCB" />
            <el-option label="交通银行" value="BOCOM" />
            <el-option label="招商银行" value="CMB" />
            <el-option label="中信银行" value="CITIC" />
            <el-option label="浦发银行" value="SPDB" />
          </el-select>
        </el-form-item>
        <el-form-item label="预留手机" prop="phone">
          <el-input v-model="bankCardForm.phone" placeholder="请输入预留手机号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bankCardDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBankCard" :loading="addingCard">
          确认添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Wallet, 
  Money, 
  Lock, 
  TrendCharts, 
  Plus, 
  CreditCard 
} from '@element-plus/icons-vue'

export default {
  name: 'Finance',
  components: {
    Wallet,
    Money,
    Lock,
    TrendCharts,
    Plus,
    CreditCard
  },
  setup() {
    const withdrawDialogVisible = ref(false)
    const bankCardDialogVisible = ref(false)
    const withdrawing = ref(false)
    const addingCard = ref(false)
    const billLoading = ref(false)
    const withdrawFormRef = ref()
    const bankCardFormRef = ref()
    const selectedCard = ref(null)
    
    // 账户信息
    const accountInfo = ref({
      availableBalance: 125680.50,
      frozenBalance: 5000.00,
      totalIncome: 456789.00
    })
    
    // 银行卡列表
    const bankCards = ref([
      {
        id: 1,
        bankName: '中国工商银行',
        lastFourDigits: '1234',
        holderName: '张三'
      },
      {
        id: 2,
        bankName: '招商银行',
        lastFourDigits: '5678',
        holderName: '张三'
      }
    ])
    
    // 提现记录
    const withdrawHistory = ref([
      {
        id: 1,
        amount: 5000,
        status: 'success',
        createTime: '2024-01-15 14:30:00',
        bankName: '中国工商银行',
        lastFourDigits: '1234'
      },
      {
        id: 2,
        amount: 3000,
        status: 'pending',
        createTime: '2024-01-14 10:20:00',
        bankName: '招商银行',
        lastFourDigits: '5678'
      }
    ])
    
    // 账单列表
    const billList = ref([
      {
        id: 1,
        orderNo: 'DD202401150001',
        type: 'income',
        amount: 7999,
        description: '订单收入',
        createTime: '2024-01-15 14:30:00',
        status: 'success'
      },
      {
        id: 2,
        orderNo: 'TX202401150001',
        type: 'expense',
        amount: 5000,
        description: '提现',
        createTime: '2024-01-15 14:30:00',
        status: 'success'
      }
    ])
    
    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(156)
    const billDateRange = ref([])
    
    // 提现表单
    const withdrawForm = reactive({
      amount: 0,
      cardId: '',
      remark: ''
    })
    
    const withdrawRules = {
      amount: [
        { required: true, message: '请输入提现金额', trigger: 'blur' },
        { type: 'number', min: 100, message: '提现金额不能少于100元', trigger: 'blur' }
      ],
      cardId: [
        { required: true, message: '请选择提现银行卡', trigger: 'change' }
      ]
    }
    
    // 银行卡表单
    const bankCardForm = reactive({
      holderName: '',
      cardNumber: '',
      bankName: '',
      phone: ''
    })
    
    const bankCardRules = {
      holderName: [
        { required: true, message: '请输入持卡人姓名', trigger: 'blur' }
      ],
      cardNumber: [
        { required: true, message: '请输入银行卡号', trigger: 'blur' },
        { pattern: /^\d{16,19}$/, message: '请输入正确的银行卡号', trigger: 'blur' }
      ],
      bankName: [
        { required: true, message: '请选择开户银行', trigger: 'change' }
      ],
      phone: [
        { required: true, message: '请输入预留手机号', trigger: 'blur' },
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
      ]
    }
    
    // 方法
    const formatNumber = (num) => {
      return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    
    const showWithdrawDialog = () => {
      if (bankCards.value.length === 0) {
        ElMessage.warning('请先添加银行卡')
        return
      }
      withdrawForm.amount = 0
      withdrawForm.cardId = ''
      withdrawForm.remark = ''
      withdrawDialogVisible.value = true
    }
    
    const submitWithdraw = async () => {
      try {
        await withdrawFormRef.value.validate()
        withdrawing.value = true
        
        setTimeout(() => {
          ElMessage.success('提现申请提交成功')
          withdrawDialogVisible.value = false
          withdrawing.value = false
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善提现信息')
      }
    }
    
    const showBankCardDialog = () => {
      bankCardForm.holderName = ''
      bankCardForm.cardNumber = ''
      bankCardForm.bankName = ''
      bankCardForm.phone = ''
      bankCardDialogVisible.value = true
    }
    
    const submitBankCard = async () => {
      try {
        await bankCardFormRef.value.validate()
        addingCard.value = true
        
        setTimeout(() => {
          ElMessage.success('银行卡添加成功')
          bankCardDialogVisible.value = false
          addingCard.value = false
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善银行卡信息')
      }
    }
    
    const selectCard = (card) => {
      selectedCard.value = card
    }
    
    const deleteCard = async (card) => {
      try {
        await ElMessageBox.confirm(`确定要删除银行卡"${card.bankName} ****${card.lastFourDigits}"吗？`, '确认删除')
        ElMessage.success('银行卡删除成功')
      } catch {
        // 用户取消
      }
    }
    
    const getWithdrawStatusType = (status) => {
      const types = {
        pending: 'warning',
        success: 'success',
        failed: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getWithdrawStatusText = (status) => {
      const texts = {
        pending: '处理中',
        success: '成功',
        failed: '失败'
      }
      return texts[status] || '未知'
    }
    
    const getBillTypeType = (type) => {
      return type === 'income' ? 'success' : 'danger'
    }
    
    const getBillTypeText = (type) => {
      return type === 'income' ? '收入' : '支出'
    }
    
    const getBillStatusType = (status) => {
      const types = {
        success: 'success',
        pending: 'warning',
        failed: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getBillStatusText = (status) => {
      const texts = {
        success: '成功',
        pending: '处理中',
        failed: '失败'
      }
      return texts[status] || '未知'
    }
    
    const handleBillDateChange = (dates) => {
      ElMessage.success('账单数据已更新')
    }
    
    const exportBills = () => {
      ElMessage.success('账单导出功能开发中...')
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
      withdrawDialogVisible,
      bankCardDialogVisible,
      withdrawing,
      addingCard,
      billLoading,
      withdrawFormRef,
      bankCardFormRef,
      selectedCard,
      accountInfo,
      bankCards,
      withdrawHistory,
      billList,
      currentPage,
      pageSize,
      total,
      billDateRange,
      withdrawForm,
      withdrawRules,
      bankCardForm,
      bankCardRules,
      formatNumber,
      showWithdrawDialog,
      submitWithdraw,
      showBankCardDialog,
      submitBankCard,
      selectCard,
      deleteCard,
      getWithdrawStatusType,
      getWithdrawStatusText,
      getBillTypeType,
      getBillTypeText,
      getBillStatusType,
      getBillStatusText,
      handleBillDateChange,
      exportBills,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.finance {
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

.account-overview {
  margin-bottom: 30px;
}

.balance-card {
  height: 120px;
}

.balance-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.balance-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  background-color: #e6f7ff;
  color: #1890ff;
}

.balance-icon.frozen {
  background-color: #fff7e6;
  color: #fa8c16;
}

.balance-icon.total {
  background-color: #f6ffed;
  color: #52c41a;
}

.balance-info {
  flex: 1;
}

.balance-label {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.balance-amount {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
}

.quick-actions {
  margin-bottom: 30px;
}

.bank-cards {
  max-height: 300px;
  overflow-y: auto;
}

.bank-card-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.bank-card-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.bank-card-item.active {
  border-color: #409eff;
  background-color: #e6f7ff;
}

.card-info {
  flex: 1;
}

.bank-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.card-number {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 3px;
}

.card-holder {
  color: #999;
  font-size: 0.8rem;
}

.no-cards {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.withdraw-history {
  max-height: 300px;
  overflow-y: auto;
}

.withdraw-item {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.withdraw-item:last-child {
  border-bottom: none;
}

.withdraw-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.withdraw-amount {
  font-weight: bold;
  color: #333;
  font-size: 1.1rem;
}

.withdraw-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.withdraw-time {
  color: #666;
  font-size: 0.9rem;
}

.withdraw-bank {
  color: #999;
  font-size: 0.8rem;
}

.no-history {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.bill-details {
  margin-bottom: 30px;
}

.income {
  color: #52c41a;
  font-weight: bold;
}

.expense {
  color: #ff4d4f;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.form-tip {
  font-size: 0.8rem;
  color: #999;
  margin-top: 5px;
}
</style> 