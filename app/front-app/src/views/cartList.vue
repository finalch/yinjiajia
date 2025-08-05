<template>
	<view class="section" v-if="!paymentUrl">
		<view class="title">课程库</view>
		<view class='shopping-cart'>
			<view class="cart-header">
				<view class="header-item">
					<checkbox :checked="isAllSelected" @click="toggleSelectAll" /> 全选
				</view>
				<view class="header-item">课程</view>
				<view class="header-item">价格</view>
				<view class="header-item">数量</view>
				<view class="header-item">操作</view>
			</view>

			<view v-for="(item, index) in cartList" :key="item.id" class="cart-item">
				<view class="select-item">
					<checkbox :checked="item.selected" @click="toggleSelectItem(item)" style="width: 20rpx; height: 20rpx" />
				</view>
				<view class='product-image'>
					<image :src='item.picture'></image>
					<view class='product-name'>{{ item.name }}</view>
				</view>				
				<view class='product-price'><text>￥{{ item.price }}</text></view>	
				<view class="quantity-control">
					<button @click="decreaseQuantity(index)">-</button>
					<text>{{ item.quantity }}</text>
					<button @click="increaseQuantity(index)">+</button>
				</view>				
				<button @click="removeFromCart(index)">删除</button>
			</view>
		</view>
		<view class="order-total">总计: ￥{{ selectedTotalPrice }}</view>
		<button @click="goToPay">去支付</button> <!-- 添加去支付按钮 -->
	</view>
	<!-- 全屏web-view用于支付 -->
	<!-- <web-view 
	  v-if="paymentUrl" 
	  :src="paymentUrl"
	  style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 9999;"
	></web-view> -->
</template>

