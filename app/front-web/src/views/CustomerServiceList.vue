<template>
  <div class="customer-service-container">
    <div class="header">
      <h2>客服管理</h2>
      <div class="stats">
        <div class="stat-item">
          <span class="stat-label">在线用户:</span>
          <span class="stat-value">{{ onlineUsersCount }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">待回复:</span>
          <span class="stat-value">{{ pendingCount }}</span>
        </div>
      </div>
    </div>

    <div class="chat-rooms-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="chatRooms.length === 0" class="empty">
        暂无聊天会话
      </div>
      <div v-else>
        <div
          v-for="room in chatRooms"
          :key="room.id"
          class="chat-room-item"
          @click="openChat(room)"
        >
          <div class="room-info">
            <div class="user-info">
              <h4>{{ room.user_name }}</h4>
              <span class="user-phone">{{ room.user_phone }}</span>
            </div>
            <div class="last-message">
              <p>{{ room.last_message || '暂无消息' }}</p>
              <span class="message-time">{{ formatTime(room.last_message_at) }}</span>
            </div>
          </div>
          <div class="room-status">
            <span :class="['status-badge', room.status]">
              {{ getStatusText(room.status) }}
            </span>
            <span v-if="room.unread_count > 0" class="unread-badge">
              {{ room.unread_count }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import websocketService from '@/services/websocketService'
import { getToken } from '@/utils/auth'

export default {
  name: 'CustomerServiceList',
  data() {
    return {
      chatRooms: [],
      loading: true,
      onlineUsersCount: 0,
      pendingCount: 0,
      merchantId: null
    }
  },
  mounted() {
    this.initWebSocket()
    this.loadChatRooms()
  },
  beforeUnmount() {
    websocketService.disconnect()
  },
  methods: {
    async initWebSocket() {
      try {
        this.merchantId = this.getMerchantIdFromToken()
        if (!this.merchantId) {
          this.$message.error('商家信息错误')
          return
        }

        await websocketService.connect()
        websocketService.joinAsMerchant(this.merchantId)

        // 监听在线状态更新
        websocketService.on('online_status', (status) => {
          this.onlineUsersCount = status.online_users_count
        })

        // 监听新消息
        websocketService.on('new_message', (message) => {
          this.handleNewMessage(message)
        })

      } catch (error) {
        console.error('WebSocket初始化失败:', error)
        this.$message.error('连接失败')
      }
    },

    async loadChatRooms() {
      try {
        this.loading = true
        // 这里应该调用API获取聊天室列表
        // 暂时使用模拟数据
        this.chatRooms = [
          {
            id: 1,
            user_id: 1,
            user_name: '张三',
            user_phone: '13800138001',
            last_message: '请问这个商品什么时候发货？',
            last_message_at: new Date().toISOString(),
            status: 'active',
            unread_count: 2
          },
          {
            id: 2,
            user_id: 2,
            user_name: '李四',
            user_phone: '13800138002',
            last_message: '商品质量有问题，可以退换吗？',
            last_message_at: new Date(Date.now() - 3600000).toISOString(),
            status: 'replied',
            unread_count: 0
          }
        ]
        this.loading = false
      } catch (error) {
        console.error('加载聊天室列表失败:', error)
        this.$message.error('加载失败')
        this.loading = false
      }
    },

    handleNewMessage(message) {
      // 更新对应聊天室的最新消息
      const room = this.chatRooms.find(r => r.id === message.chat_room_id)
      if (room) {
        room.last_message = message.content
        room.last_message_at = message.created_at
        if (message.sender_type === 'user') {
          room.unread_count = (room.unread_count || 0) + 1
        }
      } else {
        // 如果是新的聊天室，添加到列表
        this.chatRooms.unshift({
          id: message.chat_room_id,
          user_id: message.sender_id,
          user_name: message.sender_name,
          user_phone: '',
          last_message: message.content,
          last_message_at: message.created_at,
          status: 'active',
          unread_count: 1
        })
      }
    },

    openChat(room) {
      this.$router.push({
        name: 'CustomerServiceChat',
        query: { userId: room.user_id }
      })
    },

    getStatusText(status) {
      const statusMap = {
        'active': '活跃',
        'replied': '已回复',
        'closed': '已关闭'
      }
      return statusMap[status] || '未知'
    },

    formatTime(timestamp) {
      if (!timestamp) return ''
      
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date

      if (diff < 60000) { // 1分钟内
        return '刚刚'
      } else if (diff < 3600000) { // 1小时内
        return Math.floor(diff / 60000) + '分钟前'
      } else if (diff < 86400000) { // 24小时内
        return date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    },

    getMerchantIdFromToken() {
      const token = getToken()
      if (!token) return null
      
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.merchant_id || payload.id
      } catch (error) {
        console.error('解析token失败:', error)
        return null
      }
    }
  }
}
</script>

<style scoped>
.customer-service-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h2 {
  margin: 0;
  color: #333;
}

.stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.stat-value {
  color: #007bff;
  font-weight: bold;
  font-size: 16px;
}

.chat-rooms-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
}

.chat-room-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.chat-room-item:hover {
  background-color: #f8f9fa;
}

.chat-room-item:last-child {
  border-bottom: none;
}

.room-info {
  flex: 1;
}

.user-info {
  margin-bottom: 5px;
}

.user-info h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.user-phone {
  font-size: 14px;
  color: #666;
}

.last-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-message p {
  margin: 0;
  font-size: 14px;
  color: #666;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}

.room-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.active {
  background-color: #e8f5e8;
  color: #4caf50;
}

.status-badge.replied {
  background-color: #e3f2fd;
  color: #2196f3;
}

.status-badge.closed {
  background-color: #f5f5f5;
  color: #999;
}

.unread-badge {
  background-color: #ff4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}
</style>
