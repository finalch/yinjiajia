<template>
	<view class="payment-container">
		<!-- 顶部导航栏 -->
		<uni-nav-bar title="支付订单" left-icon="back" @clickLeft="goBack"></uni-nav-bar>

		<!-- 订单信息 -->
		<view class="order-info">
			<view class="info-item">
				<text class="label">订单编号：</text>
				<text class="value">{{ orderInfo.orderNo }}</text>
				<text class="copy-btn" @click="copyOrderNo">复制</text>
			</view>
			<view class="info-item">
				<text class="label">创建时间：</text>
				<text class="value">{{ orderInfo.createTime }}</text>
			</view>
			<view class="info-item">
				<text class="label">商品名称：</text>
				<text class="value">{{ orderInfo.productName }}</text>
			</view>
			<view class="info-item">
				<text class="label">应付金额：</text>
				<text class="price">¥{{ orderInfo.totalAmount }}</text>
			</view>
		</view>

		<!-- 支付方式选择 -->
		<view class="payment-methods">
			<view class="section-title">选择支付方式</view>
			<radio-group @change="paymentMethodChange">
				<!-- 简化支付方式，只保留微信和支付宝 -->
				<label class="method-item" v-for="(item, index) in paymentMethods" :key="item.value">
					<view class="method-left">
						<!-- 添加图标显示判断，避免App端路径问题 -->
						<image class="method-icon" :src="item.icon" v-if="item.icon"></image>
						<uni-icons v-else :type="item.iconType" size="24" :color="item.iconColor"></uni-icons>
						<text class="method-name">{{ item.name }}</text>
					</view>
					<view class="method-right">
						<!-- 移除radio上的style属性，改为在style标签中统一设置 -->
						<radio :value="item.value" :checked="item.value === currentMethod" color="#ff2442"></radio>
					</view>
				</label>
			</radio-group>
		</view>

		<!-- 底部支付按钮 -->
		<view class="payment-footer">
			<view class="price-info">
				<text>应付：</text>
				<text class="price">¥{{ orderInfo.totalAmount }}</text>
			</view>
			<button class="pay-btn" @click="confirmPayment">立即支付</button>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				orderInfo: {
					orderNo: '20230701123456',
					createTime: '2023-07-01 12:34:56',
					productName: '',
					totalAmount: '0.00'
				},
				// 简化支付方式，只保留微信和支付宝
				paymentMethods: [{
						name: '微信支付',
						value: 'wechat',
						icon: '/static/images/payment/wechat.png',
						iconType: 'weixin',
						iconColor: '#09BB07'
					},
					{
						name: '支付宝',
						value: 'alipay',
						icon: '/static/images/payment/alipay.png',
						iconType: 'staff',
						iconColor: '#00AAEE'
					}
				],
				currentMethod: 'wechat',
				productId: '',
				productPrice: ''
			}
		},
		onLoad(options) {
			// 从商品页面传递过来的参数
			this.productId = options.productId || '';
			this.productPrice = options.price || '0.00';

			// 模拟订单数据
			this.orderInfo.productName = '商品' + this.productId;
			this.orderInfo.totalAmount = this.productPrice;
			this.orderInfo.orderNo = '' + new Date().getTime();
			this.orderInfo.createTime = this.formatDate(new Date());

			// App端自动选择可用支付方式 - 修正条件编译语法
			// #ifdef APP-PLUS
			this.checkAvailablePaymentMethods();
			// #endif
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
				uni.navigateBack();
			},

			// 复制订单号
			copyOrderNo() {
				uni.setClipboardData({
					data: this.orderInfo.orderNo,
					success: () => {
						uni.showToast({
							title: '订单号已复制',
							icon: 'success'
						});
					}
				});
			},

			// 支付方式变更
			paymentMethodChange(e) {
				this.currentMethod = e.detail.value;
			},

			// 确认支付
			confirmPayment() {
				uni.showLoading({
					title: '正在调起支付...',
					mask: true
				});

				// 根据不同平台调用不同支付方式 - 修正条件编译语法
				// #ifdef APP-PLUS
				this.appPayment();
				// #else
				this.h5Payment();
				// #endif
			},

			// App端支付处理
			appPayment() {
				let provider = '';
				if (this.currentMethod === 'wechat') {
					provider = 'wxpay';
				} else if (this.currentMethod === 'alipay') {
					provider = 'alipay';
				}

				uni.requestPayment({
					provider: provider,
					orderInfo: this.getOrderInfoForPayment(), // 需要根据实际支付参数构造
					success: (res) => {
						uni.hideLoading();
						this.paymentSuccess();
					},
					fail: (err) => {
						uni.hideLoading();
						this.paymentFail(err);
					}
				});
			},

			// H5端支付处理
			h5Payment() {
				// 这里模拟支付成功，实际项目中需要对接支付接口
				setTimeout(() => {
					uni.hideLoading();
					this.paymentSuccess();
				}, 1500);
			},

			// 支付成功处理
			paymentSuccess() {
				uni.redirectTo({
					url: `/pages/trade-list/pay-result?status=success&orderNo=${this.orderInfo.orderNo}&amount=
					${this.orderInfo.totalAmount}`
				});
			},

			// 支付失败处理
			paymentFail(err) {
				console.error('支付失败:', err);
				uni.showModal({
					title: '支付失败',
					content: err.errMsg || '支付过程中出现问题',
					showCancel: false
				});
			},

			// 构造支付参数
			getOrderInfoForPayment() {
				// 实际项目中需要根据支付平台要求构造支付参数
				return {
					orderNo: this.orderInfo.orderNo,
					amount: this.orderInfo.totalAmount,
					subject: this.orderInfo.productName,
					// 其他必要参数...
				};
			},

			// 检查App端可用的支付方式
			checkAvailablePaymentMethods() {
				uni.getProvider({
					service: 'payment',
					success: (res) => {
						const availableMethods = [];
						this.paymentMethods.forEach(method => {
							let provider = '';
							if (method.value === 'wechat') {
								provider = 'wxpay';
							} else if (method.value === 'alipay') {
								provider = 'alipay';
							}

							if (res.provider.includes(provider)) {
								availableMethods.push(method);
							}
						});

						if (availableMethods.length > 0) {
							this.paymentMethods = availableMethods;
							this.currentMethod = availableMethods[0].value;
						} else {
							uni.showModal({
								title: '提示',
								content: '未检测到可用的支付方式',
								showCancel: false,
								success: () => {
									uni.navigateBack();
								}
							});
						}
					},
					fail: (err) => {
						console.error('获取支付供应商失败:', err);
					}
				});
			}
		}
	}
