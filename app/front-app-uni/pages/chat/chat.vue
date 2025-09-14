<template>
	<view class="chat-container">
		<!-- 聊天头部 -->
		<view class="chat-header">
			<view class="header-info">
				<image class="avatar" :src="merchantInfo.avatar || defaultAvatar"></image>
				<view class="info">
					<text class="name">{{ merchantInfo.name || '音加加客服' }}</text>
					<text class="status" :class="{ online: isOnline }">
						{{ isOnline ? '在线' : '离线' }}
					</text>
				</view>
			</view>
			<view class="header-actions">
				<uni-icons type="close" size="24" color="#666" @click="goBack"></uni-icons>
			</view>
		</view>

		<!-- 连接状态提示 -->
		<view class="connection-status" v-if="!isConnected">
			<text class="status-text">连接中...</text>
		</view>

		<!-- 聊天消息区域 -->
		<scroll-view 
			class="chat-messages" 
			scroll-y 
			:scroll-into-view="scrollToView"
			:scroll-with-animation="true"
		>
			<view class="messages-container">
				<!-- 日期分隔线 -->
				<view class="date-divider" v-if="currentDate">
					<text class="date-text">{{ currentDate }}</text>
				</view>

				<!-- 消息列表 -->
				<view 
					v-for="(message, index) in messages" 
					:key="message.id || index"
					:id="'msg-' + index"
					class="message-item"
					:class="message.sender_type === 'user' ? 'user-message' : 'merchant-message'"
				>
					<!-- 客服头像 -->
					<image 
						v-if="message.sender_type === 'merchant'"
						class="message-avatar" 
						:src="merchantInfo.avatar || defaultAvatar"
					></image>

					<view class="message-content">
						<view class="message-bubble" :class="message.sender_type === 'user' ? 'user-bubble' : 'merchant-bubble'">
							<text class="message-text">{{ message.content }}</text>
						</view>
						<text class="message-time">{{ formatTime(message.created_at) }}</text>
					</view>

					<!-- 用户头像 -->
					<image 
						v-if="message.sender_type === 'user'"
						class="message-avatar" 
						:src="userInfo.avatar || defaultAvatar"
					></image>
				</view>

				<!-- 加载更多 -->
				<view class="load-more" v-if="hasMoreMessages && !loading">
					<text class="load-more-text" @click="loadMoreMessages">加载更多消息</text>
				</view>

				<!-- 加载中 -->
				<view class="loading" v-if="loading">
					<text class="loading-text">加载中...</text>
				</view>
			</view>
		</scroll-view>

		<!-- 输入区域 -->
		<view class="input-area">
			<view class="input-container">
				<input 
					class="message-input" 
					type="text" 
					v-model="inputMessage" 
					placeholder="请输入消息内容"
					:disabled="!isConnected"
					@confirm="sendMessage"
					@input="onInputChange"
				/>
				<view class="send-button" @click="sendMessage" :class="{ disabled: !canSend }">
					<text class="send-text">发送</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import websocketService from '@/services/websocketService.js'
import { authApi } from '@/utils/api.js'

