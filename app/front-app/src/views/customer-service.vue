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

		<!-- 客服介绍 -->
		<view class="cs-intro">
			<view class="intro-content">
				<text class="intro-title">欢迎使用音加加客服</text>
				<text class="intro-desc">我们为您提供7x24小时在线服务，有任何问题都可以随时咨询</text>
			</view>
		</view>

		<!-- 快捷功能 -->
		<view class="quick-actions">
			<view class="action-item" @click="startChat">
				<uni-icons type="chat" size="24" color="#007bff"></uni-icons>
				<text class="action-text">开始对话</text>
			</view>
			<view class="action-item" @click="viewFAQ">
				<uni-icons type="help" size="24" color="#28a745"></uni-icons>
				<text class="action-text">常见问题</text>
			</view>
			<view class="action-item" @click="contactPhone">
				<uni-icons type="phone" size="24" color="#ffc107"></uni-icons>
				<text class="action-text">电话咨询</text>
			</view>
		</view>

		<!-- 服务时间 -->
		<view class="service-time">
			<text class="time-title">服务时间</text>
			<text class="time-desc">周一至周日 9:00-21:00</text>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				merchantId: 1 // 默认商家ID，实际应该从商品或配置中获取
			}
		},
		methods: {
			goBack() {
				uni.navigateBack()
			},
			startChat() {
				// 跳转到聊天页面
				uni.navigateTo({
					url: `/pages/chat/chat?merchantId=${this.merchantId}`
				})
			},
			viewFAQ() {
				uni.showToast({
					title: '常见问题功能开发中',
					icon: 'none'
				})
			},
			contactPhone() {
				uni.makePhoneCall({
					phoneNumber: '400-123-4567'
				})
			}
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

	.cs-intro {
		padding: 20px;
		background-color: #fff;
		margin: 10px;
		border-radius: 8px;
	}

	.intro-content {
		text-align: center;
	}

	.intro-title {
		display: block;
		font-size: 18px;
		font-weight: bold;
		color: #333;
		margin-bottom: 10px;
	}

	.intro-desc {
		display: block;
		font-size: 14px;
		color: #666;
		line-height: 1.5;
	}

	.quick-actions {
		display: flex;
		justify-content: space-around;
		padding: 20px;
		background-color: #fff;
		margin: 0 10px 10px;
		border-radius: 8px;
	}

	.action-item {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 15px;
		border-radius: 8px;
		background-color: #f8f9fa;
		min-width: 80px;
	}

	.action-text {
		font-size: 12px;
		color: #333;
		margin-top: 8px;
	}

	.service-time {
		padding: 15px 20px;
		background-color: #fff;
		margin: 0 10px;
		border-radius: 8px;
		text-align: center;
	}

	.time-title {
		display: block;
		font-size: 14px;
		font-weight: bold;
		color: #333;
		margin-bottom: 5px;
	}

	.time-desc {
		display: block;
		font-size: 12px;
		color: #666;
	}
</style>