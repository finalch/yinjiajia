<template>
  <div class="address-container">
    <!-- 头部 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span>←</span>
      </div>
      <div class="title">收货地址</div>
      <div class="add-btn" @click="showAddAddress">
        <span>+</span>
      </div>
    </div>

    <!-- 地址列表 -->
    <div class="address-list" v-if="addresses.length > 0">
      <div 
        class="address-item" 
        v-for="address in addresses" 
        :key="address.id"
        @click="selectAddress(address)"
      >
        <div class="address-info">
          <div class="receiver-info">
            <span class="receiver-name">{{ address.receiver_name }}</span>
            <span class="receiver-phone">{{ address.phone }}</span>
            <span class="default-tag" v-if="address.is_default">默认</span>
          </div>
          <div class="address-detail">
            {{ address.full_address }}
          </div>
        </div>
        <div class="address-actions">
          <div class="action-btn edit-btn" @click.stop="editAddress(address)">
            <span>✏️</span>
          </div>
          <div class="action-btn delete-btn" @click.stop="deleteAddress(address)">
            <span>🗑️</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <div class="empty-icon">📍</div>
      <div class="empty-text">暂无收货地址</div>
      <div class="empty-desc">添加收货地址，享受便捷购物</div>
      <div class="add-address-btn" @click="showAddAddress">
        添加地址
      </div>
    </div>

    <!-- 添加/编辑地址弹窗 -->
    <div class="modal-overlay" v-if="showModal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <div class="modal-title">{{ isEditing ? '编辑地址' : '添加地址' }}</div>
          <div class="close-btn" @click="closeModal">×</div>
        </div>
        
        <div class="form-content">
          <div class="form-item">
            <label>收货人</label>
            <input 
              v-model="addressForm.receiver_name" 
              placeholder="请输入收货人姓名"
              maxlength="20"
            />
          </div>
          
          <div class="form-item">
            <label>手机号</label>
            <input 
              v-model="addressForm.phone" 
              placeholder="请输入手机号"
              type="tel"
              maxlength="11"
            />
          </div>
          
          <div class="form-item">
            <label>省份</label>
            <input 
              v-model="addressForm.province" 
              placeholder="请输入省份"
            />
          </div>
          
          <div class="form-item">
            <label>城市</label>
            <input 
              v-model="addressForm.city" 
              placeholder="请输入城市"
            />
          </div>
          
          <div class="form-item">
            <label>区县</label>
            <input 
              v-model="addressForm.district" 
              placeholder="请输入区县"
            />
          </div>
          
          <div class="form-item">
            <label>详细地址</label>
            <textarea 
              v-model="addressForm.detail_address" 
              placeholder="请输入详细地址"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-item checkbox-item">
            <label>
              <input 
                type="checkbox" 
                v-model="addressForm.is_default"
              />
              设为默认地址
            </label>
          </div>
        </div>
        
        <div class="modal-actions">
          <div class="cancel-btn" @click="closeModal">取消</div>
          <div class="save-btn" @click="saveAddress">保存</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { request } from '../utils/api.js'

export default {
  name: 'Address',
  data() {
    return {
      addresses: [],
      showModal: false,
      isEditing: false,
      editingAddressId: null,
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
  mounted() {
    this.loadAddresses()
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },
    
    async loadAddresses() {
      try {
        const response = await request.get('/api/app/address/', {
          params: { user_id: 1 } // TODO: 从用户状态获取
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
      if (!confirm(`确定要删除地址"${address.receiver_name}"吗？`)) {
        return
      }
      
      try {
        const response = await request.delete(`/api/app/address/${address.id}`)
        if (response.data.code === 200) {
          this.loadAddresses()
        }
      } catch (error) {
        console.error('删除地址失败:', error)
      }
    },
    
    async saveAddress() {
      // 验证表单
      if (!this.addressForm.receiver_name) {
        alert('请输入收货人姓名')
        return
      }
      if (!this.addressForm.phone) {
        alert('请输入手机号')
        return
      }
      if (!this.addressForm.province || !this.addressForm.city || !this.addressForm.district) {
        alert('请完善地址信息')
        return
      }
      if (!this.addressForm.detail_address) {
        alert('请输入详细地址')
        return
      }
      
      try {
        const data = {
          user_id: 1, // TODO: 从用户状态获取
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
      if (this.$route.query.from === 'checkout') {
        this.$router.go(-1)
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