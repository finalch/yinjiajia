<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 应用启动时的初始化逻辑
		},
		onShow: function() {
			console.log('App Show')
			// 应用显示时的逻辑
		},
		onHide: function() {
			console.log('App Hide')
			// 应用隐藏时的逻辑
		}
	}
</script>

<style>
	/*每个页面公共css */
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}
	
	body {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
			'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
			sans-serif;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
		background-color: #f5f5f5;
	}
	
	/* 全局样式变量 */
	page {
		background-color: #f5f5f5;
		font-size: 14px;
		line-height: 1.5;
		color: #333;
	}
	
	/* 通用容器样式 */
	.container {
		padding: 20rpx;
	}
	
	/* 通用按钮样式 */
	.btn {
		padding: 20rpx 40rpx;
		border-radius: 8rpx;
		font-size: 28rpx;
		text-align: center;
	}
	
	.btn-primary {
		background-color: #3cc51f;
		color: #fff;
	}
	
	/* 通用卡片样式 */
	.card {
		background-color: #fff;
		border-radius: 12rpx;
		padding: 20rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
	}
</style>
