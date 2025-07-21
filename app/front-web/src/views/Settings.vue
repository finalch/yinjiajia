<template>
  <div class="settings">
    <div class="page-header">
      <h1>系统设置</h1>
    </div>

    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 基本设置 -->
      <el-tab-pane label="基本设置" name="basic">
        <el-card>
          <el-form :model="basicForm" :rules="basicRules" ref="basicFormRef" label-width="120px">
            <el-form-item label="店铺名称" prop="shopName">
              <el-input v-model="basicForm.shopName" placeholder="请输入店铺名称" />
            </el-form-item>
            <el-form-item label="店铺简介" prop="shopDescription">
              <el-input
                v-model="basicForm.shopDescription"
                type="textarea"
                :rows="3"
                placeholder="请输入店铺简介"
              />
            </el-form-item>
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="basicForm.phone" placeholder="请输入联系电话" />
            </el-form-item>
            <el-form-item label="联系邮箱" prop="email">
              <el-input v-model="basicForm.email" placeholder="请输入联系邮箱" />
            </el-form-item>
            <el-form-item label="店铺地址" prop="address">
              <el-input v-model="basicForm.address" placeholder="请输入店铺地址" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 安全设置 -->
      <el-tab-pane label="安全设置" name="security">
        <el-card>
          <el-form :model="securityForm" :rules="securityRules" ref="securityFormRef" label-width="120px">
            <el-form-item label="当前密码" prop="currentPassword">
              <el-input 
                v-model="securityForm.currentPassword" 
                type="password" 
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="securityForm.newPassword" 
                type="password" 
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="securityForm.confirmPassword" 
                type="password" 
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="changePassword">修改密码</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 通知设置 -->
      <el-tab-pane label="通知设置" name="notification">
        <el-card>
          <el-form :model="notificationForm" label-width="120px">
            <el-form-item label="订单通知">
              <el-switch v-model="notificationForm.orderNotification" />
              <span class="form-tip">新订单时发送通知</span>
            </el-form-item>
            <el-form-item label="库存预警">
              <el-switch v-model="notificationForm.stockWarning" />
              <span class="form-tip">库存不足时发送通知</span>
            </el-form-item>
            <el-form-item label="评价通知">
              <el-switch v-model="notificationForm.reviewNotification" />
              <span class="form-tip">收到新评价时发送通知</span>
            </el-form-item>
            <el-form-item label="系统通知">
              <el-switch v-model="notificationForm.systemNotification" />
              <span class="form-tip">系统维护等重要通知</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 关于我们 -->
      <el-tab-pane label="关于我们" name="about">
        <el-card>
          <div class="about-content">
            <div class="app-info">
              <h3>银家家商家后台管理系统</h3>
              <p>版本：v1.0.0</p>
              <p>更新时间：2024年1月15日</p>
            </div>
            <div class="contact-info">
              <h4>联系我们</h4>
              <p>客服电话：400-123-4567</p>
              <p>客服邮箱：support@yinjiajia.com</p>
              <p>官方网站：www.yinjiajia.com</p>
            </div>
            <div class="copyright">
              <p>© 2024 银家家科技有限公司 版权所有</p>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'Settings',
  setup() {
    const activeTab = ref('basic')
    const basicFormRef = ref()
    const securityFormRef = ref()
    
    // 基本设置表单
    const basicForm = reactive({
      shopName: '银家家数码专营店',
      shopDescription: '专业销售各类数码产品，品质保证，服务至上。',
      phone: '400-123-4567',
      email: 'contact@yinjiajia.com',
      address: '北京市朝阳区xxx街道xxx号'
    })
    
    const basicRules = {
      shopName: [
        { required: true, message: '请输入店铺名称', trigger: 'blur' }
      ],
      phone: [
        { required: true, message: '请输入联系电话', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入联系邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ]
    }
    
    // 安全设置表单
    const securityForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const securityRules = {
      currentPassword: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== securityForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
    
    // 通知设置表单
    const notificationForm = reactive({
      orderNotification: true,
      stockWarning: true,
      reviewNotification: true,
      systemNotification: true
    })
    
    // 方法
    const saveBasicSettings = async () => {
      try {
        await basicFormRef.value.validate()
        ElMessage.success('基本设置保存成功')
      } catch (error) {
        ElMessage.error('请完善基本信息')
      }
    }
    
    const changePassword = async () => {
      try {
        await securityFormRef.value.validate()
        ElMessage.success('密码修改成功')
        // 清空表单
        securityForm.currentPassword = ''
        securityForm.newPassword = ''
        securityForm.confirmPassword = ''
      } catch (error) {
        ElMessage.error('请完善密码信息')
      }
    }
    
    const saveNotificationSettings = () => {
      ElMessage.success('通知设置保存成功')
    }
    
    return {
      activeTab,
      basicFormRef,
      securityFormRef,
      basicForm,
      basicRules,
      securityForm,
      securityRules,
      notificationForm,
      saveBasicSettings,
      changePassword,
      saveNotificationSettings
    }
  }
}
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.settings-tabs {
  margin-bottom: 30px;
}

.form-tip {
  margin-left: 10px;
  color: #666;
  font-size: 0.9rem;
}

.about-content {
  padding: 20px 0;
}

.app-info {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.app-info h3 {
  color: #333;
  margin-bottom: 10px;
}

.app-info p {
  color: #666;
  margin-bottom: 5px;
}

.contact-info {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.contact-info h4 {
  color: #333;
  margin-bottom: 10px;
}

.contact-info p {
  color: #666;
  margin-bottom: 5px;
}

.copyright {
  text-align: center;
  color: #999;
}
</style> 