<script>
	export default {
		data() {
			return {
				cartList: [], // 购物车列表
				paymentUrl: ''
				// userInfo: this.$store.state.user.userInfo 
			};
		},
		
		computed: {								
			
			selectedTotalPrice() {							
				const selectedItems = this.cartList.filter(item => {
					// console.log(`Item ${item.id || item.name}: selected=${item.selected}, price=${item.price}, quantity=${item.quantity}`);
					return item.selected;
				});
				const total = this.cartList.reduce((total, item) => {
					return item.selected ? total + (item.price * item.quantity) : total;
				}, 0);
				console.log('Calculating total:', total, 'Cart items:', this.cartList);
				return total;
				// return total.toFixed(2);
			},
			isAllSelected() {
				return this.cartList.length > 0 && this.cartList.every(item => item.selected);
				
			}
		},
		async mounted() {
			// 获取购物车和订单数据
			await this.fetchCartList();

		},
		methods: {
			isEmptyObject(obj) {
				return Object.keys(obj).length === 0;
			},
			// 获取购物车列表
			async fetchCartList() {
				
				try {
					// 优先从本地存储获取用户信息，其次从Vuex获取
					let userInfo = this.$store.state.user.userInfo 					
					
					if (!userInfo || this.isEmptyObject(userInfo)) {
						uni.showToast({
							title: '请先登录',
							icon: 'none',
						});
						return;
					}
					
					// 确保有user_id
					if (!userInfo.user_id) {
						uni.showToast({
							title: '用户信息不完整',
							icon: 'none',
						});
						return;
					}														

					const res = await this.getCartList(userInfo.user_id);
					console.log(res);
					
					if (res.code === 200) {
						this.cartList = res.data.items.map(item => ({
							...item,
							id: item.id,
							name: item.product_name,
							price: item.price,
							quantity: item.quantity,
							picture: item.product_image || '/static/default-product.png',
							selected: false // 默认未选中
						}));
						console.log('Fetched cart list:', this.cartList);
					} else if (res.code === 404) {
						uni.showToast({
							title: '购物车为空',
							icon: 'none'
						});
						this.cartList = []; // 清空购物车列表
					} else {
						uni.showToast({
							title: res.data.message || '获取购物车失败',
							icon: 'none'
						});
					}
					
				} catch (error) {
					uni.showToast({
						title: '网络错误，请重试',
						icon: 'none',
					});
					console.error('获取购物车列表失败:', error);				
				}	
			},
			
			getCartList(user_id) {
			    return new Promise((resolve, reject) => {
			        uni.request({
			            url: '/api/app/cart/',
			            method: 'GET',
						params: {							
							user_id: user_id												
						},
						header: {
							'Content-Type': 'application/json'
						},
			            success: (res) => {
			                if (res.data.code === 200) {
			                    resolve(res.data);								
			                } else {
			                    reject(res.data.message || '获取购物车列表失败');
			                }
			            },
			            fail: (error) => {
			                reject(error);
			            }
			        });
			    });
			},
						
			// 全选/取消全选
			toggleSelectAll(e) {
				// const isSelected = e.detail.value;				
				// this.cartList.forEach(item => {
				// 	item.selected = isSelected;
				// });
				// 使用map创建新数组确保响应性
				const newSelectState = !this.isAllSelected;
				this.cartList = this.cartList.map(item => ({
				    ...item,
				    selected: newSelectState
				}));
			},
			// 单选/取消单选
			// toggleSelectItem(index) {
			// 	this.cartList[index].selected = !this.cartList[index].selected;
			// },
			
			toggleSelectItem(item) {
				item.selected = !item.selected
			},
			
			// toggleSelectItem(selectedItem) {
			//     this.cartList = this.cartList.map(item => 
			//         item.id === selectedItem.id ? {...item, selected: !item.selected} : item
			//     );
			// },

			// 增加商品数量
			async increaseQuantity(index) {
				const item = this.cartList[index];
				const newQuantity = item.quantity + 1;
				
				try {
					const response = await this.updateCartItemQuantity(item.id, newQuantity);
					if (response.code === 200) {
						item.quantity = newQuantity;
					} else {
						uni.showToast({
							title: response.message || '更新失败',
							icon: 'none'
						});
					}
				} catch (error) {
					console.error('更新数量失败:', error);
					uni.showToast({
						title: '网络错误',
						icon: 'none'
					});
				}
			},
			// 减少商品数量
			// 减少商品数量
			async decreaseQuantity(index) {
				const item = this.cartList[index];
				if (item.quantity > 1) {
					const newQuantity = item.quantity - 1;
					
					try {
						const response = await this.updateCartItemQuantity(item.id, newQuantity);
						if (response.code === 200) {
							item.quantity = newQuantity;
						} else {
							uni.showToast({
								title: response.message || '更新失败',
								icon: 'none'
							});
						}
					} catch (error) {
						console.error('更新数量失败:', error);
						uni.showToast({
							title: '网络错误',
							icon: 'none'
						});
					}
				}
			},
			
			async removeFromCart(index) {
				const item = this.cartList[index];
				
				try {
					const response = await this.deleteCartItem(item.id);
					if (response.code === 200) {
						this.cartList.splice(index, 1);
						uni.showToast({
							title: '删除成功',
							icon: 'success'
						});
					} else {
						uni.showToast({
							title: response.message || '删除失败',
							icon: 'none'
						});
					}
				} catch (error) {
					console.error('删除失败:', error);
					uni.showToast({
						title: '网络错误',
						icon: 'none'
					});
				}
			},	
				
			deleteFromCart(index) {
				let userInfo = this.$store.state.user.userInfo;
				const item = this.cartList[index];
				if (!item || !userInfo) {
					return Promise.reject(new Error('无效的商品或用户信息'));
				}
				
			    return new Promise((resolve, reject) => {
					
			        uni.request({
			            url: `https://api.service.sclrkj.com.cn/service3/api/cart/remove/${item.id}`,
						method: 'DELETE',
						data: {
							user_id: userInfo.user_id
						},
						header: {
							'Content-Type': 'application/json',							
						},
					
			            success: (res) => {
							console.log('res:',res)
			                // 检查HTTP状态码
							if (res.statusCode >= 200 && res.statusCode < 300) {
								// 确保响应数据是JSON格式
								if (res.data && typeof res.data === 'object') {
									resolve(res.data);
								} else {
									// 如果后端返回空内容，构造标准响应
									resolve({ code: res.statusCode, message: '删除成功' });
								}							
			                } else {
			                    // 根据HTTP状态码提供更具体的错误信息
								const errorMsg = res.data?.message || `请求失败，状态码: ${res.statusCode}`;
								reject(new Error(errorMsg));
							}
						},
			            fail: (error) => {
			                reject(error);
			            }
			        });
			    });
						},
			
			// 更新购物车商品数量
			updateCartItemQuantity(itemId, quantity) {
				return new Promise((resolve, reject) => {
					uni.request({
						url: `/api/app/cart/${itemId}`,
						method: 'PUT',
						data: {
							quantity: quantity,
							user_id: 1 // TODO: 从用户状态获取
						},
						header: {
							'Content-Type': 'application/json'
						},
						success: (res) => {
							if (res.data.code === 200) {
								resolve(res.data);
							} else {
								reject(res.data.message || '更新失败');
							}
						},
						fail: (error) => {
							reject(error);
						}
					});
				});
			},
			
			// 删除购物车商品API
			deleteCartItem(itemId) {
				return new Promise((resolve, reject) => {
					uni.request({
						url: `/api/app/cart/${itemId}`,
						method: 'DELETE',
						params: {
							user_id: 1 // TODO: 从用户状态获取
						},
						header: {
							'Content-Type': 'application/json'
						},
						success: (res) => {
							if (res.data.code === 200) {
								resolve(res.data);
							} else {
								reject(res.data.message || '删除失败');
							}
						},
						fail: (error) => {
							reject(error);
						}
					});
				});
			},
			
			async goToPay() {
			    try {
			        // 1. 检查是否有选中商品
			        const selectedItems = this.cartList.filter(item => item.selected);
			        if (selectedItems.length === 0) {
			            uni.showToast({
			                title: '请选择至少一个商品',
			                icon: 'none',
			            });
			        return;
			        }
			
			        // 2. 计算总金额
			        const totalAmount = selectedItems.reduce((total, item) => {
			            return total + (item.price * item.quantity);
			        }, 0);
			
			        // 3. 跳转到支付方式选择页面
			        const cartItemIds = selectedItems.map(item => item.id).join(',');
			        this.$router.push({
			            path: '/payment-method',
			            query: { 
			                cart_items: cartItemIds,
			                total_amount: totalAmount.toFixed(2)
			            }
			        });
			    } catch (error) {
			        console.error('跳转下单页面失败:', error);
			        uni.showToast({
			            title: error.message || '跳转失败',
			            icon: 'none'
			        });
			    }
			},

			// 轮询检查支付状态
			async pollPaymentStatus(orderId) {
			    const maxRetry = 30; // 最大重试次数，约3分钟(每6秒一次)
			    
			    for (let retryCount = 0; retryCount < maxRetry; retryCount++) {
			        try {
			            const res = await this.checkOrderStatus(orderId);
						console.log('pollpayment:',res);
			            if (res.data.status === 'paid') {
			                return true; // 支付成功
			            }			            
			            // 等待6秒后再次检查
			            await new Promise(resolve => setTimeout(resolve, 6000));
			        } catch (error) {
			            console.error('检查支付状态出错:', error);
			            // 发生错误也继续重试
			            await new Promise(resolve => setTimeout(resolve, 6000));
			        }
			    }			    
			    return false; // 超过最大重试次数仍未支付成功
			},
								
			// 创建订单
			createOrders(selectedItems) {
				// 清理数据，只保留必要的字段
				const cleanedItems = selectedItems.map(item => ({
					id: item.id,
					category_id: item.categoryId,
					course_id: item.courseId,
					course_name: item.name,
					course_price: item.price,
					course_quantity: item.quantity,
					course_picture: item.picture
				}));
				const userInfo = this.$store.state.user.userInfo;
								
				console.log('Calculated Total Price:', this.selectedTotalPrice);
				
			    return new Promise((resolve, reject) => {
					
			        uni.request({
			            url: 'https://api.service.sclrkj.com.cn/service3/api/createOrder',
			            method: 'POST',
			            header: {
			                'Content-Type': 'application/json'
			            },
			            data: {
			                user_id: userInfo.user_id,
			                items: cleanedItems,
			                totalPrice: parseFloat(this.selectedTotalPrice),
			            },
			            success: (res) => {
							console.log('res:',res);
			                if (res.statusCode === 201 && res.data) {
			                    resolve(res);
			                } else {
			                    reject(new Error(res.data.message || '创建订单失败'));
			                }
			            },
			            fail: (err) => {
			                reject(new Error('网络请求失败'));
			            }
			        });
			    });
			},
			
			// 获取支付参数
			payOrders(orderId) {
			    return new Promise((resolve, reject) => {
			        uni.request({
			            url: `https://api.service.sclrkj.com.cn/service3/api/getPaymentParams/${orderId}`,
			            method: 'GET',			            
			            success: (res) => {
							console.log('payorders:',res);
			                if (res.statusCode === 200 && res.data) {
			                    resolve(res.data);
			                } else {
			                    reject(new Error(res.data.message || '获取支付参数失败'));
			                }
			            },
			            fail: (err) => {
			                reject(new Error('网络请求失败'));
			            }
			        });
			    });
			},						
			
			// payment(paymentParams) {
			//     return new Promise((resolve, reject) => {
			//         uni.request({
			//             url: 'https://api.service.sclrkj.com.cn/service3/api/handlePayment',
			//             method: 'POST',
			//             data: paymentParams,
			//             success: (res) => {
			// 				console.log('payment res:',res);
			//                 if (res.statusCode === 200) {
			// 					resolve(res.data);			                    															
			// 					// resolve({ errMsg: 'payment:ok' });
			//                 } else {
			//                     reject(new Error(res.data.message || '支付处理失败'));
			//                 }
			//             },
			//             fail: (err) => {
			//                 reject(new Error('网络请求失败'));
			//             }
			//         });
			//     });
			// },
			
			// 检查订单状态
			checkOrderStatus(orderId) {
			    return new Promise((resolve, reject) => {
			        uni.request({
			            url: `https://api.service.sclrkj.com.cn/service3/api/checkOrderStatus/${orderId}`,
			            method: 'GET',
			            success: (res) => {
							console.log('check res:',res);
			                if (res.statusCode === 200) {
			                    resolve(res.data);
			                } else {
			                    reject(new Error(res.data.message || '检查订单状态失败'));
			                }
			            },
			            fail: (err) => {
			                reject(new Error('网络请求失败'));
			            }
			        });
			    });
			},
			
			// 加入我的订单
			addToOrders(orderId) {
			    return new Promise((resolve, reject) => {
			        uni.request({
			            url: 'https://api.service.sclrkj.com.cn/service3/add_to_my_courses',
			            method: 'POST',						
			            header: {			                
			                'Content-Type': 'application/json'
			            },
			            data: {
			                user_id: this.$store.state.user.userInfo.user_id,
			                order_id: orderId
			            },
			            success: (res) => {
			                if (res.statusCode === 200 && res.data) {
			                    resolve(res);
			                } else {
			                    reject(new Error(res.data.message || '加入我的课程失败'));
			                }
			            },
			            fail: (err) => {
			                reject(new Error('网络请求失败'));
			            }
			        });
			    });
			},
			
			// 清空已选商品
			clearSelectedItems() {
			    this.cartList.forEach(item => {
			        item.selected = false;
			    });
			    // 如果需要更新到后端，可以在这里调用API
			}									
		}		
	}
