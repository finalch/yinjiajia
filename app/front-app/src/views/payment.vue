<template>
	<div class="payment-container">
		<!-- 头部 -->
		<div class="header">
			<div class="back-btn" @click="goBack">
				<span>←</span>
			</div>
			<div class="title">支付订单</div>
		</div>

		<!-- 订单信息 -->
		<div class="order-info">
			<div class="info-item">
				<span class="label">订单编号：</span>
				<span class="value">{{ orderInfo.orderNo }}</span>
				<span class="copy-btn" @click="copyOrderNo">复制</span>
			</div>
			<div class="info-item">
				<span class="label">创建时间：</span>
				<span class="value">{{ orderInfo.createTime }}</span>
			</div>
			<div class="info-item">
				<span class="label">商品名称：</span>
				<span class="value">{{ orderInfo.productName }}</span>
			</div>
			<div class="info-item">
				<span class="label">应付金额：</span>
				<span class="price">¥{{ orderInfo.totalAmount }}</span>
			</div>
		</div>

		<!-- 支付方式选择 -->
		<div class="payment-methods">
			<div class="section-title">支付方式</div>
			<div class="method-list">
				<div 
					class="method-item" 
					v-for="method in paymentMethods" 
					:key="method.value"
					:class="{ selected: method.value === currentMethod }"
					@click="selectMethod(method.value)"
				>
					<div class="method-left">
						<div class="method-icon">
							<span :class="method.icon"></span>
						</div>
						<div class="method-info">
							<div class="method-name">{{ method.name }}</div>
							<div class="method-desc">{{ method.description }}</div>
						</div>
					</div>
					<div class="method-right">
						<div class="radio-btn" :class="{ active: method.value === currentMethod }">
							<span class="radio-inner"></span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 底部支付按钮 -->
		<div class="payment-footer">
			<div class="price-info">
				<span>应付：</span>
				<span class="price">¥{{ orderInfo.totalAmount }}</span>
			</div>
			<div class="pay-btn" @click="confirmPayment">立即支付</div>
		</div>

		<!-- 支付确认弹窗 -->
		<div class="payment-modal" v-if="showPaymentModal">
			<div class="modal-content">
				<div class="modal-header">
					<h3>确认支付</h3>
				</div>
				<div class="modal-body">
					<p>订单号：{{ orderInfo.orderNo }}</p>
					<p>支付金额：¥{{ orderInfo.totalAmount }}</p>
					<p>支付方式：{{ getCurrentMethodName() }}</p>
				</div>
				<div class="modal-footer">
					<button class="cancel-btn" @click="cancelPayment">取消</button>
					<button class="confirm-btn" @click="processPayment">确认支付</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import request from '../utils/request.js'
import { getUserId } from '@/utils/auth.js'

export default {
		data() {
			return {
				orderInfo: {
					orderNo: '',
					createTime: '',
					productName: '',
					totalAmount: '0.00'
				},
				orderId: null, // 订单ID
				paymentMethods: [
					{
						name: '微信支付',
						value: 'wechat',
						description: '推荐使用微信支付',
						icon: 'wechat-icon'
					},
					{
						name: '支付宝',
						value: 'alipay',
						description: '安全便捷的支付方式',
						icon: 'alipay-icon'
					}
				],
				currentMethod: 'wechat',
				showPaymentModal: false,
				isProcessing: false
			}
		},
		mounted() {
			this.loadOrderInfo();
		},
		methods: {
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

			// 加载订单信息
			loadOrderInfo() {
				const query = this.$route.query;
				this.orderInfo.orderNo = query.order_number || '';
				this.orderInfo.totalAmount = query.total_amount || '0.00';
				this.orderInfo.createTime = this.formatDate(new Date());
				this.orderInfo.productName = '商品订单';
				this.currentMethod = query.payment_method || 'wechat';
				this.orderId = query.order_id; // 保存订单ID
			},

			// 复制订单号
			copyOrderNo() {
				if (navigator.clipboard) {
					navigator.clipboard.writeText(this.orderInfo.orderNo).then(() => {
						alert('订单号已复制');
					}).catch(() => {
						alert('复制失败');
					});
				} else {
					// 兼容旧浏览器
					const textArea = document.createElement('textarea');
					textArea.value = this.orderInfo.orderNo;
					document.body.appendChild(textArea);
					textArea.select();
					try {
						document.execCommand('copy');
						alert('订单号已复制');
					} catch (err) {
						alert('复制失败');
					}
					document.body.removeChild(textArea);
				}
			},

			// 选择支付方式
			selectMethod(methodId) {
				this.currentMethod = methodId;
			},

			// 获取当前支付方式名称
			getCurrentMethodName() {
				const method = this.paymentMethods.find(m => m.value === this.currentMethod);
				return method ? method.name : '';
			},

			// 确认支付
			confirmPayment() {
				this.showPaymentModal = true;
			},

			// 取消支付
			cancelPayment() {
				this.showPaymentModal = false;
			},

			// 处理支付
			processPayment() {
				if (this.isProcessing) return
				
				this.isProcessing = true
				this.showPaymentModal = false
				
				// 显示加载状态
				this.showLoading('正在处理支付...')
				
				// 模拟支付处理
				setTimeout(async () => {
					try {
						// 调用支付成功接口
						if (this.orderInfo.orderNo) {
              const response = await request.post(`/api/app/order/${this.orderInfo.orderNo}/pay-success`, {
                user_id: getUserId(),
								payment_method: this.currentMethod
							})
							
							if (response.data.code === 200) {
								this.hideLoading()
								this.paymentSuccess()
							} else {
								throw new Error(response.data.message || '支付失败')
							}
						} else {
							throw new Error('订单号不存在')
						}
					} catch (error) {
						console.error('支付处理失败:', error)
						this.hideLoading()
						this.paymentFail(error)
					}
				}, 2000)
			},

			// 显示加载状态
			showLoading(message) {
				// 创建加载提示
				const loading = document.createElement('div');
				loading.className = 'loading-overlay';
				loading.innerHTML = `
					<div class="loading-content">
						<div class="loading-spinner"></div>
						<div class="loading-text">${message}</div>
					</div>
				`;
				document.body.appendChild(loading);
			},

			// 隐藏加载状态
			hideLoading() {
				const loading = document.querySelector('.loading-overlay');
				if (loading) {
					document.body.removeChild(loading);
				}
			},

			// 支付成功处理
			paymentSuccess() {
				// 跳转到支付结果页面
				this.$router.push({
					path: '/pay-result',
					query: {
						status: 'success',
						order_number: this.orderInfo.orderNo,
						total_amount: this.orderInfo.totalAmount
					}
				});
			},

			// 支付失败处理
			paymentFail(err) {
				console.error('支付失败:', err);
				alert('支付失败：' + (err.message || '支付过程中出现问题'));
			}
		}
	}
