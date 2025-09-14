import io from 'socket.io-client'

class WebSocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.userId = null
    this.merchantId = null
    this.chatRoomId = null
    this.messageHandlers = new Map()
  }

  // 连接WebSocket服务器
  connect(serverUrl = 'http://localhost:8001') {
    if (this.socket && this.isConnected) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      this.socket = io(serverUrl, {
        transports: ['websocket', 'polling'],
        timeout: 20000,
        forceNew: true
      })

      this.socket.on('connect', () => {
        console.log('WebSocket connected')
        this.isConnected = true
        resolve()
      })

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected')
        this.isConnected = false
      })

      this.socket.on('connect_error', (error) => {
        console.error('WebSocket connection error:', error)
        this.isConnected = false
        reject(error)
      })

      // 监听各种事件
      this.setupEventListeners()
    })
  }

  // 设置事件监听器
  setupEventListeners() {
    this.socket.on('user_joined', (data) => {
      console.log('User joined:', data)
      this.emit('user_joined', data)
    })

    this.socket.on('merchant_joined', (data) => {
      console.log('Merchant joined:', data)
      this.emit('merchant_joined', data)
    })

    this.socket.on('joined_chat_room', (data) => {
      console.log('Joined chat room:', data)
      this.chatRoomId = data.chat_room_id
      this.emit('joined_chat_room', data)
    })

    this.socket.on('new_message', (data) => {
      console.log('New message received:', data)
      this.emit('new_message', data)
    })

    this.socket.on('message_marked_read', (data) => {
      console.log('Message marked as read:', data)
      this.emit('message_marked_read', data)
    })

    this.socket.on('chat_history', (data) => {
      console.log('Chat history received:', data)
      this.emit('chat_history', data)
    })

    this.socket.on('online_status', (data) => {
      console.log('Online status:', data)
      this.emit('online_status', data)
    })

    this.socket.on('error', (data) => {
      console.error('WebSocket error:', data)
      this.emit('error', data)
    })
  }

  // 用户加入聊天
  joinAsUser(userId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.userId = userId
    this.socket.emit('user_join', { user_id: userId })
  }

  // 商家加入聊天
  joinAsMerchant(merchantId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.merchantId = merchantId
    this.socket.emit('merchant_join', { merchant_id: merchantId })
  }

  // 加入聊天室
  joinChatRoom(userId, merchantId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.socket.emit('join_chat_room', { 
      user_id: userId, 
      merchant_id: merchantId 
    })
  }

  // 发送消息
  sendMessage(content, messageType = 'text', fileUrl = null) {
    if (!this.isConnected || !this.chatRoomId) {
      throw new Error('Not connected to chat room')
    }

    const senderType = this.userId ? 'user' : 'merchant'
    const senderId = this.userId || this.merchantId

    this.socket.emit('send_message', {
      chat_room_id: this.chatRoomId,
      sender_type: senderType,
      sender_id: senderId,
      content: content,
      message_type: messageType,
      file_url: fileUrl
    })
  }

  // 标记消息为已读
  markMessageAsRead(messageId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.socket.emit('mark_message_read', { message_id: messageId })
  }

  // 获取聊天历史
  getChatHistory(page = 1, perPage = 20) {
    if (!this.isConnected || !this.chatRoomId) {
      throw new Error('Not connected to chat room')
    }
    
    this.socket.emit('get_chat_history', {
      chat_room_id: this.chatRoomId,
      page: page,
      per_page: perPage
    })
  }

  // 获取在线状态
  getOnlineStatus() {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.socket.emit('get_online_status', {
      user_id: this.userId,
      merchant_id: this.merchantId
    })
  }

  // 事件监听
  on(event, handler) {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, [])
    }
    this.messageHandlers.get(event).push(handler)
  }

  // 移除事件监听
  off(event, handler) {
    if (this.messageHandlers.has(event)) {
      const handlers = this.messageHandlers.get(event)
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  // 触发事件
  emit(event, data) {
    if (this.messageHandlers.has(event)) {
      this.messageHandlers.get(event).forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error)
        }
      })
    }
  }

  // 断开连接
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
      this.userId = null
      this.merchantId = null
      this.chatRoomId = null
      this.messageHandlers.clear()
    }
  }

  // 获取连接状态
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      userId: this.userId,
      merchantId: this.merchantId,
      chatRoomId: this.chatRoomId
    }
  }
}

// 创建单例实例
const websocketService = new WebSocketService()

export default websocketService
