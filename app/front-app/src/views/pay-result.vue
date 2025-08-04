<template>
	<div class="pay-result-container">
		<!-- 头部 -->
		<div class="header">
			<div class="back-btn" @click="goBack">
				<span>←</span>
			</div>
			<div class="title">支付结果</div>
		</div>

		<!-- 支付结果内容 -->
		<div class="result-content">
			<!-- 成功状态 -->
			<div v-if="paymentStatus === 'success'" class="success-result">
				<div class="result-icon success">
					<span>✓</span>
				</div>
				<div class="result-title">支付成功</div>
				<div class="result-desc">您的订单已支付成功，我们会尽快为您发货</div>
				
				<div class="order-info">
					<div class="info-item">
						<span class="label">订单号：</span>
						<span class="value">{{ orderInfo.orderNo }}</span>
					</div>
					<div class="info-item">
						<span class="label">支付金额：</span>
						<span class="value price">¥{{ orderInfo.totalAmount }}</span>
					</div>
					<div class="info-item">
						<span class="label">支付时间：</span>
						<span class="value">{{ orderInfo.payTime }}</span>
					</div>
				</div>
			</div>

			<!-- 失败状态 -->
			<div v-else class="fail-result">
				<div class="result-icon fail">
					<span>✗</span>
				</div>
				<div class="result-title">支付失败</div>
				<div class="result-desc">支付过程中出现问题，请重新尝试</div>
				
				<div class="order-info">
					<div class="info-item">
						<span class="label">订单号：</span>
						<span class="value">{{ orderInfo.orderNo }}</span>
					</div>
					<div class="info-item">
						<span class="label">应付金额：</span>
						<span class="value price">¥{{ orderInfo.totalAmount }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- 操作按钮 -->
		<div class="action-buttons">
			<div v-if="paymentStatus === 'success'" class="btn-group">
				<button class="btn btn-secondary" @click="viewOrder">查看订单</button>
				<button class="btn btn-primary" @click="goHome">返回首页</button>
			</div>
			<div v-else class="btn-group">
				<button class="btn btn-secondary" @click="retryPayment">重新支付</button>
				<button class="btn btn-primary" @click="goHome">返回首页</button>
			</div>
		</div>
	</div>
</template>

<script>
	export default {
		data() {
			return {
				paymentStatus: 'success', // success 或 fail
				orderInfo: {
					orderNo: '',
					totalAmount: '0.00',
					payTime: ''
				}
			}
		},
		mounted() {
			this.loadPaymentResult();
		},
		methods: {
			// 加载支付结果
			loadPaymentResult() {
				const query = this.$route.query;
				this.paymentStatus = query.status || 'success';
				this.orderInfo.orderNo = query.order_number || '';
				this.orderInfo.totalAmount = query.total_amount || '0.00';
				this.orderInfo.payTime = this.formatDate(new Date());
			},

			// 格式化日期
			formatDate(date) {
				const year = date.getFullYear();
				const month = (date.getMonth() + 1).toString().padStart(2, '0');
				const day = date.getDate().toString().padStart(2, '0');
				const hours = date.getHours().toString().padStart(2, '0');
				const minutes = date.getMinutes().toString().padStart(2, '0');
				const seconds = date.getSeconds().toString().padStart(2, '0');

				return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
			},

			// 返回上一页
			goBack() {
				this.$router.go(-1);
			},

			// 查看订单
			viewOrder() {
				this.$router.push('/my-order');
			},

			// 重新支付
			retryPayment() {
				this.$router.push({
					path: '/payment',
					query: {
						order_number: this.orderInfo.orderNo,
						total_amount: this.orderInfo.totalAmount
					}
				});
			},

			// 返回首页
			goHome() {
				this.$router.push('/');
			}
		}
	}
</script>

<style scoped>
	.pay-result-container {
		min-height: 100vh;
		background-color: #f5f5f5;
		padding-bottom: 80px;
	}

	.header {
		background: white;
		padding: 15px 20px;
		display: flex;
		align-items: center;
		border-bottom: 1px solid #eee;
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.back-btn {
		font-size: 20px;
		cursor: pointer;
		padding: 5px;
		margin-right: 10px;
	}

	.title {
		font-size: 18px;
		font-weight: bold;
	}

	/* 结果内容样式 */
	.result-content {
		padding: 40px 20px;
		text-align: center;
	}

	.result-icon {
		width: 80px;
		height: 80px;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin: 0 auto 20px;
		font-size: 40px;
		color: white;
	}

	.result-icon.success {
		background: #07c160;
	}

	.result-icon.fail {
		background: #ff4757;
	}

	.result-title {
		font-size: 24px;
		font-weight: bold;
		margin-bottom: 10px;
		color: #333;
	}

	.result-desc {
		font-size: 14px;
		color: #666;
		margin-bottom: 30px;
		line-height: 1.5;
	}

	/* 订单信息样式 */
	.order-info {
		background: white;
		border-radius: 8px;
		padding: 20px;
		margin: 20px 0;
		text-align: left;
	}

	.info-item {
		display: flex;
		align-items: center;
		margin-bottom: 12px;
		font-size: 14px;
	}

	.info-item:last-child {
		margin-bottom: 0;
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

	/* 操作按钮样式 */
	.action-buttons {
		padding: 20px;
	}

	.btn-group {
		display: flex;
		gap: 15px;
	}

	.btn {
		flex: 1;
		padding: 15px;
		border: none;
		border-radius: 8px;
		font-size: 16px;
		font-weight: bold;
		cursor: pointer;
		transition: all 0.3s;
	}

	.btn-primary {
		background: #ff4757;
		color: white;
	}

	.btn-primary:hover {
		background: #ff3742;
	}

	.btn-secondary {
		background: #f5f5f5;
		color: #666;
		border: 1px solid #ddd;
	}

	.btn-secondary:hover {
		background: #e9e9e9;
	}
</style>