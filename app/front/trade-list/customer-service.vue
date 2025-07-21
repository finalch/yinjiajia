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
					<text class="cs-status">在线</text>
				</view>
			</view>
			<uni-icons type="close" size="24" color="#999" @click="goBack"></uni-icons>
		</view>

		<!-- 聊天区域 -->
		<scroll-view class="chat-area" scroll-y :scroll-into-view="scrollToView">
			<view class="chat-date">今天 10:30</view>

			<!-- 客服消息 -->
			<view class="chat-message cs-message">
				<image class="avatar"
					src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
				</image>
				<view class="message-content">
					<text class="message-text">您好，音加加客服为您服务，请问有什么可以帮您？</text>
					<text class="message-time">10:30</text>
				</view>
			</view>

			<!-- 用户消息 -->
			<view class="chat-message user-message">
				<view class="message-content">
					<text class="message-text">我买的iPhone 13什么时候能发货？</text>
					<text class="message-time">10:32</text>
				</view>
				<image class="avatar"
					src="https://img10.360buyimg.com/img/s80x80_jfs/t1/123456/32/12345/67890/5f6789abE12345678/abcdef123456.jpg">
				</image>
			</view>

			<!-- 更多消息... -->
		</scroll-view>

		<!-- 输入区域 -->
		<view class="input-area">
			<view class="input-box">
				<input class="message-input" type="text" v-model="message" placeholder="请输入消息内容"
					@confirm="sendMessage" />
				<view class="emoji-btn" @click="toggleEmoji">
					<uni-icons type="happy" size="24" color="#666"></uni-icons>
				</view>
			</view>
			<view class="send-btn" @click="sendMessage">发送</view>
		</view>

		<!-- 表情面板 -->
		<view class="emoji-panel" v-show="showEmoji">
			<!-- 这里可以添加表情选择器 -->
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				message: '',
				showEmoji: false,
				scrollToView: '',
				messages: [{
						type: 'cs',
						text: '您好，音加加客服为您服务，请问有什么可以帮您？',
						time: '10:30'
					},
					{
						type: 'user',
						text: '我买的iPhone 13什么时候能发货？',
						time: '10:32'
					}
					// 更多消息...
				]
			}
		},
		methods: {
			goBack() {
				uni.navigateBack()
			},
			sendMessage() {
				if (!this.message.trim()) return

				// 添加到消息列表
				this.messages.push({
					type: 'user',
					text: this.message,
					time: this.getCurrentTime()
				})

				// 模拟客服回复
				setTimeout(() => {
					this.messages.push({
						type: 'cs',
						text: '您的订单将在24小时内发货，请耐心等待。',
						time: this.getCurrentTime()
					})
					this.scrollToBottom()
				}, 1000)

				this.message = ''
				this.scrollToBottom()
			},
			toggleEmoji() {
				this.showEmoji = !this.showEmoji
			},
			scrollToBottom() {
				this.scrollToView = 'msg-' + (this.messages.length - 1)
			},
			getCurrentTime() {
				const now = new Date()
				return `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`
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
		color: #07c160;
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

	.emoji-panel {
		height: 200px;
		background-color: #fff;
		border-top: 1px solid #eee;
		padding: 10px;
	}
</style>