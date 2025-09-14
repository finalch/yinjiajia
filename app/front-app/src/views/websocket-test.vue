<template>
  <div class="websocket-test">
    <h2>WebSocket 测试页面</h2>
    
    <div class="test-section">
      <h3>连接状态</h3>
      <p>状态: {{ connectionStatus.isConnected ? '已连接' : '未连接' }}</p>
      <p>用户ID: {{ connectionStatus.userId || '未设置' }}</p>
      <p>商家ID: {{ connectionStatus.merchantId || '未设置' }}</p>
      <p>聊天室ID: {{ connectionStatus.chatRoomId || '未设置' }}</p>
    </div>

    <div class="test-section">
      <h3>操作</h3>
      <button @click="connect" :disabled="connectionStatus.isConnected">连接</button>
      <button @click="disconnect" :disabled="!connectionStatus.isConnected">断开</button>
      <button @click="joinAsUser" :disabled="!connectionStatus.isConnected">以用户身份加入</button>
      <button @click="joinAsMerchant" :disabled="!connectionStatus.isConnected">以商家身份加入</button>
      <button @click="joinChatRoom" :disabled="!connectionStatus.isConnected">加入聊天室</button>
    </div>

    <div class="test-section">
      <h3>消息</h3>
      <input v-model="testMessage" placeholder="输入测试消息" />
      <button @click="sendTestMessage" :disabled="!connectionStatus.isConnected">发送消息</button>
    </div>

    <div class="test-section">
      <h3>消息历史</h3>
      <div class="messages">
        <div v-for="message in messages" :key="message.id" class="message">
          <strong>{{ message.sender_name }}:</strong> {{ message.content }}
          <small>({{ message.created_at }})</small>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import websocketService from '@/services/websocketService'

export default {
  name: 'WebSocketTest',
  data() {
    return {
      testMessage: '',
      messages: [],
      connectionStatus: {
        isConnected: false,
        userId: null,
        merchantId: null,
        chatRoomId: null
      }
    }
  },
  mounted() {
    this.setupEventListeners()
  },
  beforeUnmount() {
    websocketService.disconnect()
  },
  methods: {
    async connect() {
      try {
        await websocketService.connect()
        this.updateConnectionStatus()
        alert('连接成功')
      } catch (error) {
        alert('连接失败: ' + error.message)
      }
    },

    disconnect() {
      websocketService.disconnect()
      this.updateConnectionStatus()
      this.messages = []
      alert('已断开连接')
    },

    joinAsUser() {
      const userId = prompt('请输入用户ID:', '1')
      if (userId) {
        websocketService.joinAsUser(parseInt(userId))
        this.updateConnectionStatus()
        alert('已以用户身份加入')
      }
    },

    joinAsMerchant() {
      const merchantId = prompt('请输入商家ID:', '1')
      if (merchantId) {
        websocketService.joinAsMerchant(parseInt(merchantId))
        this.updateConnectionStatus()
        alert('已以商家身份加入')
      }
    },

    joinChatRoom() {
      const userId = prompt('请输入用户ID:', '1')
      const merchantId = prompt('请输入商家ID:', '1')
      if (userId && merchantId) {
        websocketService.joinChatRoom(parseInt(userId), parseInt(merchantId))
        this.updateConnectionStatus()
        alert('已加入聊天室')
      }
    },

    sendTestMessage() {
      if (!this.testMessage.trim()) {
        alert('请输入消息内容')
        return
      }

      try {
        websocketService.sendMessage(this.testMessage)
        this.testMessage = ''
        alert('消息已发送')
      } catch (error) {
        alert('发送失败: ' + error.message)
      }
    },

    setupEventListeners() {
      websocketService.on('new_message', (message) => {
        this.messages.push(message)
      })

      websocketService.on('chat_history', (data) => {
        this.messages = data.messages.reverse()
      })

      websocketService.on('joined_chat_room', (data) => {
        this.updateConnectionStatus()
        alert('已加入聊天室: ' + data.chat_room_id)
      })

      websocketService.on('error', (error) => {
        alert('错误: ' + error.message)
      })
    },

    updateConnectionStatus() {
      this.connectionStatus = websocketService.getConnectionStatus()
    }
  }
}
</script>

<style scoped>
.websocket-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.test-section h3 {
  margin-top: 0;
  color: #333;
}

button {
  margin: 5px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

input {
  padding: 8px;
  margin: 5px;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 200px;
}

.messages {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 10px;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 10px;
  padding: 5px;
  border-bottom: 1px solid #eee;
}

.message small {
  color: #666;
  margin-left: 10px;
}
</style>
