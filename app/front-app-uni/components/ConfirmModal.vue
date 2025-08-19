<template>
	<view v-if="visible" class="modal-overlay" @click="handleOverlayClick">
		<view class="modal-content" :class="typeClass" @click.stop>
			<view class="modal-header">
				<text class="modal-title">{{ title }}</text>
			</view>
			<view class="modal-body">
				<text class="modal-message">{{ content }}</text>
			</view>
			<view class="modal-footer">
				<button 
					class="modal-btn cancel-btn" 
					@click="handleCancel"
				>
					{{ cancelText }}
				</button>
				<button 
					class="modal-btn confirm-btn" 
					@click="handleConfirm"
				>
					{{ confirmText }}
				</button>
			</view>
		</view>
	</view>
</template>

<script>
export default {
	name: 'ConfirmModal',
	props: {
		visible: {
			type: Boolean,
			default: false
		},
		title: {
			type: String,
			default: '确认'
		},
		content: {
			type: String,
			default: ''
		},
		confirmText: {
			type: String,
			default: '确定'
		},
		cancelText: {
			type: String,
			default: '取消'
		},
		type: {
			type: String,
			default: 'default'
		}
	},
	computed: {
		typeClass() {
			return `modal-${this.type}`
		}
	},
	methods: {
		handleConfirm() {
			this.$emit('confirm')
		},
		handleCancel() {
			this.$emit('cancel')
		},
		handleOverlayClick() {
			this.$emit('cancel')
		}
	}
}
</script>

<style scoped>
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 9999;
}

.modal-content {
	background: white;
	border-radius: 16px;
	width: 80%;
	max-width: 320px;
	overflow: hidden;
	box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.modal-header {
	padding: 24px 24px 16px;
	text-align: center;
	border-bottom: 1px solid #f0f0f0;
}

.modal-title {
	font-size: 18px;
	font-weight: 600;
	color: #333;
}

.modal-body {
	padding: 20px 24px;
	text-align: center;
}

.modal-message {
	font-size: 16px;
	color: #666;
	line-height: 1.5;
}

.modal-footer {
	display: flex;
	border-top: 1px solid #f0f0f0;
}

.modal-btn {
	flex: 1;
	padding: 16px;
	border: none;
	background: none;
	font-size: 16px;
	cursor: pointer;
	transition: background-color 0.2s;
}

.modal-btn:active {
	background-color: #f5f5f5;
}

.cancel-btn {
	color: #999;
	border-right: 1px solid #f0f0f0;
}

.confirm-btn {
	color: #007aff;
	font-weight: 500;
}

/* 为退出登录特殊样式 */
.modal-logout .modal-title {
	color: #ff4757;
}

.modal-logout .confirm-btn {
	color: #ff4757;
}

.modal-logout .modal-content {
	border: 2px solid #ff4757;
}

.modal-logout .modal-header {
	background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
}

.modal-logout .modal-title {
	color: white;
}

.modal-logout .modal-footer {
	border-top: 1px solid #ff4757;
}

/* 为删除操作特殊样式 */
.modal-delete .modal-title {
	color: #ff4757;
}

.modal-delete .confirm-btn {
	color: #ff4757;
	font-weight: 600;
}

.modal-delete .modal-content {
	border: 2px solid #ff4757;
}

.modal-delete .modal-header {
	background: linear-gradient(135deg, #ff4757 0%, #ff6b7a 100%);
}

.modal-delete .modal-title {
	color: white;
}

.modal-delete .modal-footer {
	border-top: 1px solid #ff4757;
}
</style>
