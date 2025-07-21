<template>
	<view class="result-container">
		<uni-nav-bar title="支付结果" left-icon="back" @clickLeft="goBack"></uni-nav-bar>

		<view class="result-content">
			<image class="result-icon" :src="resultIcon"></image>
			<text class="result-title">{{ resultTitle }}</text>
			<text class="result-desc">{{ resultDesc }}</text>

			<view class="order-info">
				<view class="info-item">
					<text class="label">订单编号：</text>
					<text class="value">{{ orderInfo.orderNo }}</text>
				</view>
				<view class="info-item">
					<text class="label">支付金额：</text>
					<text class="value price">¥{{ orderInfo.amount }}</text>
				</view>
				<view class="info-item">
					<text class="label">支付方式：</text>
					<text class="value">{{ orderInfo.paymentMethod }}</text>
				</view>
				<view class="info-item">
					<text class="label">支付时间：</text>
					<text class="value">{{ orderInfo.paymentTime }}</text>
				</view>
			</view>
		</view>

		<view class="action-btns">
			<button class="btn" @click="goToHome">返回首页</button>
			<button class="btn primary" @click="viewOrder">查看订单</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				status: 'success', // success/fail
				orderInfo: {
					orderNo: '',
					amount: '0.00',
					paymentMethod: '微信支付',
					paymentTime: ''
				}
			}
		},
		computed: {
			resultIcon() {
				return this.status === 'success' ?
					'/static/images/payment/success.png' :
					'/static/images/payment/fail.png';
			},
			resultTitle() {
				return this.status === 'success' ? '支付成功' : '支付失败';
			},
			resultDesc() {
				return this.status === 'success' ?
					'您的订单已支付成功，我们将尽快为您发货' :
					'支付过程中出现问题，请重新尝试或选择其他支付方式';
			}
		},
		onLoad(options) {
			this.status = options.status || 'success';
			this.orderInfo.orderNo = options.orderNo || 'JD20230701123456';
			this.orderInfo.amount = options.amount || '0.00';
			this.orderInfo.paymentTime = this.formatDate(new Date());
		},
		methods: {
			formatDate(date) {
				const year = date.getFullYear();
				const month = (date.getMonth() + 1).toString().padStart(2, '0');
				const day = date.getDate().toString().padStart(2, '0');
				const hours = date.getHours().toString().padStart(2, '0');
				const minutes = date.getMinutes().toString().padStart(2, '0');
				const seconds = date.getSeconds().toString().padStart(2, '0');

				return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
			},

			goBack() {
				uni.navigateBack();
			},

			goToHome() {
				uni.switchTab({
					url: '/pages/tabbar/index/index'
				});
			},

			viewOrder() {
				uni.navigateTo({
					url: `/pages/trade-list/myorder?orderNo=${this.orderInfo.orderNo}`
				});
			}
		}
	}
</script>

<style scoped>
	.result-container {
		background-color: #f5f5f5;
		min-height: 100vh;
	}

	.result-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 30px 15px;
		background-color: #fff;
		margin-bottom: 10px;
	}

	.result-icon {
		width: 80px;
		height: 80px;
		margin-bottom: 20px;
	}

	.result-title {
		font-size: 20px;
		font-weight: bold;
		margin-bottom: 10px;
		color: #333;
	}

	.result-desc {
		font-size: 14px;
		color: #999;
		margin-bottom: 30px;
		text-align: center;
	}

	.order-info {
		width: 100%;
		border-top: 1px solid #f5f5f5;
		padding-top: 15px;
	}

	.info-item {
		display: flex;
		margin-bottom: 10px;
		font-size: 14px;
	}

	.label {
		color: #999;
		width: 80px;
	}

	.value {
		flex: 1;
		color: #333;
	}

	.price {
		color: #ff2442;
		font-weight: bold;
	}

	.action-btns {
		display: flex;
		padding: 15px;
		background-color: #fff;
	}

	.btn {
		flex: 1;
		height: 44px;
		line-height: 44px;
		border: 1px solid #ddd;
		border-radius: 22px;
		font-size: 16px;
		color: #333;
		background-color: #fff;
		margin: 0 5px;
	}

	.btn.primary {
		background-color: #ff2442;
		color: #fff;
		border-color: #ff2442;
	}
</style>