</script>

<style scoped>
	.payment-container {
		padding-bottom: 100px;
		background-color: #f5f5f5;
		min-height: 100vh;
	}

	/* 订单信息样式 */
	.order-info {
		background-color: #fff;
		padding: 20px 15px;
		margin-bottom: 10px;
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
	}

	/* 支付方式样式 */
	.payment-methods {
		background-color: #fff;
		padding: 0 15px;
	}

	.section-title {
		padding: 15px 0;
		font-size: 16px;
		font-weight: bold;
		border-bottom: 1px solid #f5f5f5;
	}

	.method-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 15px 0;
		border-bottom: 1px solid #f5f5f5;
	}

	.method-left {
		display: flex;
		align-items: center;
	}

	.method-icon {
		width: 24px;
		height: 24px;
		margin-right: 10px;
	}

	.method-name {
		font-size: 15px;
		color: #333;
	}

	/* 添加radio样式 */
	.method-right radio {
		transform: scale(0.9);
	}

	/* 底部支付按钮样式 */
	.payment-footer {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		height: 50px;
		display: flex;
		background-color: #fff;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		z-index: 100;
	}

	.price-info {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding-right: 15px;
		font-size: 14px;
		color: #333;
	}

	.pay-btn {
		width: 120px;
		height: 50px;
		line-height: 50px;
		background-color: #ff2442;
		color: #fff;
		font-size: 16px;
		border-radius: 0;
	}
</style>