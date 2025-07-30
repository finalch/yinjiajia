<template>
  <div class="products">
    <div class="page-header">
      <h1>商品管理</h1>
      <el-button type="primary" @click="$router.push('/products/add')">
        <el-icon><Plus /></el-icon>
        发布商品
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="商品名称">
          <el-input v-model="filters.name" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item label="商品分类">
          <el-select v-model="filters.category" placeholder="选择分类" clearable>
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="商品状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 批量操作 -->
    <el-card class="batch-card">
      <div class="batch-actions">
        <el-checkbox v-model="selectAll" @change="handleSelectAll">全选</el-checkbox>
        <el-button 
          type="primary" 
          size="small" 
          :disabled="!hasSelected"
          @click="batchOnSale"
        >
          批量上架
        </el-button>
        <el-button 
          type="warning" 
          size="small" 
          :disabled="!hasSelected"
          @click="batchOffSale"
        >
          批量下架
        </el-button>
        <el-button 
          type="danger" 
          size="small" 
          :disabled="!hasSelected"
          @click="batchDelete"
        >
          批量删除
        </el-button>
        <span class="selected-count" v-if="hasSelected">
          已选择 {{ selectedCount }} 件商品
        </span>
      </div>
    </el-card>

    <!-- 商品列表 -->
    <el-card>
      <el-table
        :data="products"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="商品信息" min-width="300">
          <template #default="{ row }">
            <div class="product-info">
              <el-image
                :src="row.image"
                class="product-image"
                fit="cover"
              />
              <div class="product-details">
                <h4 class="product-name">{{ row.name }}</h4>
                <p class="product-specs">{{ row.specs }}</p>
                <p class="product-category">{{ row.categoryName }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="120">
          <template #default="{ row }">
            <span class="price">¥{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="100" />
        <el-table-column prop="sales" label="销量" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.statusText }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="editProduct(row)">
              编辑
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleStatus(row)"
              v-if="row.status === 'on_sale'"
            >
              下架
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleStatus(row)"
              v-else-if="row.status === 'approved' || row.status === 'off_sale'"
            >
              上架
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="viewProduct(row)"
            >
              预览
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteProduct(row)"
              style="color: #f56c6c;"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from '@/api/request'
import dayjs from 'dayjs'

export default {
  name: 'Products',
  components: {
    Plus
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const selectAll = ref(false)
    const selectedProducts = ref([])
    
    // 筛选条件
    const filters = reactive({
      name: '',
      category: '',
      status: ''  // 默认为空，显示所有状态
    })
    
    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(156)
    
    // 商品分类
    const categories = ref([])
    
    // 商品列表
    const products = ref([])
    
    // 商品状态映射
    const statusOptions = [
      { label: '全部', value: '' },
      { label: '审核中', value: 'pending' },
      { label: '审核通过', value: 'approved' },
      { label: '已上架', value: 'on_sale' },
      { label: '已下架', value: 'off_sale' },
      { label: '审核失败', value: 'rejected' }
    ]
    
    // 计算属性
    const hasSelected = computed(() => selectedProducts.value.length > 0)
    const selectedCount = computed(() => selectedProducts.value.length)
    
    // 获取商品列表
    const fetchProducts = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          per_page: pageSize.value
        }
        if (filters.name) params.name = filters.name
        if (filters.category) params.category_id = filters.category
        if (filters.status) params.status = filters.status
        params.merchant_id = 1 // 示例

        const res = await axios.get('/api/web/product/', { params })
        
        if (res.data.code === 200) {
          // 适配后端返回数据到前端表格字段
          products.value = (res.data.data.list || []).map(item => ({
            id: item.id,
            name: item.name,
            specs: '',
            categoryName: item.category_name || '',
            price: item.price,
            stock: item.stock,
            sales: 0,
            status: item.status,
            statusText: item.status_text || getStatusText(item.status), // 使用后端返回的状态文本
            image: item.image_url,
            createTime: item.created_at || ''
          }))
          total.value = res.data.data.pagination.total
        } else {
          products.value = []
          total.value = 0
        }
      } catch (e) {
        console.error('获取商品列表失败:', e)
        products.value = []
        total.value = 0
        ElMessage.error('获取商品列表失败')
      } finally {
        loading.value = false
      }
    }
    // 获取分类列表
    const fetchCategories = async () => {
      try {
        const res = await axios.get('/api/web/categories?merchant_id=1&status=active')
        if (res.data.code === 200) {
          categories.value = res.data.data.list || []
        } else {
          categories.value = []
        }
      } catch (e) {
        console.error('获取分类列表失败:', e)
        categories.value = []
      }
    }
    // 页面加载时获取数据
    fetchProducts()
    fetchCategories()
    
    // 方法
    const handleSearch = () => {
      fetchProducts()
      ElMessage.success('搜索完成')
    }
    
    const resetFilters = () => {
      filters.name = ''
      filters.category = ''
      filters.status = ''
      handleSearch()
    }
    
    const handleSelectAll = (val) => {
      if (val) {
        selectedProducts.value = products.value.map(item => item.id)
      } else {
        selectedProducts.value = []
      }
    }
    
    const handleSelectionChange = (selection) => {
      selectedProducts.value = selection.map(item => item.id)
      selectAll.value = selection.length === products.value.length
    }
    
    const batchOnSale = async () => {
      try {
        await ElMessageBox.confirm('确定要批量上架选中的商品吗？', '提示')
        
        const productIds = selectedProducts.value
        const response = await axios.post('/api/web/product/batch-toggle-status', {
          product_ids: productIds,
          status: 'on_sale'
        })
        
        if (response.data.code === 200) {
          ElMessage.success(`批量上架成功，成功${response.data.data.updated_count}个，失败${response.data.data.failed_count}个`)
          selectedProducts.value = []
          fetchProducts() // 刷新列表
        } else {
          ElMessage.error(response.data.message || '批量上架失败')
        }
      } catch (error) {
        if (error.message !== 'cancel') {
          console.error('批量上架失败:', error)
          ElMessage.error('批量上架失败')
        }
      }
    }
    
    const batchOffSale = async () => {
      try {
        await ElMessageBox.confirm('确定要批量下架选中的商品吗？', '提示')
        
        const productIds = selectedProducts.value
        const response = await axios.post('/api/web/product/batch-toggle-status', {
          product_ids: productIds,
          status: 'off_sale'
        })
        
        if (response.data.code === 200) {
          ElMessage.success(`批量下架成功，成功${response.data.data.updated_count}个，失败${response.data.data.failed_count}个`)
          selectedProducts.value = []
          fetchProducts() // 刷新列表
        } else {
          ElMessage.error(response.data.message || '批量下架失败')
        }
      } catch (error) {
        if (error.message !== 'cancel') {
          console.error('批量下架失败:', error)
          ElMessage.error('批量下架失败')
        }
      }
    }
    
    const batchDelete = async () => {
      try {
        await ElMessageBox.confirm('确定要批量删除选中的商品吗？此操作不可恢复！', '警告', {
          type: 'warning'
        })
        
        // 批量删除需要逐个调用删除API
        const productIds = selectedProducts.value
        let successCount = 0
        let failCount = 0
        
        for (const productId of productIds) {
          try {
            const response = await axios.delete(`/api/web/product/${productId}`)
            if (response.data.code === 200) {
              successCount++
            } else {
              failCount++
            }
          } catch (error) {
            failCount++
          }
        }
        
        ElMessage.success(`批量删除完成，成功${successCount}个，失败${failCount}个`)
        selectedProducts.value = []
        fetchProducts() // 刷新列表
      } catch (error) {
        if (error.message !== 'cancel') {
          console.error('批量删除失败:', error)
          ElMessage.error('批量删除失败')
        }
      }
    }
    
    const getStatusType = (status) => {
      const types = {
        on_sale: 'success',
        off_sale: 'info',
        pending: 'warning',
        approved: 'success',
        rejected: 'danger'
      }
      return types[status] || 'info'
    }
    
    const getStatusText = (status) => {
      const texts = {
        pending: '审核中',
        approved: '审核通过',
        on_sale: '已上架',
        off_sale: '已下架',
        rejected: '审核失败'
      }
      return texts[status] || '未知'
    }
    
    const editProduct = (product) => {
      router.push(`/products/edit/${product.id}`)
    }
    
    const toggleStatus = async (product) => {
      try {
        const newStatus = product.status === 'on_sale' ? 'off_sale' : 'on_sale'
        const action = product.status === 'on_sale' ? '下架' : '上架'
        
        // 只有审核通过的商品才能上架
        if (newStatus === 'on_sale' && product.status !== 'approved') {
          ElMessage.warning('只有审核通过的商品才能上架')
          return
        }
        
        const response = await axios.post(`/api/web/product/${product.id}/toggle-status`, {
          status: newStatus
        })
        
        if (response.data.code === 200) {
          ElMessage.success(`${action}成功`)
          fetchProducts() // 刷新列表
        } else {
          ElMessage.error(response.data.message || `${action}失败`)
        }
      } catch (error) {
        console.error('切换状态失败:', error)
        ElMessage.error('操作失败')
      }
    }
    
    const viewProduct = (product) => {
      ElMessage.info('商品预览功能开发中...')
    }
    
    const deleteProduct = async (product) => {
      try {
        await ElMessageBox.confirm(`确定要删除商品"${product.name}"吗？`, '警告', {
          type: 'warning'
        })
        
        const response = await axios.delete(`/api/web/product/${product.id}`)
        
        if (response.data.code === 200) {
          ElMessage.success('删除成功')
          fetchProducts() // 刷新列表
        } else {
          ElMessage.error(response.data.message || '删除失败')
        }
      } catch (error) {
        if (error.message !== 'cancel') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }
    
    const handleSizeChange = (val) => {
      pageSize.value = val
      currentPage.value = 1
      fetchProducts()
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
      fetchProducts()
    }
    
    return {
      loading,
      filters,
      categories,
      products,
      selectAll,
      selectedProducts,
      currentPage,
      pageSize,
      total,
      hasSelected,
      selectedCount,
      handleSearch,
      resetFilters,
      handleSelectAll,
      handleSelectionChange,
      batchOnSale,
      batchOffSale,
      batchDelete,
      getStatusType,
      getStatusText,
      editProduct,
      toggleStatus,
      viewProduct,
      deleteProduct,
      handleSizeChange,
      handleCurrentChange,
      fetchProducts,
      fetchCategories,
      statusOptions
    }
  }
}
</script>

<style scoped>
.products {
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

.filter-card {
  margin-bottom: 20px;
}

.batch-card {
  margin-bottom: 20px;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.selected-count {
  color: #666;
  font-size: 0.9rem;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.product-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
}

.product-details {
  flex: 1;
}

.product-name {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1rem;
}

.product-specs {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.product-category {
  margin: 0;
  color: #999;
  font-size: 0.8rem;
}

.price {
  color: #e74c3c;
  font-weight: bold;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}
</style> 