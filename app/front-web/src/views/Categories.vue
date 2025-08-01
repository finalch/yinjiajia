<template>
  <div class="categories">
    <div class="page-header">
      <h1>商品分类</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog">
          <el-icon><Plus /></el-icon>
          添加分类
        </el-button>
      </div>
    </div>

    <!-- 分类统计 -->
    <el-row :gutter="20" class="category-stats">
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

    <!-- 分类列表 -->
    <el-card>
      <el-table :data="categories" v-loading="loading" row-key="id">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="分类名称" min-width="150" />
        <el-table-column prop="description" label="分类描述" min-width="200" />
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
            <el-button type="text" size="small" @click="editCategory(row)">
              编辑
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteCategory(row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingCategory ? '编辑分类' : '添加分类'"
      width="600px"
    >
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        <el-form-item label="排序权重" prop="sort_order">
          <el-input-number 
            v-model="categoryForm.sort_order" 
            :min="0" 
            :step="1"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分类状态" prop="status">
          <el-radio-group v-model="categoryForm.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类图标">
          <el-upload
            class="icon-upload"
            :action="uploadAction"
            :show-file-list="false"
            :on-success="handleIconSuccess"
            :before-upload="beforeIconUpload"
          >
            <div class="upload-area" v-if="!categoryForm.icon_url">
              <el-icon size="48" color="#ddd"><Picture /></el-icon>
              <p>点击上传图标</p>
            </div>
            <div class="icon-preview" v-else>
              <el-image :src="categoryForm.icon_url" fit="cover" />
              <div class="icon-actions">
                <el-button type="text" @click="removeIcon">删除</el-button>
              </div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCategory" :loading="submitting">
          {{ editingCategory ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
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

// API基础URL已由全局request统一配置

export default {
  name: 'Categories',
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
    const editingCategory = ref(false)
    const categoryFormRef = ref()
    
    // 统计数据
    const stats = ref({
      total: 0,
      active: 0,
      products: 0,
      sales: 0
    })
    
    // 分类列表
    const categories = ref([])
    
    // 当前商家ID（实际项目中应该从登录状态获取）
    const currentMerchantId = 1
    
    // 分类表单
    const categoryForm = reactive({
      name: '',
      description: '',
      sort_order: 0,
      status: 'active',
      icon_url: ''
    })
    
    const categoryRules = {
      name: [
        { required: true, message: '请输入分类名称', trigger: 'blur' },
        { min: 2, max: 20, message: '分类名称长度在 2 到 20 个字符', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入分类描述', trigger: 'blur' },
        { max: 200, message: '分类描述不能超过 200 个字符', trigger: 'blur' }
      ],
      sort_order: [
        { required: true, message: '请输入排序权重', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择分类状态', trigger: 'change' }
      ]
    }
    
    // 上传地址（模拟）
    const uploadAction = 'https://jsonplaceholder.typicode.com/posts/'
    
    // API方法
    const fetchCategories = async () => {
      try {
        loading.value = true
        const response = await request.get('/api/web/categories', {
          params: {
            merchant_id: currentMerchantId
          }
        })
        
        if (response.data.code === 200) {
          categories.value = response.data.data.list.map(item => ({
            id: item.id,
            name: item.name,
            description: item.description,
            sort: item.sort_order,
            productCount: item.product_count,
            status: item.status,
            icon: item.icon_url,
            createTime: item.created_at
          }))
          
          // 更新统计数据
          stats.value.total = response.data.data.pagination.total
          stats.value.active = categories.value.filter(cat => cat.status === 'active').length
          stats.value.products = categories.value.reduce((sum, cat) => sum + cat.productCount, 0)
        }
      } catch (error) {
        console.error('获取分类列表失败:', error)
        ElMessage.error('获取分类列表失败')
      } finally {
        loading.value = false
      }
    }
    
    // 方法
    const showAddDialog = () => {
      editingCategory.value = false
      categoryForm.name = ''
      categoryForm.description = ''
      categoryForm.sort_order = 0
      categoryForm.status = 'active'
      categoryForm.icon_url = ''
      dialogVisible.value = true
    }
    
    const editCategory = (category) => {
      editingCategory.value = category.id
      categoryForm.name = category.name
      categoryForm.description = category.description
      categoryForm.sort_order = category.sort
      categoryForm.status = category.status
      categoryForm.icon_url = category.icon
      dialogVisible.value = true
    }
    
    const submitCategory = async () => {
      try {
        await categoryFormRef.value.validate()
        submitting.value = true
        
        const requestData = {
          name: categoryForm.name,
          description: categoryForm.description,
          sort_order: categoryForm.sort_order,
          status: categoryForm.status,
          icon_url: categoryForm.icon_url,
          merchant_id: currentMerchantId
        }
        
        let response
        if (editingCategory.value) {
          // 更新分类
          response = await request.put(`/categories/${editingCategory.value}`, requestData)
        } else {
          // 创建分类
          response = await request.post('/categories', requestData)
        }
        
        if (response.data.code === 200) {
          ElMessage.success(editingCategory.value ? '分类更新成功' : '分类添加成功')
          dialogVisible.value = false
          fetchCategories() // 重新获取列表
        } else {
          ElMessage.error(response.data.message || '操作失败')
        }
      } catch (error) {
        console.error('提交分类失败:', error)
        ElMessage.error(error.response?.data?.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
    
    const toggleStatus = async (category) => {
      const action = category.status === 'active' ? '禁用' : '启用'
      try {
        await ElMessageBox.confirm(`确定要${action}分类"${category.name}"吗？`, '确认操作')
        
        const response = await request.put(`/categories/${category.id}`, {
          status: category.status === 'active' ? 'inactive' : 'active'
        })
        
        if (response.data.code === 200) {
          ElMessage.success(`${action}成功`)
          fetchCategories() // 重新获取列表
        } else {
          ElMessage.error(response.data.message || '操作失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('切换状态失败:', error)
          ElMessage.error(error.response?.data?.message || '操作失败')
        }
      }
    }
    
    const deleteCategory = async (category) => {
      try {
        await ElMessageBox.confirm(`确定要删除分类"${category.name}"吗？此操作不可恢复！`, '确认删除', {
          type: 'warning'
        })
        
        const response = await request.delete(`/categories/${category.id}`)
        
        if (response.data.code === 200) {
          ElMessage.success('删除成功')
          fetchCategories() // 重新获取列表
        } else {
          ElMessage.error(response.data.message || '删除失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除分类失败:', error)
          ElMessage.error(error.response?.data?.message || '删除失败')
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
      categoryForm.icon_url = URL.createObjectURL(file.raw)
      ElMessage.success('图标上传成功')
    }
    
    const removeIcon = () => {
      categoryForm.icon_url = ''
    }
    
    // 生命周期钩子
    onMounted(() => {
      fetchCategories()
    })
    
    return {
      loading,
      dialogVisible,
      submitting,
      editingCategory,
      categoryFormRef,
      stats,
      categories,
      categoryForm,
      categoryRules,
      uploadAction,
      fetchCategories,
      showAddDialog,
      editCategory,
      submitCategory,
      toggleStatus,
      deleteCategory,
      beforeIconUpload,
      handleIconSuccess,
      removeIcon
    }
  }
}
</script>

<style scoped>
.categories {
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

.category-stats {
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