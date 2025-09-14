<template>
	<view class="customer-service-container">
		<!-- 客服头部 -->
		<view class="cs-header">
			<view class="cs-info">
				<image class="cs-avatar"
					src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
				</image>
				<view class="cs-meta">
					<text class="cs-name">音加加客服</text>
					<text class="cs-status" :class="{ online: isOnline }">{{ isOnline ? '在线' : '离线' }}</text>
				</view>
			</view>
			<view class="header-actions">
				<uni-icons type="chat" size="24" color="#07c160" @click="startChat"></uni-icons>
				<uni-icons type="close" size="24" color="#999" @click="goBack"></uni-icons>
			</view>
		</view>

		<!-- 连接状态提示 -->
		<view class="connection-status" v-if="!isConnected">
			<text class="status-text">正在连接客服...</text>
		</view>

		<!-- 聊天区域 -->
		<scroll-view class="chat-area" scroll-y :scroll-into-view="scrollToView">
			<view class="chat-date" v-if="messages.length > 0">今天 {{ getCurrentTime() }}</view>

			<!-- 消息列表 -->
			<view 
				v-for="(message, index) in messages" 
				:key="index"
				:id="'msg-' + index"
				class="chat-message"
				:class="message.type === 'user' ? 'user-message' : 'cs-message'"
			>
				<!-- 客服消息 -->
				<template v-if="message.type === 'cs'">
					<image class="avatar"
						src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
					</image>
					<view class="message-content">
						<text class="message-text">{{ message.text }}</text>
						<text class="message-time">{{ message.time }}</text>
					</view>
				</template>

				<!-- 用户消息 -->
				<template v-else>
					<view class="message-content">
						<text class="message-text">{{ message.text }}</text>
						<text class="message-time">{{ message.time }}</text>
					</view>
					<image class="avatar"
						src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
					</image>
				</template>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-if="messages.length === 0">
				<text class="empty-text">开始与客服对话</text>
			</view>
		</scroll-view>

		<!-- 输入区域 -->
		<view class="input-area">
			<view class="input-box">
				<input 
					class="message-input" 
					type="text" 
					v-model="message" 
					placeholder="请输入消息内容"
					:disabled="!isConnected"
					@confirm="sendMessage" 
				/>
				<view class="emoji-btn" @click="toggleEmoji">
					<uni-icons type="happy" size="24" color="#666"></uni-icons>
				</view>
			</view>
			<view class="send-btn" @click="sendMessage" :class="{ disabled: !canSend }">发送</view>
		</view>

		<!-- 表情面板 -->
		<view class="emoji-panel" v-show="showEmoji">
			<!-- 这里可以添加表情选择器 -->
		</view>

		<!-- 快捷操作按钮 -->
		<view class="quick-actions">
			<view class="action-item" @click="startChat">
				<uni-icons type="chat" size="20" color="#07c160"></uni-icons>
				<text class="action-text">开始聊天</text>
			</view>
			<view class="action-item" @click="callService">
				<uni-icons type="phone" size="20" color="#07c160"></uni-icons>
				<text class="action-text">电话客服</text>
			</view>
			<view class="action-item" @click="viewFAQ">
				<uni-icons type="help" size="20" color="#07c160"></uni-icons>
				<text class="action-text">常见问题</text>
			</view>
		</view>
	</view>
</template>