</script>

<style scoped>
	.payment-container {
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

	/* 订单信息样式 */
	.order-info {
		background-color: #fff;
		padding: 20px 15px;
		margin: 10px;
		border-radius: 8px;
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
		font-size: 16px;
	}

	.copy-btn {
		color: #ff2442;
		font-size: 12px;
		border: 1px solid #ff2442;
		border-radius: 3px;
		padding: 2px 6px;
		margin-left: 10px;
		cursor: pointer;
	}

	/* 支付方式样式 */
	.payment-methods {
		background-color: #fff;
		padding: 15px;
		margin: 10px;
		border-radius: 8px;
	}

	.section-title {
		padding: 15px 0;
		font-size: 16px;
		font-weight: bold;
		border-bottom: 1px solid #f5f5f5;
	}

	.method-list {
		margin-top: 10px;
	}

	.method-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px 0;
		border-bottom: 1px solid #f0f0f0;
		cursor: pointer;
		transition: background-color 0.3s;
	}

	.method-item:last-child {
		border-bottom: none;
	}

	.method-item:hover {
		background-color: #f8f9fa;
	}

	.method-item.selected {
		background-color: #fff5f5;
	}

	.method-left {
		display: flex;
		align-items: center;
		flex: 1;
	}

	.method-icon {
		width: 40px;
		height: 40px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 15px;
		font-size: 20px;
	}

	.wechat-icon {
		color: #07c160;
	}

	.alipay-icon {
		color: #1677ff;
	}

	.method-info {
		flex: 1;
	}

	.method-name {
		font-size: 16px;
		color: #333;
		margin-bottom: 4px;
		font-weight: 500;
	}

	.method-desc {
		font-size: 12px;
		color: #999;
	}

	.method-right {
		margin-left: 15px;
	}

	.radio-btn {
		width: 20px;
		height: 20px;
		border: 2px solid #ddd;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.3s;
	}

	.radio-btn.active {
		border-color: #ff4757;
		background-color: #ff4757;
	}

	.radio-inner {
		width: 8px;
		height: 8px;
		background-color: white;
		border-radius: 50%;
		opacity: 0;
		transition: opacity 0.3s;
	}

	.radio-btn.active .radio-inner {
		opacity: 1;
	}

	/* 底部支付按钮样式 */
	.payment-footer {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		background: white;
		padding: 15px 20px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-top: 1px solid #eee;
		z-index: 100;
	}

	.price-info {
		font-size: 14px;
		color: #666;
	}

	.pay-btn {
		background: #ff4757;
		color: white;
		padding: 12px 30px;
		border-radius: 25px;
		cursor: pointer;
		font-size: 16px;
		font-weight: bold;
		transition: background-color 0.3s;
	}

	.pay-btn:hover {
		background: #ff3742;
	}

	/* 支付确认弹窗样式 */
	.payment-modal {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background: white;
		border-radius: 8px;
		width: 90%;
		max-width: 400px;
		overflow: hidden;
	}

	.modal-header {
		padding: 20px;
		border-bottom: 1px solid #eee;
		text-align: center;
	}

	.modal-header h3 {
		margin: 0;
		color: #333;
	}

	.modal-body {
		padding: 20px;
	}

	.modal-body p {
		margin: 10px 0;
		color: #666;
	}

	.modal-footer {
		display: flex;
		border-top: 1px solid #eee;
	}

	.cancel-btn, .confirm-btn {
		flex: 1;
		padding: 15px;
		border: none;
		font-size: 16px;
		cursor: pointer;
	}

	.cancel-btn {
		background: #f5f5f5;
		color: #666;
	}

	.confirm-btn {
		background: #ff4757;
		color: white;
	}

	/* 加载状态样式 */
	.loading-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 2000;
	}

	.loading-content {
		background: white;
		padding: 30px;
		border-radius: 8px;
		text-align: center;
	}

	.loading-spinner {
		width: 40px;
		height: 40px;
		border: 4px solid #f3f3f3;
		border-top: 4px solid #ff4757;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		margin: 0 auto 15px;
	}

	.loading-text {
		color: #666;
		font-size: 14px;
	}

	@keyframes spin {
		0% { transform: rotate(0deg); }
		100% { transform: rotate(360deg); }
	}
</style>