</script>

<style lang='scss'>
	.section {
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		width: 100%;
		margin-bottom: 20px;

		.title {
			font-size: 30rpx;
			font-weight: bold;
			margin: 10rpx 100rpx;
		}

		.shopping-cart {
			display: flex;
			flex-direction: column;
			align-content: space-between;
			box-sizing: border-box;
			width: 100%;
			padding-bottom: 30rpx;

			.cart-header {
				display: flex;
				justify-content: space-between;
				padding: 10rpx 0;
				border-bottom: 1rpx solid #eee;

				.header-item {
					flex: 1;
					font-size: 24rpx;
					text-align: center;
				}
			}

			.cart-item {
				display: flex;
				width:100%;
				height:200rpx;
				flex-direction: row;
				box-sizing: border-box;
				align-items: center;
				justify-content: space-between;
				padding: 20rpx;
				border-bottom: 1rpx solid #eee;

				.select-item {
					flex: 0 0 15%;
					text-align: center;					
				}

				.product-image {
					flex:1;					
					box-sizing: border-box;
					height: 100%;
					width:200rpx;

					image {						
						width: 100%;
						height: 80%;
					}
					.product-name{
						width: 100%;
						height: 20%;
						font-size: 24rpx;
						text-align: center;
					}
				}

				.product-price {
					flex:1;
					display: flex;
					box-sizing: border-box;
					align-items: center;
					justify-content: center;
					height: 100%;
										
					text{						
						display:flex;
						/* width: 100%; */						
						text-align: center;
						font-size: 20rpx;
						color: #f40;
					}
				}

				.quantity-control {
					flex:1;					
					height:100%;
					align-items: center;
					justify-content: center;
					flex-direction: column;

					button {						
						width: 30rpx;
						height: 30rpx;
						line-height: 30rpx;
						text-align: center;
						border: 1rpx solid #ddd;
						background-color: #f8f8f8;
					}

					text {
						width: 30rpx;
						height: 15rpx;
						margin: 0 10rpx;
						text-align: center;
						size:10rpx;
					}
				}
			
				button {
					flex:0 0 15%;
					align-items: center;
					font-size: 20rpx;
					background-color: blue;
				}
			}
		}

		.order-total {
			display: flex;
			box-sizing: border-box;
			flex-direction: row;
			justify-content: flex-end;
			width: 100%;
			height: 30rpx;
			padding-right: 50rpx;
			margin-bottom: 50rpx;
		}
	}
</style>