<script>
	import websocketService from '@/src/services/websocketService.js'
	
	export default {
		data() {
			return {
				// WebSocket连接状态
				isConnected: false,
				isOnline: false,
				
				// 聊天相关
				message: '',
				showEmoji: false,
				scrollToView: '',
				messages: [],
				chatRoomId: null,
				
				// 用户信息
				userInfo: {
					id: null,
					name: '',
					avatar: null
				}
			}
		},
		
		computed: {
			canSend() {
				return this.isConnected && this.message.trim().length > 0
			}
		},
		
		onLoad() {
			this.initCustomerService()
		},
		
		onUnload() {
			this.disconnectWebSocket()
		},
		
		onShow() {
			if (!this.isConnected) {
				this.connectWebSocket()
			}
		},
		
		onHide() {
			this.disconnectWebSocket()
		},
		
		methods: {
			// 初始化客服页面
			async initCustomerService() {
				try {
					// 获取用户信息
					await this.getUserInfo()
					
					// 连接WebSocket
					await this.connectWebSocket()
					
					// 添加欢迎消息
					this.addWelcomeMessage()
					
				} catch (error) {
					console.error('初始化客服页面失败:', error)
				}
			},
			
			// 获取用户信息
			async getUserInfo() {
				try {
					const userInfo = uni.getStorageSync('userInfo')
					if (userInfo) {
						this.userInfo = userInfo
					} else {
						// 使用默认用户信息
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
					
					// 设置事件监听
					this.setupWebSocketListeners()
					
					console.log('WebSocket连接成功')
				} catch (error) {
					console.error('WebSocket连接失败:', error)
					this.isConnected = false
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
				websocketService.on('online_status', this.handleOnlineStatus)
				websocketService.on('error', this.handleError)
				websocketService.on('auth_error', this.handleAuthError)
			},
			
			// 移除WebSocket事件监听
			removeWebSocketListeners() {
				websocketService.off('joined_chat_room', this.handleJoinedChatRoom)
				websocketService.off('new_message', this.handleNewMessage)
				websocketService.off('online_status', this.handleOnlineStatus)
				websocketService.off('error', this.handleError)
				websocketService.off('auth_error', this.handleAuthError)
			},
			
			// 添加欢迎消息
			addWelcomeMessage() {
				this.messages = [{
					type: 'cs',
					text: '您好，音加加客服为您服务，请问有什么可以帮您？',
					time: this.getCurrentTime()
				}]
			},
			
			// 开始聊天
			startChat() {
				if (this.isConnected && this.userInfo.id) {
					// 加入聊天室
					websocketService.joinChatRoom(this.userInfo.id, 1) // 默认商家ID为1
				} else {
					// 跳转到专门的聊天页面
					uni.navigateTo({
						url: '/pages/chat/chat?merchantId=1'
					})
				}
			},
			
			// 发送消息
			sendMessage() {
				if (!this.canSend) return
				
				const messageText = this.message.trim()
				if (!messageText) return
				
				// 添加到消息列表
				this.messages.push({
					type: 'user',
					text: messageText,
					time: this.getCurrentTime()
				})
				
				// 发送到服务器
				if (this.isConnected && this.chatRoomId) {
					try {
						websocketService.sendChatMessage(messageText)
					} catch (error) {
						console.error('发送消息失败:', error)
					}
				} else {
					// 模拟客服回复
					setTimeout(() => {
						this.messages.push({
							type: 'cs',
							text: '您的消息已收到，客服人员会尽快回复您。',
							time: this.getCurrentTime()
						})
						this.scrollToBottom()
					}, 1000)
				}
				
				this.message = ''
				this.scrollToBottom()
			},
			
			// 电话客服
			callService() {
				uni.showModal({
					title: '电话客服',
					content: '客服电话：400-123-4567',
					confirmText: '拨打',
					cancelText: '取消',
					success: (res) => {
						if (res.confirm) {
							// 拨打客服电话
							uni.makePhoneCall({
								phoneNumber: '400-123-4567'
							})
						}
					}
				})
			},
			
			// 查看常见问题
			viewFAQ() {
				uni.showToast({
					title: '常见问题功能开发中',
					icon: 'none'
				})
			},
			
			// 返回
			goBack() {
				uni.navigateBack()
			},
			
			// 切换表情
			toggleEmoji() {
				this.showEmoji = !this.showEmoji
			},
			
			// 滚动到底部
			scrollToBottom() {
				this.$nextTick(() => {
					if (this.messages.length > 0) {
						const lastIndex = this.messages.length - 1
						this.scrollToView = `msg-${lastIndex}`
					}
				})
			},
			
			// 获取当前时间
			getCurrentTime() {
				const now = new Date()
				return `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`
			},
			
			// WebSocket事件处理函数
			handleJoinedChatRoom(data) {
				console.log('加入聊天室成功:', data)
				this.chatRoomId = data.chat_room_id
			},
			
			handleNewMessage(data) {
				console.log('收到新消息:', data)
				this.messages.push({
					type: data.sender_type === 'user' ? 'user' : 'cs',
					text: data.content,
					time: this.getCurrentTime()
				})
				
				this.scrollToBottom()
			},
			
			handleOnlineStatus(data) {
				console.log('在线状态更新:', data)
				this.isOnline = data.is_online
			},
			
			handleError(error) {
				console.error('WebSocket错误:', error)
				uni.showToast({
					title: '连接出现问题',
					icon: 'error'
				})
			},
			
			handleAuthError(error) {
				console.error('WebSocket认证失败:', error)
				this.isConnected = false
				uni.showModal({
					title: '认证失败',
					content: error.message || '认证失败，请重新登录',
					showCancel: false,
					confirmText: '重新登录',
					success: (res) => {
						if (res.confirm) {
							// 跳转到登录页面
							uni.navigateTo({
								url: '/pages/login/login'
							})
						}
					}
				})
			}
		},
		
		onReady() {
			this.scrollToBottom()
		}
	}
</script>

<style scoped>
	.customer-service-container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #f5f5f5;
	}

	.cs-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px;
		background-color: #fff;
		border-bottom: 1px solid #eee;
	}

	.cs-info {
		display: flex;
		align-items: center;
	}

	.cs-avatar {
		width: 40px;
		height: 40px;
		border-radius: 20px;
		margin-right: 10px;
	}

	.cs-meta {
		display: flex;
		flex-direction: column;
	}

	.cs-name {
		font-size: 16px;
		font-weight: bold;
	}

	.cs-status {
		font-size: 12px;
		color: #999;
	}

	.cs-status.online {
		color: #07c160;
	}

	.header-actions {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.connection-status {
		padding: 10px 15px;
		background-color: #fff3cd;
		text-align: center;
	}

	.status-text {
		font-size: 14px;
		color: #856404;
	}

	.chat-area {
		flex: 1;
		padding: 15px;
		overflow: auto;
	}

	.chat-date {
		text-align: center;
		font-size: 12px;
		color: #999;
		margin: 10px 0;
	}

	.chat-message {
		display: flex;
		margin-bottom: 15px;
	}

	.avatar {
		width: 36px;
		height: 36px;
		border-radius: 18px;
	}

	.message-content {
		max-width: 70%;
		margin: 0 10px;
	}

	.message-text {
		padding: 10px;
		font-size: 14px;
		line-height: 1.4;
		border-radius: 5px;
		display: inline-block;
	}

	.message-time {
		display: block;
		font-size: 10px;
		color: #999;
		margin-top: 5px;
		text-align: right;
	}

	.cs-message {
		justify-content: flex-start;
	}

	.cs-message .message-text {
		background-color: #fff;
		color: #333;
	}

	.user-message {
		justify-content: flex-end;
	}

	.user-message .message-text {
		background-color: #07c160;
		color: #fff;
	}

	.input-area {
		display: flex;
		align-items: center;
		padding: 10px;
		background-color: #fff;
		border-top: 1px solid #eee;
	}

	.input-box {
		flex: 1;
		display: flex;
		align-items: center;
		background-color: #f5f5f5;
		border-radius: 18px;
		padding: 5px 10px;
		margin-right: 10px;
	}

	.message-input {
		flex: 1;
		height: 36px;
		font-size: 14px;
	}

	.emoji-btn {
		width: 30px;
		height: 30px;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.send-btn {
		font-size: 14px;
		color: #07c160;
		font-weight: bold;
	}

	.send-btn.disabled {
		color: #ccc;
	}

	.emoji-panel {
		height: 200px;
		background-color: #fff;
		border-top: 1px solid #eee;
		padding: 10px;
	}

	.empty-state {
		text-align: center;
		padding: 50px 20px;
	}

	.empty-text {
		font-size: 14px;
		color: #999;
	}

	.quick-actions {
		display: flex;
		justify-content: space-around;
		padding: 15px;
		background-color: #fff;
		border-top: 1px solid #eee;
	}

	.action-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 5px;
		padding: 10px;
		border-radius: 8px;
		background-color: #f8f9fa;
		min-width: 80px;
	}

	.action-text {
		font-size: 12px;
		color: #07c160;
	}
</style>