<template>
	<view class="my-courses">
		<view class="title">我的课程</view>
		<view class='order-courses'>
			<view class="order-header">
				<view class="header-item">
					<checkbox :checked="isAllSelected" @change="handleSelectAll" /> 全选
				</view>
				<view class="header-item">课程</view>
				<view class="header-item">价格</view>
				<view class="header-item">数量</view>
				<view class="header-item">操作</view>
			</view>

			<view v-for="(item, index) in orderList" :key="index" class="order-item">
				<view class="select-item">
					<checkbox :checked="item.selected" @change="handleSelectItem(index)" />
				</view>
				<view class='course-image'>
					<image :src='item.course_picture'></image>
				</view>
				<view class='course-info'>
					<text>{{ item.course_name }}</text>
					<text class="price">￥{{ item.course_price }}</text>
					<text>{{ item.course_quantity }}</text>
				</view>
				<button @click="removeFromOrders(index)">删除</button>
			</view>
		</view>
	</view>
</template>


<script>
	export default {
		data() {
			return {

				orderList: [], // 订单列表
			};
		},
		computed: {
			// 计算已支付订单总价
			// totalPrice() {
			//   return this.order_items.reduce((total, item) => total + item.price * item.quantity, 0);
			// },
		},
		handleSelectAll(e) {
			const isSelected = e.detail.value;
			this.orderList.forEach(item => {
				item.selected = isSelected;
			});
		},
		handleSelectItem(index) {
			this.orderList[index].selected = !this.orderList[index].selected;
		},

		async removeFromOrders(index) {
			const item = this.orderList[index];
			await uni.request({
				url: `https://api.service.sclrkj.com.cn/service3/api/cart/remove/${item.id}`,
				method: 'DELETE',
				header: {
					'Authorization': 'Bearer ' + uni.getStorageSync('token'),
				},
			});
			this.orderList.splice(index, 1); // 从本地列表中移除
		},
	

		async mounted() {
				// 获取购物车和订单数据

			await this.fetchOrderList();
		},
		
		methods: {	
			async fetchOrderList() {
					// const res = await uni.request({
					//   url: 'https://api.service.sclrkj.com.cn/service3/api/orderlist',
					//   method: 'GET',
					//   header: {
					// 	'Authorization': 'Bearer ' + uni.getStorageSync('token'),
					//   },
					// });
					// this.order_items = res.data.result;
					//  },

				const res = await uni.request({
					url: 'http://your-flask-server/get_my_courses',
					method: 'GET',
					header: {
						'Authorization': 'Bearer ' + uni.getStorageSync('token'),
					},
					data: {
						user_id: this.$store.state.userInfo.id, // 当前用户的 ID
					},
					success: (res) => {
						if (res.data.status === 'success') {
							this.orderList = res.data.orderCourses; // 将课程信息绑定到页面数据
						} else {
							console.error('Failed to fetch my courses:', res.data.message);
						}
					},
					fail: (err) => {
						console.error('Request failed:', err);
					}
				});
			}
		}	
	}	
				
</script>

<style lang='scss'>
	.my-courses {
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		width: 100%;
		margin-bottom: 20px;

		.title {
			font-size: 18px;
			font-weight: bold;
			margin-left: 100rpx;
			margin-bottom: 10px;
		}

		.order-courses {
			display: flex;
			flex-direction: column;
			align-content: space-between;
			box-sizing: border-box;
			width: 100%;
			padding-bottom: 30rpx;

			.order-header {
				display: flex;
				justify-content: space-between;
				padding: 10px 0;
				border-bottom: 1px solid #eee;

				.header-item {
					flex: 1;
					text-align: center;
				}
			}

			.order-item {
				display: flex;
				flex-direction: row;
				box-sizing: border-box;
				align-items: center;
				justify-content: space-between;
				padding: 10px;
				border-bottom: 1px solid #eee;

				.select-item {
					flex: 0.1;
					text-align: center;
				}

				.course-image {
					box-sizing: border-box;
					width: 30%;
					height: 100rpx;

					image {
						display: flex;
						width: 100%;
						height: 100%;
					}
				}

				.course-info {
					display: flex;
					flex-direction: row;
					box-sizing: border-box;
					width: 50%;
					height: 100%;

					text {
						justify-content: flex-end;
						align-items: center;
						font-size: 20rpx;
						color: black;
					}

					.price {
						color: #f40;
						margin: 5px 0;
					}

				}

				button {
					align-items: center;
					font-size: 20rpx;
					background-color: blue;
				}
			}
		}
	}
</style>