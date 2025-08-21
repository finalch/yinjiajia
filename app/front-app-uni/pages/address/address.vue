<template>
  <view class="address-container">
    <!-- 头部 -->
    <view class="header">
      <view class="back-btn" @click="goBack">
        <text>←</text>
      </view>
      <view class="title">收货地址</view>
      <view class="add-btn" @click="showAddAddress">
        <text>+</text>
      </view>
    </view>

    <!-- 地址列表 -->
    <view class="address-list" v-if="addresses.length > 0">
      <view 
        class="address-item" 
        v-for="address in addresses" 
        :key="address.id"
        @click="selectAddress(address)"
      >
        <view class="address-info">
          <view class="receiver-info">
            <text class="receiver-name">{{ address.receiver_name }}</text>
            <text class="receiver-phone">{{ address.phone }}</text>
            <text class="default-tag" v-if="address.is_default">默认</text>
          </view>
          <view class="address-detail">
            {{ address.full_address }}
          </view>
        </view>
        <view class="address-actions">
          <view class="action-btn edit-btn" @click.stop="editAddress(address)">
            <text>✏️</text>
          </view>
          <view class="action-btn delete-btn" @click.stop="deleteAddress(address)">
            <text>��️</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-text">暂无收货地址</view>
      <view class="empty-desc">添加收货地址，享受便捷购物</view>
      <view class="add-address-btn" @click="showAddAddress">
        添加地址
      </view>
    </view>

    <!-- 添加/编辑地址弹窗 -->
    <view class="modal-overlay" v-if="showModal" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <view class="modal-title">{{ isEditing ? '编辑地址' : '添加地址' }}</view>
          <view class="close-btn" @click="closeModal">×</view>
        </view>
        
        <view class="form-content">
          <view class="form-item">
            <label>收货人</label>
            <input 
              v-model="addressForm.receiver_name" 
              placeholder="请输入收货人姓名"
              maxlength="20"
            />
          </view>
          
          <view class="form-item">
            <label>手机号</label>
            <input 
              v-model="addressForm.phone" 
              placeholder="请输入手机号"
              type="tel"
              maxlength="11"
            />
          </view>
          
          <view class="form-item">
            <label>省份</label>
            <input 
              v-model="addressForm.province" 
              placeholder="请输入省份"
            />
          </view>
          
          <view class="form-item">
            <label>城市</label>
            <input 
              v-model="addressForm.city" 
              placeholder="请输入城市"
            />
          </view>
          
          <view class="form-item">
            <label>区县</label>
            <input 
              v-model="addressForm.district" 
              placeholder="请输入区县"
            />
          </view>
          
          <view class="form-item">
            <label>详细地址</label>
            <textarea 
              v-model="addressForm.detail_address" 
              placeholder="请输入详细地址"
              rows="3"
            ></textarea>
          </view>
          
          <view class="form-item checkbox-item">
            <label>
              <input 
                type="checkbox" 
                v-model="addressForm.is_default"
              />
              设为默认地址
            </label>
          </view>
        </view>
        
        <view class="modal-actions">
          <view class="cancel-btn" @click="closeModal">取消</view>
          <view class="save-btn" @click="saveAddress">保存</view>
        </view>
      </view>
    </view>
  </view>

  <!-- 删除确认弹窗 -->
  <ConfirmModal
    :visible="showDeleteModal"
    title="确认删除"
    :content="deleteConfirmContent"
    confirm-text="删除"
    cancel-text="取消"
    type="delete"
    @confirm="performDeleteAddress"
    @cancel="showDeleteModal = false"
  />
</template>

<script>
import { getUserId } from '@/src/utils/auth.js'
import request from '@/src/utils/request.js'
import ConfirmModal from '@/components/ConfirmModal.vue'

