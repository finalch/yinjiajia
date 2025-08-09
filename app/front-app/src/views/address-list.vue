<template>
  <div class="address-list-container">
    <!-- 头部 -->
    <div class="header">
      <div class="back-btn" @click="goBack">
        <span>←</span>
      </div>
      <div class="title">选择收货地址</div>
      <div class="add-btn" @click="addAddress">新增</div>
    </div>

    <!-- 地址列表 -->
    <div class="address-list" v-if="addressList.length > 0">
      <div 
        class="address-item" 
        v-for="address in addressList" 
        :key="address.id"
        :class="{ selected: selectedAddressId === address.id }"
        @click="selectAddress(address)"
      >
        <div class="address-content">
          <div class="receiver-info">
            <span class="receiver-name">{{ address.receiver_name }}</span>
            <span class="receiver-phone">{{ address.phone }}</span>
          </div>
          <div class="address-detail">{{ address.full_address }}</div>
        </div>
        <div class="address-actions">
          <div class="default-tag" v-if="address.is_default">默认</div>
          <div class="select-icon" v-if="selectedAddressId === address.id">✓</div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-else>
      <div class="empty-icon">📍</div>
      <div class="empty-text">暂无收货地址</div>
      <div class="empty-desc">请添加收货地址以便下单</div>
      <div class="add-address-btn" @click="addAddress">添加地址</div>
    </div>

    <!-- 底部确认按钮 -->
    <div class="bottom-bar" v-if="addressList.length > 0">
      <div class="confirm-btn" 
        @click="confirmAddress" 
        :class="{ disabled: !selectedAddressId }">
        确认选择
      </div>
    </div>
  </div>
</template>

<script>
import { getUserId } from '@/utils/auth.js'
import request from '../utils/request.js'
import AddressService from '../services/addressService.js'

export default {
  name: 'AddressList',
  data() {
    return {
      addressList: [],
      selectedAddressId: null,
      fromPage: ''
    }
  },
  mounted() {
    this.fromPage = this.$route.query.from || ''
    this.loadAddressList()
  },
  methods: {
    goBack() {
      this.$router.go(-1)
    },

    async loadAddressList() {
      try {
        const response = await request.get('/api/app/address/', {
          params: { user_id: getUserId() }
        })
        
        if (response.data.code === 200) {
          this.addressList = response.data.data
          // 优先勾选本地缓存的已选地址；不存在则回落到默认地址
          const cached = AddressService.getSelectedAddress()
          if (cached) {
            const exist = this.addressList.find(addr => String(addr.id) === String(cached.id))
            if (exist) {
              this.selectedAddressId = exist.id
            }
          }
          if (!this.selectedAddressId) {
            const defaultAddress = this.addressList.find(addr => addr.is_default)
            if (defaultAddress) {
              this.selectedAddressId = defaultAddress.id
            }
          }
        }
      } catch (error) {
        console.error('加载地址列表失败:', error)
      }
    },

    selectAddress(address) {
      this.selectedAddressId = address.id
      // 存储到本地
      AddressService.setSelectedAddress(address)
      // 若来自 checkout，选中即返回并回显
      if (this.fromPage === 'checkout' || this.fromPage === 'product-detail') {
        this.$router.go(-1)
      }
    },

    addAddress() {
      this.$router.push('/address')
    },

    confirmAddress() {
      if (!this.selectedAddressId) {
        alert('请选择收货地址')
        return
      }

      const selectedAddress = this.addressList.find(addr => addr.id === this.selectedAddressId)
      
      // 使用AddressService保存选中的地址
      AddressService.setSelectedAddress(selectedAddress)
      
      // 返回上一页
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.address-list-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 80px;
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

.back-btn {
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  flex: 1;
  text-align: center;
}

.add-btn {
  color: #ff4757;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
}

.address-list {
  padding: 10px;
}

.address-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.address-item:hover {
  border-color: #ff4757;
}

.address-item.selected {
  border-color: #ff4757;
  background-color: #fff5f5;
}

.address-content {
  flex: 1;
}

.receiver-info {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.receiver-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  margin-right: 10px;
}

.receiver-phone {
  font-size: 14px;
  color: #666;
}

.address-detail {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
}

.address-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}

.default-tag {
  background: #ff4757;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.select-icon {
  color: #ff4757;
  font-size: 18px;
  font-weight: bold;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.empty-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
}

.empty-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 30px;
}

.add-address-btn {
  background: #ff4757;
  color: white;
  padding: 12px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.add-address-btn:hover {
  background: #ff3742;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  z-index: 100;
}

.confirm-btn {
  background: #ff4757;
  color: white;
  padding: 12px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  text-align: center;
  transition: background-color 0.3s;
}

.confirm-btn:hover {
  background: #ff3742;
}

.confirm-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
}

.confirm-btn.disabled:hover {
  background: #ccc;
}
</style> 