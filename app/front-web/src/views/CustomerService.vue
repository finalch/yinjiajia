<template>
  <div class="customer-service">
    <div class="page-header">
      <h1>客户服务</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showQuickReplyDialog">
          <el-icon><Plus /></el-icon>
          添加快捷短语
        </el-button>
      </div>
    </div>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-overview">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">待回复</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon today">
              <el-icon size="24"><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.today }}</div>
              <div class="stat-label">今日咨询</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon resolved">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.resolved }}</div>
              <div class="stat-label">已解决</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon satisfaction">
              <el-icon size="24"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.satisfaction }}%</div>
              <div class="stat-label">满意度</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 客服工作台 -->
    <el-row :gutter="20" class="service-workspace">
      <el-col :span="8">
        <!-- 咨询列表 -->
        <el-card class="chat-list-card">
          <template #header>
            <span>咨询列表</span>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索客户"
              size="small"
              style="width: 150px; float: right;"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </template>
          
          <div class="chat-list">
            <div 
              v-for="chat in filteredChats" 
              :key="chat.id"
              class="chat-item"
              :class="{ active: selectedChat?.id === chat.id }"
              @click="selectChat(chat)"
            >
              <el-avatar :src="chat.customerAvatar" />
              <div class="chat-info">
                <div class="customer-name">{{ chat.customerName }}</div>
                <div class="last-message">{{ chat.lastMessage }}</div>
                <div class="chat-meta">
                  <span class="time">{{ chat.lastTime }}</span>
                  <el-badge v-if="chat.unreadCount > 0" :value="chat.unreadCount" class="unread-badge" />
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <!-- 聊天窗口 -->
        <el-card class="chat-window-card" v-if="selectedChat">
          <template #header>
            <div class="chat-header">
              <div class="customer-info">
                <el-avatar :src="selectedChat.customerAvatar" />
                <span class="customer-name">{{ selectedChat.customerName }}</span>
                <el-tag :type="getStatusType(selectedChat.status)" size="small">
                  {{ getStatusText(selectedChat.status) }}
                </el-tag>
              </div>
              <div class="chat-actions">
                <el-button type="text" size="small" @click="transferChat">
                  转接
                </el-button>
                <el-button type="text" size="small" @click="endChat">
                  结束对话
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="chat-messages" ref="messagesContainer">
            <div 
              v-for="message in selectedChat.messages" 
              :key="message.id"
              class="message-item"
              :class="{ 'message-customer': message.type === 'customer', 'message-service': message.type === 'service' }"
            >
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
          </div>
          
          <div class="chat-input">
            <div class="quick-replies">
              <el-button 
                v-for="reply in quickReplies" 
                :key="reply.id"
                size="small"
                @click="useQuickReply(reply.content)"
              >
                {{ reply.title }}
              </el-button>
            </div>
            <div class="input-area">
              <el-input
                v-model="messageInput"
                type="textarea"
                :rows="3"
                placeholder="请输入回复内容..."
                @keydown.ctrl.enter="sendMessage"
              />
              <div class="input-actions">
                <el-button type="primary" @click="sendMessage" :disabled="!messageInput.trim()">
                  发送
                </el-button>
                <el-button @click="sendAutoReply">自动回复</el-button>
              </div>
            </div>
          </div>
        </el-card>
        
        <!-- 未选择聊天时的提示 -->
        <el-card class="no-chat-card" v-else>
          <div class="no-chat-content">
            <el-icon size="64" color="#ddd"><ChatDotRound /></el-icon>
            <p>请选择一个咨询对话</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷短语管理 -->
    <el-card class="quick-replies-card">
      <template #header>
        <span>快捷短语管理</span>
      </template>
      
      <el-table :data="quickReplies" border>
        <el-table-column prop="title" label="短语标题" width="200" />
        <el-table-column prop="content" label="短语内容" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryText(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="useCount" label="使用次数" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="editQuickReply(row)">
              编辑
            </el-button>
            <el-button type="text" size="small" @click="deleteQuickReply(row)" style="color: #f56c6c;">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 快捷短语对话框 -->
    <el-dialog
      v-model="quickReplyDialogVisible"
      :title="editingQuickReply ? '编辑快捷短语' : '添加快捷短语'"
      width="600px"
    >
      <el-form :model="quickReplyForm" :rules="quickReplyRules" ref="quickReplyFormRef" label-width="100px">
        <el-form-item label="短语标题" prop="title">
          <el-input v-model="quickReplyForm.title" placeholder="请输入短语标题" />
        </el-form-item>
        <el-form-item label="短语内容" prop="content">
          <el-input
            v-model="quickReplyForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入短语内容"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="quickReplyForm.category" placeholder="选择分类">
            <el-option label="问候语" value="greeting" />
            <el-option label="商品咨询" value="product" />
            <el-option label="订单问题" value="order" />
            <el-option label="售后服务" value="service" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickReplyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitQuickReply">
          {{ editingQuickReply ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Clock, 
  ChatDotRound, 
  CircleCheck, 
  Star, 
  Search 
} from '@element-plus/icons-vue'

export default {
  name: 'CustomerService',
  components: {
    Plus,
    Clock,
    ChatDotRound,
    CircleCheck,
    Star,
    Search
  },
  setup() {
    const quickReplyDialogVisible = ref(false)
    const editingQuickReply = ref(false)
    const selectedChat = ref(null)
    const messageInput = ref('')
    const searchKeyword = ref('')
    const messagesContainer = ref(null)
    const quickReplyFormRef = ref()
    
    // 统计数据
    const stats = ref({
      pending: 8,
      today: 45,
      resolved: 156,
      satisfaction: 95.2
    })
    
    // 快捷短语
    const quickReplies = ref([
      {
        id: 1,
        title: '欢迎语',
        content: '您好！欢迎咨询，我是客服小助手，很高兴为您服务！',
        category: 'greeting',
        useCount: 25
      },
      {
        id: 2,
        title: '商品介绍',
        content: '这款商品是我们店铺的热销产品，质量有保证，价格实惠，您可以放心购买。',
        category: 'product',
        useCount: 18
      },
      {
        id: 3,
        title: '发货说明',
        content: '我们会在24小时内为您发货，发货后会及时更新物流信息，请您耐心等待。',
        category: 'order',
        useCount: 12
      },
      {
        id: 4,
        title: '退换货政策',
        content: '我们支持7天无理由退换货，商品有质量问题可以申请退换货，我们会及时处理。',
        category: 'service',
        useCount: 8
      }
    ])
    
    // 聊天列表
    const chats = ref([
      {
        id: 1,
        customerName: '张三',
        customerAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        lastMessage: '请问这个商品什么时候发货？',
        lastTime: '14:30',
        unreadCount: 2,
        status: 'pending',
        messages: [
          {
            id: 1,
            type: 'customer',
            content: '您好，我想咨询一下商品发货的问题',
            time: '14:25'
          },
          {
            id: 2,
            type: 'service',
            content: '您好！欢迎咨询，我是客服小助手，很高兴为您服务！',
            time: '14:26'
          },
          {
            id: 3,
            type: 'customer',
            content: '请问这个商品什么时候发货？',
            time: '14:30'
          }
        ]
      },
      {
        id: 2,
        customerName: '李四',
        customerAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        lastMessage: '好的，谢谢',
        lastTime: '13:45',
        unreadCount: 0,
        status: 'resolved',
        messages: [
          {
            id: 1,
            type: 'customer',
            content: '商品收到了，质量很好',
            time: '13:40'
          },
          {
            id: 2,
            type: 'service',
            content: '感谢您的认可，如果还有其他问题随时联系我们',
            time: '13:42'
          },
          {
            id: 3,
            type: 'customer',
            content: '好的，谢谢',
            time: '13:45'
          }
        ]
      }
    ])
    
    // 快捷短语表单
    const quickReplyForm = reactive({
      title: '',
      content: '',
      category: ''
    })
    
    const quickReplyRules = {
      title: [
        { required: true, message: '请输入短语标题', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入短语内容', trigger: 'blur' }
      ],
      category: [
        { required: true, message: '请选择分类', trigger: 'change' }
      ]
    }
    
    // 计算属性
    const filteredChats = computed(() => {
      if (!searchKeyword.value) return chats.value
      return chats.value.filter(chat => 
        chat.customerName.includes(searchKeyword.value)
      )
    })
    
    // 方法
    const selectChat = (chat) => {
      selectedChat.value = chat
      // 滚动到底部
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    const sendMessage = () => {
      if (!messageInput.value.trim() || !selectedChat.value) return
      
      const newMessage = {
        id: Date.now(),
        type: 'service',
        content: messageInput.value,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      }
      
      selectedChat.value.messages.push(newMessage)
      selectedChat.value.lastMessage = messageInput.value
      selectedChat.value.lastTime = newMessage.time
      selectedChat.value.unreadCount = 0
      
      messageInput.value = ''
      
      // 滚动到底部
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    const useQuickReply = (content) => {
      messageInput.value = content
    }
    
    const sendAutoReply = () => {
      const autoReply = '感谢您的咨询，我们会尽快为您处理，请稍等片刻。'
      messageInput.value = autoReply
      sendMessage()
    }
    
    const transferChat = () => {
      ElMessage.info('转接功能开发中...')
    }
    
    const endChat = async () => {
      try {
        await ElMessageBox.confirm('确定要结束这个对话吗？', '确认结束')
        selectedChat.value.status = 'resolved'
        ElMessage.success('对话已结束')
      } catch {
        // 用户取消
      }
    }
    
    const showQuickReplyDialog = () => {
      editingQuickReply.value = false
      quickReplyForm.title = ''
      quickReplyForm.content = ''
      quickReplyForm.category = ''
      quickReplyDialogVisible.value = true
    }
    
    const editQuickReply = (reply) => {
      editingQuickReply.value = true
      quickReplyForm.title = reply.title
      quickReplyForm.content = reply.content
      quickReplyForm.category = reply.category
      quickReplyDialogVisible.value = true
    }
    
    const submitQuickReply = async () => {
      try {
        await quickReplyFormRef.value.validate()
        
        if (editingQuickReply.value) {
          ElMessage.success('快捷短语更新成功')
        } else {
          ElMessage.success('快捷短语添加成功')
        }
        
        quickReplyDialogVisible.value = false
      } catch (error) {
        ElMessage.error('请完善快捷短语信息')
      }
    }
    
    const deleteQuickReply = async (reply) => {
      try {
        await ElMessageBox.confirm(`确定要删除快捷短语"${reply.title}"吗？`, '确认删除')
        ElMessage.success('快捷短语删除成功')
      } catch {
        // 用户取消
      }
    }
    
    const getStatusType = (status) => {
      const types = {
        pending: 'warning',
        active: 'primary',
        resolved: 'success'
      }
      return types[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const texts = {
        pending: '待回复',
        active: '进行中',
        resolved: '已解决'
      }
      return texts[status] || '未知'
    }
    
    const getCategoryType = (category) => {
      const types = {
        greeting: 'success',
        product: 'primary',
        order: 'warning',
        service: 'info',
        other: 'default'
      }
      return types[category] || 'default'
    }
    
    const getCategoryText = (category) => {
      const texts = {
        greeting: '问候语',
        product: '商品咨询',
        order: '订单问题',
        service: '售后服务',
        other: '其他'
      }
      return texts[category] || '未知'
    }
    
    return {
      quickReplyDialogVisible,
      editingQuickReply,
      selectedChat,
      messageInput,
      searchKeyword,
      messagesContainer,
      quickReplyFormRef,
      stats,
      quickReplies,
      chats,
      filteredChats,
      quickReplyForm,
      quickReplyRules,
      selectChat,
      sendMessage,
      useQuickReply,
      sendAutoReply,
      transferChat,
      endChat,
      showQuickReplyDialog,
      editQuickReply,
      submitQuickReply,
      deleteQuickReply,
      getStatusType,
      getStatusText,
      getCategoryType,
      getCategoryText
    }
  }
}
</script>

<style scoped>
.customer-service {
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

.stats-overview {
  margin-bottom: 30px;
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

.stat-icon.today {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-icon.resolved {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.satisfaction {
  background-color: #f9f0ff;
  color: #722ed1;
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

.service-workspace {
  margin-bottom: 30px;
}

.chat-list-card {
  height: 600px;
}

.chat-list {
  height: 500px;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.chat-item:hover {
  background-color: #f5f5f5;
}

.chat-item.active {
  background-color: #e6f7ff;
}

.chat-info {
  flex: 1;
  margin-left: 10px;
}

.customer-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.last-message {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.time {
  color: #999;
  font-size: 0.8rem;
}

.chat-window-card {
  height: 600px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-messages {
  height: 400px;
  overflow-y: auto;
  padding: 20px;
  background-color: #f8f9fa;
}

.message-item {
  margin-bottom: 15px;
}

.message-customer {
  text-align: left;
}

.message-service {
  text-align: right;
}

.message-content {
  display: inline-block;
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 10px;
  word-wrap: break-word;
}

.message-customer .message-content {
  background-color: #fff;
  border: 1px solid #e6e6e6;
}

.message-service .message-content {
  background-color: #409eff;
  color: #fff;
}

.message-text {
  margin-bottom: 5px;
}

.message-time {
  font-size: 0.8rem;
  opacity: 0.7;
}

.chat-input {
  padding: 20px;
}

.quick-replies {
  margin-bottom: 15px;
}

.quick-replies .el-button {
  margin-right: 10px;
  margin-bottom: 5px;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area .el-input {
  flex: 1;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.no-chat-card {
  height: 600px;
}

.no-chat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
}

.quick-replies-card {
  margin-bottom: 30px;
}
</style> 