export default {
  name: 'Address',
  components: {
    ConfirmModal
  },
  data() {
    return {
      addresses: [],
      showModal: false,
      isEditing: false,
      editingAddressId: null,
      fromPage: '', // 记录来源页面
      showDeleteModal: false, // 显示删除确认弹窗
      deleteAddressId: null, // 要删除的地址ID
      deleteAddressName: '', // 要删除的地址名称
      addressForm: {
        receiver_name: '',
        phone: '',
        province: '',
        city: '',
        district: '',
        detail_address: '',
        is_default: false
      }
    }
  },
  computed: {
    deleteConfirmContent() {
      return `确定要删除地址"${this.deleteAddressName}"吗？`
    }
  },
  onLoad(options) {
    // 获取页面参数
    if (options.from) {
      this.fromPage = options.from
    }
    this.loadAddresses()
  },
  methods: {
    goBack() {
      uni.navigateBack()
    },
    
    async loadAddresses() {
      try {
        const response = await request.get('/api/app/address/', {
          params: { user_id: getUserId() }
        })
        if (response.data.code === 200) {
          this.addresses = response.data.data
        }
      } catch (error) {
        console.error('加载地址失败:', error)
      }
    },
    
    showAddAddress() {
      this.isEditing = false
      this.editingAddressId = null
      this.resetForm()
      this.showModal = true
    },
    
    editAddress(address) {
      this.isEditing = true
      this.editingAddressId = address.id
      this.addressForm = { ...address }
      this.showModal = true
    },
    
    async deleteAddress(address) {
      // 设置要删除的地址信息
      this.deleteAddressId = address.id
      this.deleteAddressName = address.receiver_name
      this.showDeleteModal = true
    },
    
    async performDeleteAddress() {
      try {
        const response = await request.delete(`/api/app/address/${this.deleteAddressId}`)
        if (response.data.code === 200) {
          this.loadAddresses()
          this.showDeleteModal = false
          // 重置删除相关变量
          this.deleteAddressId = null
          this.deleteAddressName = ''
        }
      } catch (error) {
        console.error('删除地址失败:', error)
      }
    },
    
    async saveAddress() {
      // 验证表单
      if (!this.addressForm.receiver_name) {
        uni.showToast({
          title: '请输入收货人姓名',
          icon: 'error'
        })
        return
      }
      if (!this.addressForm.phone) {
        uni.showToast({
          title: '请输入手机号',
          icon: 'error'
        })
        return
      }
      if (!this.addressForm.province || !this.addressForm.city || !this.addressForm.district) {
        uni.showToast({
          title: '请完善地址信息',
          icon: 'error'
        })
        return
      }
      if (!this.addressForm.detail_address) {
        uni.showToast({
          title: '请输入详细地址',
          icon: 'error'
        })
        return
      }
      
      try {
        const data = {
        user_id: getUserId(),
          ...this.addressForm
        }
        
        let response
        if (this.isEditing) {
          response = await request.put(`/api/app/address/${this.editingAddressId}`, data)
        } else {
          response = await request.post('/api/app/address/', data)
        }
        
        if (response.data.code === 200) {
          this.closeModal()
          this.loadAddresses()
        }
      } catch (error) {
        console.error('保存地址失败:', error)
      }
    },
    
    selectAddress(address) {
      // 如果是从下单页面跳转过来的，选择地址后返回
      if (this.fromPage === 'checkout') {
        uni.navigateBack()
      }
    },
    
    closeModal() {
      this.showModal = false
      this.resetForm()
    },
    
    resetForm() {
      this.addressForm = {
        receiver_name: '',
        phone: '',
        province: '',
        city: '',
        district: '',
        detail_address: '',
        is_default: false
      }
    }
  }
}
</script>

<style scoped>
.address-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 20px;
}

.header {
  background: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn, .add-btn {
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.address-list {
  padding: 15px;
}

.address-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.address-info {
  flex: 1;
}

.receiver-info {
  margin-bottom: 8px;
}

.receiver-name {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.receiver-phone {
  color: #666;
  margin-right: 10px;
}

.default-tag {
  background: #ff4757;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.address-detail {
  color: #333;
  line-height: 1.4;
}

.address-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
}

.edit-btn:hover {
  background: #f0f0f0;
}

.delete-btn:hover {
  background: #ffe6e6;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
}

.empty-desc {
  color: #999;
  margin-bottom: 30px;
}

.add-address-btn {
  background: #ff4757;
  color: white;
  padding: 12px 30px;
  border-radius: 25px;
  display: inline-block;
  cursor: pointer;
}

.modal-overlay {
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
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 18px;
  font-weight: bold;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.form-content {
  padding: 20px;
}

.form-item {
  margin-bottom: 15px;
}

.form-item label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-item input:focus,
.form-item textarea:focus {
  outline: none;
  border-color: #ff4757;
}

.checkbox-item {
  display: flex;
  align-items: center;
}

.checkbox-item label {
  display: flex;
  align-items: center;
  margin-bottom: 0;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: auto;
  margin-right: 8px;
}

.modal-actions {
  padding: 20px;
  display: flex;
  gap: 10px;
  border-top: 1px solid #eee;
}

.cancel-btn,
.save-btn {
  flex: 1;
  padding: 12px;
  text-align: center;
  border-radius: 6px;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
}

.save-btn {
  background: #ff4757;
  color: white;
}
</style> 