export default {
	data() {
		return {
			// WebSocket连接状态
			isConnected: false,
			isOnline: false,
			
			// 用户信息
			userInfo: {
				id: null,
				avatar: null,
				name: ''
			},
			
			// 商家信息
			merchantInfo: {
				id: 1, // 默认商家ID
				avatar: null,
				name: '音加加客服'
			},
			
			// 聊天相关
			chatRoomId: null,
			messages: [],
			inputMessage: '',
			scrollToView: '',
			loading: false,
			hasMoreMessages: true,
			currentPage: 1,
			
			// 默认头像
			defaultAvatar: 'https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg'
		}
	},
	
	computed: {
		canSend() {
			return this.isConnected && this.inputMessage.trim().length > 0
		},
		
		currentDate() {
			if (this.messages.length === 0) return null
			const today = new Date()
			const todayStr = today.toLocaleDateString()
			return todayStr
		}
	},
	
	onLoad(options) {
		// 获取传递的参数
		if (options.merchantId) {
			this.merchantInfo.id = parseInt(options.merchantId)
		}
		
		this.initChat()
	},
	
	onUnload() {
		// 页面卸载时断开WebSocket连接
		this.disconnectWebSocket()
	},
	
	onShow() {
		// 页面显示时重新连接
		if (!this.isConnected) {
			this.connectWebSocket()
		}
	},
	
	onHide() {
		// 页面隐藏时断开连接
		this.disconnectWebSocket()
	},
	
	methods: {
		// 初始化聊天
		async initChat() {
			try {
				// 获取用户信息
				await this.getUserInfo()
				
				// 连接WebSocket
				await this.connectWebSocket()
				
				// 加入聊天室
				this.joinChatRoom()
				
			} catch (error) {
				console.error('初始化聊天失败:', error)
				uni.showToast({
					title: '初始化失败',
					icon: 'error'
				})
			}
		},
		
		// 获取用户信息
		async getUserInfo() {
			try {
				// 从本地存储获取用户信息
				const userInfo = uni.getStorageSync('userInfo')
				if (userInfo) {
					this.userInfo = userInfo
				} else {
					// 如果没有用户信息，使用默认值
					this.userInfo = {
						id: 1,
						name: '用户',
						avatar: null
					}
				}
			} catch (error) {
				console.error('获取用户信息失败:', error)
			}
		},
		
		// 连接WebSocket
		async connectWebSocket() {
			try {
				await websocketService.connect()
				this.isConnected = true
				
				// 监听WebSocket事件
				this.setupWebSocketListeners()
				
				console.log('WebSocket连接成功')
			} catch (error) {
				console.error('WebSocket连接失败:', error)
				this.isConnected = false
				
				uni.showToast({
					title: '连接失败，请重试',
					icon: 'error'
				})
			}
		},
		
		// 断开WebSocket连接
		disconnectWebSocket() {
			websocketService.disconnect()
			this.isConnected = false
			this.removeWebSocketListeners()
		},
		
		// 设置WebSocket事件监听
		setupWebSocketListeners() {
			websocketService.on('joined_chat_room', this.handleJoinedChatRoom)
			websocketService.on('new_message', this.handleNewMessage)
			websocketService.on('chat_history', this.handleChatHistory)
			websocketService.on('online_status', this.handleOnlineStatus)
			websocketService.on('error', this.handleError)
			websocketService.on('reconnect_failed', this.handleReconnectFailed)
		},
		
		// 移除WebSocket事件监听
		removeWebSocketListeners() {
			websocketService.off('joined_chat_room', this.handleJoinedChatRoom)
			websocketService.off('new_message', this.handleNewMessage)
			websocketService.off('chat_history', this.handleChatHistory)
			websocketService.off('online_status', this.handleOnlineStatus)
			websocketService.off('error', this.handleError)
			websocketService.off('reconnect_failed', this.handleReconnectFailed)
		},
		
		// 加入聊天室
		joinChatRoom() {
			if (this.isConnected && this.userInfo.id) {
				websocketService.joinChatRoom(this.userInfo.id, this.merchantInfo.id)
			}
		},
		
		// 发送消息
		sendMessage() {
			if (!this.canSend) return
			
			const message = this.inputMessage.trim()
			if (!message) return
			
			try {
				// 发送消息到服务器
				websocketService.sendChatMessage(message)
				
				// 清空输入框
				this.inputMessage = ''
				
				// 滚动到底部
				this.$nextTick(() => {
					this.scrollToBottom()
				})
				
			} catch (error) {
				console.error('发送消息失败:', error)
				uni.showToast({
					title: '发送失败',
					icon: 'error'
				})
			}
		},
		
		// 输入框内容变化
		onInputChange(e) {
			this.inputMessage = e.detail.value
		},
		
		// 加载更多消息
		loadMoreMessages() {
			if (this.loading || !this.hasMoreMessages) return
			
			this.loading = true
			this.currentPage++
			
			// 获取聊天历史
			websocketService.getChatHistory(this.currentPage, 20)
		},
		
		// 滚动到底部
		scrollToBottom() {
			if (this.messages.length > 0) {
				const lastIndex = this.messages.length - 1
				this.scrollToView = `msg-${lastIndex}`
			}
		},
		
		// 格式化时间
		formatTime(timestamp) {
			if (!timestamp) return ''
			
			const date = new Date(timestamp)
			const now = new Date()
			const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
			const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate())
			
			if (messageDate.getTime() === today.getTime()) {
				// 今天
				return date.toLocaleTimeString('zh-CN', { 
					hour: '2-digit', 
					minute: '2-digit' 
				})
			} else {
				// 其他日期
				return date.toLocaleString('zh-CN', {
					month: '2-digit',
					day: '2-digit',
					hour: '2-digit',
					minute: '2-digit'
				})
			}
		},
		
		// 返回上一页
		goBack() {
			uni.navigateBack()
		},
		
		// WebSocket事件处理函数
		handleJoinedChatRoom(data) {
			console.log('加入聊天室成功:', data)
			this.chatRoomId = data.chat_room_id
			
			// 获取聊天历史
			this.loading = true
			websocketService.getChatHistory(1, 20)
		},
		
		handleNewMessage(data) {
			console.log('收到新消息:', data)
			this.messages.push(data)
			
			// 滚动到底部
			this.$nextTick(() => {
				this.scrollToBottom()
			})
		},
		
		handleChatHistory(data) {
			console.log('收到聊天历史:', data)
			this.loading = false
			
			if (data.messages && data.messages.length > 0) {
				if (this.currentPage === 1) {
					// 第一页，替换消息列表
					this.messages = data.messages.reverse()
				} else {
					// 后续页，添加到列表前面
					this.messages = [...data.messages.reverse(), ...this.messages]
				}
				
				// 检查是否还有更多消息
				this.hasMoreMessages = data.messages.length === 20
			} else {
				this.hasMoreMessages = false
			}
			
			// 如果是第一页，滚动到底部
			if (this.currentPage === 1) {
				this.$nextTick(() => {
					this.scrollToBottom()
				})
			}
		},
		
		handleOnlineStatus(data) {
			console.log('在线状态更新:', data)
			this.isOnline = data.is_online
		},
		
		handleError(error) {
			console.error('WebSocket错误:', error)
			uni.showToast({
				title: error.message || '发生错误',
				icon: 'error'
			})
		},
		
		handleReconnectFailed() {
			console.error('WebSocket重连失败')
			uni.showToast({
				title: '连接已断开',
				icon: 'error'
			})
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
	padding: 15px;
	background-color: #fff;
	border-bottom: 1px solid #eee;
}

.header-info {
	display: flex;
	align-items: center;
}

.avatar {
	width: 40px;
	height: 40px;
	border-radius: 20px;
	margin-right: 12px;
}

.info {
	display: flex;
	flex-direction: column;
}

.name {
	font-size: 16px;
	font-weight: bold;
	color: #333;
}

.status {
	font-size: 12px;
	color: #999;
}

.status.online {
	color: #07c160;
}

.header-actions {
	display: flex;
	align-items: center;
}

.connection-status {
	padding: 10px;
	background-color: #fff3cd;
	text-align: center;
}

.status-text {
	font-size: 14px;
	color: #856404;
}

.chat-messages {
	flex: 1;
	padding: 0 15px;
}

.messages-container {
	padding: 15px 0;
}

.date-divider {
	text-align: center;
	margin: 20px 0;
}

.date-text {
	font-size: 12px;
	color: #999;
	background-color: #f5f5f5;
	padding: 4px 12px;
	border-radius: 12px;
}

.message-item {
	display: flex;
	margin-bottom: 15px;
	align-items: flex-start;
}

.user-message {
	justify-content: flex-end;
}

.merchant-message {
	justify-content: flex-start;
}

.message-avatar {
	width: 36px;
	height: 36px;
	border-radius: 18px;
	margin: 0 8px;
}

.message-content {
	max-width: 70%;
	display: flex;
	flex-direction: column;
}

.message-bubble {
	padding: 12px 16px;
	border-radius: 18px;
	word-wrap: break-word;
}

.user-bubble {
	background-color: #07c160;
	color: #fff;
	border-bottom-right-radius: 4px;
}

.merchant-bubble {
	background-color: #fff;
	color: #333;
	border-bottom-left-radius: 4px;
	border: 1px solid #eee;
}

.message-text {
	font-size: 14px;
	line-height: 1.4;
}

.message-time {
	font-size: 11px;
	color: #999;
	margin-top: 4px;
	text-align: right;
}

.merchant-message .message-time {
	text-align: left;
}

.load-more {
	text-align: center;
	padding: 15px;
}

.load-more-text {
	font-size: 14px;
	color: #07c160;
}

.loading {
	text-align: center;
	padding: 15px;
}

.loading-text {
	font-size: 14px;
	color: #999;
}

.input-area {
	background-color: #fff;
	border-top: 1px solid #eee;
	padding: 10px 15px;
}

.input-container {
	display: flex;
	align-items: center;
	background-color: #f5f5f5;
	border-radius: 20px;
	padding: 8px 15px;
}

.message-input {
	flex: 1;
	height: 36px;
	font-size: 14px;
	background-color: transparent;
	border: none;
	outline: none;
}

.send-button {
	margin-left: 10px;
	padding: 8px 16px;
	background-color: #07c160;
	border-radius: 16px;
}

.send-button.disabled {
	background-color: #ccc;
}

.send-text {
	font-size: 14px;
	color: #fff;
	font-weight: bold;
}

.send-button.disabled .send-text {
	color: #999;
}
</style>
