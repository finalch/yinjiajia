import { apiConfig } from '../config/api.js'
import { getToken } from '../utils/auth.js'

class WebSocketService {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.userId = null
    this.merchantId = null
    this.chatRoomId = null
    this.messageHandlers = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
  }

  // 连接WebSocket服务器
  connect(serverUrl = null) {
    if (this.socket && this.isConnected) {
      return Promise.resolve()
    }

    // 获取认证token
    const token = getToken()
    if (!token) {
      return Promise.reject(new Error('未找到认证token，请先登录'))
    }

    // 如果没有指定服务器地址，从配置中获取
    if (!serverUrl) {
      const baseUrl = apiConfig.baseURL.replace('http://', '').replace('https://', '')
      // 使用原生WebSocket服务器端口8003（app后端）
      const host = baseUrl.split(':')[0]
      serverUrl = `ws://${host}:8003`
    }

    return new Promise((resolve, reject) => {
      try {
        // uni-app中的WebSocket连接
        // 注意：uni-app的WebSocket API不支持直接设置请求头
        // 我们通过URL参数传递token，后端会从查询参数中获取
        this.socket = uni.connectSocket({
          url: `${serverUrl}?authorization=${encodeURIComponent(`Bearer ${token}`)}`,
          success: () => {
            console.log('WebSocket连接请求已发送')
          },
          fail: (error) => {
            console.error('WebSocket连接请求失败:', error)
            reject(error)
          }
        })

        // 连接成功
        this.socket.onOpen(() => {
          console.log('WebSocket connected')
          this.isConnected = true
          this.reconnectAttempts = 0
          resolve()
        })

        // 连接关闭
        this.socket.onClose((event) => {
          console.log('WebSocket disconnected:', event)
          this.isConnected = false
          
          // 如果是认证失败导致的关闭，不进行重连
          if (event.code === 1008 || event.code === 1002 || event.code === 1006) {
            console.error('WebSocket连接因认证失败而关闭')
            this.emit('auth_error', { message: '认证失败，请重新登录' })
            return
          }
          
          this.handleReconnect()
        })

        // 连接错误
        this.socket.onError((error) => {
          console.error('WebSocket connection error:', error)
          this.isConnected = false
          reject(error)
        })

        // 监听消息
        this.socket.onMessage((message) => {
          try {
            const data = JSON.parse(message.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        })

      } catch (error) {
        console.error('WebSocket connection error:', error)
        reject(error)
      }
    })
  }

  // 处理接收到的消息
  handleMessage(data) {
    console.log('WebSocket message received:', data)
    
    switch (data.type) {
      case 'user_joined':
        this.emit('user_joined', data.data)
        break
      case 'merchant_joined':
        this.emit('merchant_joined', data.data)
        break
      case 'joined_chat_room':
        this.chatRoomId = data.data.chat_room_id
        this.emit('joined_chat_room', data.data)
        break
      case 'new_message':
        this.emit('new_message', data.data)
        break
      case 'message_marked_read':
        this.emit('message_marked_read', data.data)
        break
      case 'chat_history':
        this.emit('chat_history', data.data)
        break
      case 'online_status':
        this.emit('online_status', data.data)
        break
      case 'error':
        console.error('WebSocket error:', data.data)
        this.emit('error', data.data)
        break
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  // 处理重连
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`尝试重连WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('重连失败:', error)
        })
      }, this.reconnectInterval)
    } else {
      console.error('WebSocket重连次数已达上限')
      this.emit('reconnect_failed', null)
    }
  }

  // 发送消息到服务器
  sendMessage(type, data) {
    if (!this.isConnected || !this.socket) {
      throw new Error('WebSocket not connected')
    }

    const message = {
      type: type,
      data: data,
      timestamp: Date.now()
    }

    this.socket.send({
      data: JSON.stringify(message),
      success: () => {
        console.log('Message sent successfully:', type)
      },
      fail: (error) => {
        console.error('Failed to send message:', error)
        throw error
      }
    })
  }

  // 用户加入聊天
  joinAsUser(userId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.userId = userId
    this.sendMessage('user_join', { user_id: userId })
  }

  // 商家加入聊天
  joinAsMerchant(merchantId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.merchantId = merchantId
    this.sendMessage('merchant_join', { merchant_id: merchantId })
  }

  // 加入聊天室
  joinChatRoom(userId, merchantId) {
    if (!this.isConnected) {
      throw new Error('WebSocket not connected')
    }
    
    this.sendMessage('join_chat_room', { 
      user_id: userId, 
      merchant_id: merchantId 
    })
  }

  // 发送消息
  sendChatMessage(content, messageType = 'text', fileUrl = null) {
    if (!this.isConnected || !this.chatRoomId) {
      throw new Error('Not connected to chat room')
    }

    const senderType = this.userId ? 'user' : 'merchant'
    const senderId = this.userId || this.merchantId

    this.sendMessage('send_message', {
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
    
    this.sendMessage('mark_message_read', { message_id: messageId })
  }

  // 获取聊天历史
  getChatHistory(page = 1, perPage = 20) {
    if (!this.isConnected || !this.chatRoomId) {
      throw new Error('Not connected to chat room')
    }
    
    this.sendMessage('get_chat_history', {
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
    
    this.sendMessage('get_online_status', {
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
      this.socket.close({
        success: () => {
          console.log('WebSocket disconnected successfully')
        },
        fail: (error) => {
          console.error('Error disconnecting WebSocket:', error)
        }
      })
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
