<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-info">
        <h3>{{ userName || '用户' }}</h3>
        <div class="status">
          <span :class="['status-dot', isOnline ? 'online' : 'offline']"></span>
          <span>{{ isOnline ? '在线' : '离线' }}</span>
        </div>
      </div>
      <button @click="goBack" class="back-btn">← 返回</button>
    </div>

    <!-- 消息列表 -->
    <div class="messages-container" ref="messagesContainer">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="messages.length === 0" class="empty-message">
        暂无消息
      </div>
      <div v-else class="messages-list">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message-item', message.sender_type === 'merchant' ? 'merchant-message' : 'user-message']"
        >
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ formatTime(message.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-container">
      <div class="input-wrapper">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="输入回复..."
          class="message-input"
          :disabled="!isConnected"
        />
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim() || !isConnected"
          class="send-btn"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import websocketService from '@/services/websocketService'
import { getToken } from '@/utils/auth'

export default {
  name: 'CustomerServiceChat',
  data() {
    return {
      messages: [],
      newMessage: '',
      isConnected: false,
      isOnline: false,
      userId: null,
      userName: '',
      loading: true,
      merchantId: null
    }
  },
  mounted() {
    this.initChat()
  },
  beforeUnmount() {
    // 组件销毁时断开WebSocket连接
    websocketService.disconnect()
  },
  methods: {
    async initChat() {
      try {
        // 获取商家ID和用户ID
        this.merchantId = this.getMerchantIdFromToken()
        this.userId = this.$route.query.userId
        
        if (!this.merchantId || !this.userId) {
          this.$message.error('参数错误')
          this.goBack()
          return
        }

        // 连接WebSocket
        await websocketService.connect()
        this.isConnected = true

        // 商家加入聊天
        websocketService.joinAsMerchant(this.merchantId)

        // 加入聊天室
        websocketService.joinChatRoom(this.userId, this.merchantId)

        // 监听事件
        this.setupEventListeners()

        // 获取聊天历史
        websocketService.getChatHistory()

        // 获取在线状态
        websocketService.getOnlineStatus()

      } catch (error) {
        console.error('初始化聊天失败:', error)
        this.$message.error('连接失败，请重试')
      }
    },

    setupEventListeners() {
      // 监听加入聊天室成功
      websocketService.on('joined_chat_room', (data) => {
        console.log('已加入聊天室:', data)
      })

      // 监听新消息
      websocketService.on('new_message', (message) => {
        this.messages.push(message)
        this.scrollToBottom()
        
        // 如果是用户发送的消息，自动标记为已读
        if (message.sender_type === 'user') {
          websocketService.markMessageAsRead(message.id)
        }
      })

      // 监听聊天历史
      websocketService.on('chat_history', (data) => {
        this.messages = data.messages.reverse() // 反转消息顺序，最新的在底部
        this.loading = false
        this.scrollToBottom()
        
        // 标记所有用户消息为已读
        this.messages.forEach(message => {
          if (message.sender_type === 'user' && !message.is_read) {
            websocketService.markMessageAsRead(message.id)
          }
        })
      })

      // 监听在线状态
      websocketService.on('online_status', (status) => {
        this.isOnline = status.user_online
      })

      // 监听错误
      websocketService.on('error', (error) => {
        console.error('WebSocket错误:', error)
        this.$message.error(error.message || '发生错误')
      })
    },

    sendMessage() {
      if (!this.newMessage.trim() || !this.isConnected) {
        return
      }

      try {
        websocketService.sendMessage(this.newMessage.trim())
        this.newMessage = ''
      } catch (error) {
        console.error('发送消息失败:', error)
        this.$message.error('发送失败，请重试')
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },

    formatTime(timestamp) {
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
        return date.toLocaleDateString('zh-CN') + ' ' + 
               date.toLocaleTimeString('zh-CN', { 
                 hour: '2-digit', 
                 minute: '2-digit' 
               })
      }
    },

    getMerchantIdFromToken() {
      const token = getToken()
      if (!token) return null
      
      try {
        // 简单的JWT解析，实际项目中应该使用更安全的方式
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.merchant_id || payload.id
      } catch (error) {
        console.error('解析token失败:', error)
        return null
      }
    },

    goBack() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #fff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-info h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.status {
  display: flex;
  align-items: center;
  margin-top: 5px;
  font-size: 14px;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 5px;
}

.status-dot.online {
  background-color: #4CAF50;
}

.status-dot.offline {
  background-color: #ccc;
}

.back-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #007bff;
  cursor: pointer;
  padding: 5px 10px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f5f5;
}

.loading, .empty-message {
  text-align: center;
  color: #666;
  margin-top: 50px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  display: flex;
  margin-bottom: 10px;
}

.user-message {
  justify-content: flex-start;
}

.merchant-message {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.user-message .message-content {
  background-color: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.merchant-message .message-content {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-text {
  font-size: 16px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 5px;
}

.input-container {
  padding: 15px 20px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.input-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.message-input:focus {
  border-color: #007bff;
}

.message-input:disabled {
  background-color: #f5f5f5;
  color: #999;
}

.send-btn {
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.send-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
