<template>
  <div class="groups">
    <div class="page-header">
      <h1>商品分组</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加分组
        </el-button>
      </div>
    </div>

    <!-- 分组统计 -->
    <el-row :gutter="20" class="group-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon size="24"><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">总分类数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon active">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active }}</div>
              <div class="stat-label">启用分类</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon products">
              <el-icon size="24"><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.products }}</div>
              <div class="stat-label">商品总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sales">
              <el-icon size="24"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.sales }}</div>
              <div class="stat-label">今日销量</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 分组列表 -->
    <el-card>
      <el-table :data="groups" v-loading="loading" row-key="id">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="分组名称" min-width="150" />
        <el-table-column prop="description" label="分组描述" min-width="200" />
        <el-table-column prop="sort" label="排序" width="100" />
        <el-table-column prop="productCount" label="商品数量" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="editGroup(row)">
              编辑
            </el-button>
            <el-button 
              type="text" size="small" 
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteGroup(row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑分组对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingGroup ? '编辑分组' : '添加分组'"
      width="600px"
    >
      <el-form :model="groupForm" :rules="groupRules" ref="groupFormRef" label-width="100px">
        <el-form-item label="分组名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="分组描述" prop="description">
          <el-input
            v-model="groupForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分组描述"
          />
        </el-form-item>
        <el-form-item label="排序权重" prop="sort_order">
          <el-input-number 
            v-model="groupForm.sort_order" 
            :min="0" 
            :step="1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分组状态" prop="status">
          <el-radio-group v-model="groupForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分组图标">
          <el-upload
            class="icon-upload"
            :action="uploadAction"
            :show-file-list="false"
            :on-success="handleIconSuccess"
            :before-upload="beforeIconUpload"
          >
            <div class="upload-area" v-if="!groupForm.icon_url">
              <el-icon size="48" color="#ddd"><Picture /></el-icon>
              <p>点击上传图标</p>
            </div>
            <div class="icon-preview" v-else>
              <el-image :src="groupForm.icon_url" fit="cover" />
              <div class="icon-actions">
                <el-button type="text" @click="removeIcon">删除</el-button>
              </div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitGroup" :loading="submitting">
          {{ editingGroup ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Folder, 
  CircleCheck, 
  Goods, 
  TrendCharts, 
  Picture 
} from '@element-plus/icons-vue'
import request from '@/api/request'
import groupService from '../services/groupService'
import authService from '../services/authService'
// API基础URL已由全局request统一配置

export default {
  name: 'Groups',
  components: {
    Plus,
    Folder,
    CircleCheck,
    Goods,
    TrendCharts,
    Picture
  },
  setup() {
    const loading = ref(false)
    const dialogVisible = ref(false)
    const submitting = ref(false)
    const editingGroup = ref(false)
    const groupFormRef = ref()
    
    // 统计数据
    const stats = ref({
      total: 0,
      active: 0,
      products: 0,
      sales: 0
    })
    
    // 分组列表
    const groups = ref([])
    
    // 当前商家ID（实际项目中应该从登录状态获取）
    const currentMerchantId = computed(() => {
      const userInfo = authService.getUserInfo()
      return userInfo?.merchant_id || userInfo?.id
    })
    
    // 分组表单
    const groupForm = reactive({
      name: '',
      description: '',
      sort_order: 0,
      status: '',
      icon_url: ''
    })
    
    const groupRules = {
      name: [
        { required: true, message: '请输入分组名称', trigger: 'blur' },
        { min: 2, max: 20, message: '分组名称长度在 2 到 20 个字符', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入分组描述', trigger: 'blur' },
        { max: 200, message: '分组描述不能超过 200 个字符', trigger: 'blur' }
      ],
      sort_order: [
        { required: true, message: '请输入排序权重', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择分组状态', trigger: 'change' }
      ]
    }
    
    // 上传地址（模拟）
    const uploadAction = 'https://jsonplaceholder.typicode.com/posts/'
    
    // API方法
    const fetchGroups = async () => {
      try {
        loading.value = true
        
        // 使用 groupService 获取分组列表
        const result = await groupService.getGroups({
          merchant_id: currentMerchantId.value
        })
        
        if (result.success) {
          groups.value = result.data.map(item => ({
            id: item.id,
            name: item.name,
            description: item.description,
            sort: item.sort_order,
            productCount: item.product_count || 0,
            status: item.status,
            icon: item.icon_url,
            createTime: item.created_at
          }))
          
          // 更新统计数据
          stats.value.total = result.total
          stats.value.active = groups.value.filter(grp => grp.status === 'active').length
          stats.value.products = groups.value.reduce((sum, grp) => sum + grp.productCount, 0)
        } else {
          ElMessage.error(result.message || '获取分组列表失败')
        }
      } catch (error) {
        console.error('获取分组列表失败:', error)
        ElMessage.error('获取分组列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 方法
    const showAddDialog = () => {
      editingGroup.value = false
      groupForm.name = ''
      groupForm.description = ''
      groupForm.sort_order = 0
      groupForm.status = 'active'
      groupForm.icon_url = ''
      dialogVisible.value = true
    }
    
    const editGroup = (group) => {
      editingGroup.value = group.id
      groupForm.name = group.name
      groupForm.description = group.description
      groupForm.sort_order = group.sort
      groupForm.status = group.status
      groupForm.icon_url = group.icon
      dialogVisible.value = true
    }
    
    const submitGroup = async () => {
      try {
        await groupFormRef.value.validate()
        submitting.value = true
        
        const requestData = {
          name: groupForm.name,
          description: groupForm.description,
          sort_order: groupForm.sort_order,
          status: groupForm.status,
          icon_url: groupForm.icon_url,
          merchant_id: currentMerchantId.value
        }
        
        let result
        if (editingGroup.value) {
          // 更新分组
          result = await groupService.updateGroup(editingGroup.value, requestData)
        } else {
          // 创建分组
          result = await groupService.createGroup(requestData)
        }
        
        if (result.success) {
          ElMessage.success(result.message || (editingGroup.value ? '分组更新成功' : '分组添加成功'))
          dialogVisible.value = false
          fetchGroups() // 重新获取列表
        } else {
          ElMessage.error(result.message || '操作失败')
        }
      } catch (error) {
        console.error('提交分组失败:', error)
        ElMessage.error('操作失败')
      } finally {
        submitting.value = false
      }
    }
    
    const toggleStatus = async (group) => {
      const action = group.status === 'active' ? '禁用' : '启用'
      try {
        await ElMessageBox.confirm(`确定要${action}分组"${group.name}"吗？`, '确认操作')
        
        const result = await groupService.toggleGroupStatus(group.id, group.status === 'active' ? 'inactive' : 'active')
        
        if (result.success) {
          ElMessage.success(result.message || `${action}成功`)
          fetchGroups() // 重新获取列表
        } else {
          ElMessage.error(result.message || '操作失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('切换状态失败:', error)
          ElMessage.error('操作失败')
        }
      }
    }
    
    const deleteGroup = async (group) => {
      try {
        await ElMessageBox.confirm(`确定要删除分组"${group.name}"吗？此操作不可恢复！`, '确认删除', {
          type: 'warning'
        })
        
        const result = await groupService.deleteGroup(group.id)
        
        if (result.success) {
          ElMessage.success(result.message || '删除成功')
          fetchGroups() // 重新获取列表
        } else {
          ElMessage.error(result.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除分组失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }
    
    const beforeIconUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2
      
      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return false
      }
      if (!isLt2M) {
        ElMessage.error('图片大小不能超过 2MB!')
        return false
      }
      return true
    }
    
    const handleIconSuccess = (response, file) => {
      // 模拟上传成功
      groupForm.icon_url = URL.createObjectURL(file.raw)
      ElMessage.success('图标上传成功')
    }
    
    const removeIcon = () => {
      groupForm.icon_url = ''
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchGroups()
    })
    
    return {
      loading,
      dialogVisible,
      submitting,
      editingGroup,
      groupFormRef,
      stats,
      groups,
      groupForm,
      groupRules,
      uploadAction,
      fetchGroups,
      showAddDialog,
      editGroup,
      submitGroup,
      toggleStatus,
      deleteGroup,
      beforeIconUpload,
      handleIconSuccess,
      removeIcon
    }
  }
}
</script>

<style scoped>
.groups {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.group-stats {
  margin-bottom: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon.total {
  background-color: #e6f7ff;
  color: #1890ff;
}

.stat-icon.active {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.products {
  background-color: #fff7e6;
  color: #fa8c16;
}

.stat-icon.sales {
  background-color: #f9f0ff;
  color: #722ed1;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.icon-upload {
  width: 120px;
}

.upload-area {
  width: 120px;
  height: 120px;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-area p {
  margin: 10px 0 0 0;
  color: #666;
}

.icon-preview {
  position: relative;
  width: 120px;
  height: 120px;
}

.icon-preview .el-image {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

.icon-actions {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 6px;
}

.icon-preview:hover .icon-actions {
  opacity: 1;
}
</style> 