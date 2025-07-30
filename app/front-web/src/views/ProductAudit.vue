<template>
  <div class="product-audit">
    <el-card class="audit-card">
      <template #header>
        <div class="card-header">
          <span>商品审核管理</span>
          <el-button type="primary" @click="refreshData">刷新数据</el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="商品名称">
            <el-input
              v-model="filterForm.name"
              placeholder="请输入商品名称"
              clearable
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="商品分类">
            <el-select
              v-model="filterForm.category_id"
              placeholder="请选择分类"
              clearable
            >
              <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="审核状态">
            <el-select
              v-model="filterForm.status"
              placeholder="请选择状态"
              clearable
            >
              <el-option label="待审核和审核失败" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="审核通过" value="approved" />
              <el-option label="审核拒绝" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 批量操作 -->
      <div class="batch-actions">
        <el-button
          type="success"
          :disabled="selectedProducts.length === 0"
          @click="batchApprove"
        >
          批量通过 ({{ selectedProducts.length }})
        </el-button>
        <el-button
          type="danger"
          :disabled="selectedProducts.length === 0"
          @click="batchReject"
        >
          批量拒绝 ({{ selectedProducts.length }})
        </el-button>
        <el-button @click="clearSelection">清空选择</el-button>
      </div>

      <!-- 商品列表 -->
      <el-table
        :data="products"
        v-loading="loading"
        @selection-change="handleSelectionChange"
        class="product-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="商品ID" width="80" />
        <el-table-column label="商品信息" min-width="300">
          <template #default="{ row }">
            <div class="product-info">
              <el-image
                :src="row.image_url || '/default-product.jpg'"
                :preview-src-list="[row.image_url]"
                class="product-image"
                fit="cover"
              />
              <div class="product-details">
                <div class="product-name">{{ row.name }}</div>
                <div class="product-category">{{ row.category_name }}</div>
                <div class="product-price">¥{{ row.price }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="auditProduct(row.id, 'approved')"
            >
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              size="small"
              @click="auditProduct(row.id, 'rejected')"
            >
              拒绝
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="viewProduct(row.id)"
            >
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="auditDialog.visible"
      :title="auditDialog.title"
      width="500px"
    >
      <el-form :model="auditForm" label-width="80px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="auditForm.status">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="rejected">拒绝</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="拒绝原因" v-if="auditForm.status === 'rejected'">
          <el-input
            v-model="auditForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
        <el-form-item label="审核备注">
          <el-input
            v-model="auditForm.note"
            type="textarea"
            :rows="3"
            placeholder="请输入审核备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="auditDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="confirmAudit">确认审核</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 商品详情对话框 -->
    <el-dialog
      v-model="productDialog.visible"
      title="商品详情"
      width="800px"
    >
      <div v-if="productDialog.product" class="product-detail">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-image
              :src="productDialog.product.image_url || '/default-product.jpg'"
              :preview-src-list="[productDialog.product.image_url]"
              class="detail-image"
              fit="cover"
            />
          </el-col>
          <el-col :span="12">
            <div class="detail-info">
              <h3>{{ productDialog.product.name }}</h3>
              <p><strong>分类：</strong>{{ productDialog.product.category_name }}</p>
              <p><strong>价格：</strong>¥{{ productDialog.product.price }}</p>
              <p><strong>库存：</strong>{{ productDialog.product.stock }}</p>
              <p><strong>状态：</strong>
                <el-tag :type="getStatusType(productDialog.product.status)">
                  {{ productDialog.product.status_text }}
                </el-tag>
              </p>
              <p><strong>创建时间：</strong>{{ productDialog.product.created_at }}</p>
              <p><strong>描述：</strong>{{ productDialog.product.description }}</p>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/api/request'

export default {
  name: 'ProductAudit',
  setup() {
    const loading = ref(false)
    const products = ref([])
    const categories = ref([])
    const selectedProducts = ref([])

    const pagination = reactive({
      page: 1,
      per_page: 10,
      total: 0,
      pages: 0
    })

    const filterForm = reactive({
      name: '',
      category_id: '',
      status: ''  // 默认为空，显示所有状态
    })

    const auditDialog = reactive({
      visible: false,
      title: '审核商品',
      productId: null
    })

    const auditForm = reactive({
      status: 'approved',
      reason: '',
      note: ''
    })

    const productDialog = reactive({
      visible: false,
      product: null
    })

    // 获取商品列表（包含待审核和审核失败的商品）
    const getProducts = async () => {
      loading.value = true
      try {
        const params = {
          merchant_id: 1, // 这里应该从用户信息中获取
          page: pagination.page,
          per_page: pagination.per_page
        }
        
        // 添加筛选条件
        if (filterForm.name) params.name = filterForm.name
        if (filterForm.category_id) params.category_id = filterForm.category_id
        if (filterForm.status) params.status = filterForm.status
        
        console.log('请求参数:', params)
        const response = await axios.get('/api/web/product/', { params })
        console.log('响应数据:', response.data)
        
        if (response.data.code === 200) {
          // 如果状态筛选为空，只显示待审核和审核失败的商品
          if (!filterForm.status) {
            products.value = response.data.data.list.filter(item => 
              item.status === 'pending' || item.status === 'rejected'
            )
            pagination.total = products.value.length
          } else {
            products.value = response.data.data.list
            pagination.total = response.data.data.pagination.total
          }
          pagination.pages = response.data.data.pagination.pages
        }
      } catch (error) {
        console.error('获取商品列表失败:', error)
        ElMessage.error('获取商品列表失败')
      } finally {
        loading.value = false
      }
    }

    // 获取分类列表
    const getCategories = async () => {
      try {
        const response = await axios.get('/api/web/categories', {
          params: { merchant_id: 1, status: 'active' }
        })
        
        if (response.data.code === 200) {
          categories.value = response.data.data.list
        }
      } catch (error) {
        console.error('获取分类列表失败:', error)
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      getProducts()
    }

    // 重置筛选
    const resetFilter = () => {
      Object.assign(filterForm, {
        name: '',
        category_id: '',
        status: ''
      })
      handleSearch()
    }

    // 分页处理
    const handleSizeChange = (size) => {
      pagination.per_page = size
      pagination.page = 1
      getProducts()
    }

    const handleCurrentChange = (page) => {
      pagination.page = page
      getProducts()
    }

    // 选择处理
    const handleSelectionChange = (selection) => {
      selectedProducts.value = selection
    }

    const clearSelection = () => {
      selectedProducts.value = []
    }

    // 单个审核
    const auditProduct = (productId, status) => {
      auditDialog.productId = productId
      auditForm.status = status
      auditForm.reason = ''
      auditForm.note = ''
      auditDialog.visible = true
    }

    // 确认审核
    const confirmAudit = async () => {
      try {
        const response = await axios.post(`/api/web/product/${auditDialog.productId}/audit`, {
          status: auditForm.status,
          reason: auditForm.reason,
          note: auditForm.note
        })
        
        if (response.data.code === 200) {
          ElMessage.success('审核成功')
          auditDialog.visible = false
          getProducts()
        }
      } catch (error) {
        ElMessage.error('审核失败')
        console.error(error)
      }
    }

    // 批量审核
    const batchAudit = async (status) => {
      if (selectedProducts.value.length === 0) {
        ElMessage.warning('请选择要审核的商品')
        return
      }

      try {
        const productIds = selectedProducts.value.map(item => item.id)
        const response = await axios.post('/api/web/product/batch-audit', {
          product_ids: productIds,
          status: status
        })
        
        if (response.data.code === 200) {
          ElMessage.success(`批量${status === 'approved' ? '通过' : '拒绝'}成功`)
          selectedProducts.value = []
          getProducts()
        }
      } catch (error) {
        ElMessage.error('批量审核失败')
        console.error(error)
      }
    }

    const batchApprove = () => {
      ElMessageBox.confirm('确定要批量通过选中的商品吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        batchAudit('approved')
      })
    }

    const batchReject = () => {
      ElMessageBox.confirm('确定要批量拒绝选中的商品吗？', '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        batchAudit('rejected')
      })
    }

    // 查看商品详情
    const viewProduct = async (productId) => {
      try {
        const response = await axios.get(`/api/web/product/${productId}`)
        
        if (response.data.code === 200) {
          productDialog.product = response.data.data
          productDialog.visible = true
        }
      } catch (error) {
        ElMessage.error('获取商品详情失败')
        console.error(error)
      }
    }

    // 获取状态类型
    const getStatusType = (status) => {
      const typeMap = {
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'on_sale': 'primary',
        'off_sale': 'info'
      }
      return typeMap[status] || 'info'
    }

    // 刷新数据
    const refreshData = () => {
      getProducts()
    }

    onMounted(() => {
      getProducts()
      getCategories()
    })

    return {
      loading,
      products,
      categories,
      selectedProducts,
      pagination,
      filterForm,
      auditDialog,
      auditForm,
      productDialog,
      handleSearch,
      resetFilter,
      handleSizeChange,
      handleCurrentChange,
      handleSelectionChange,
      clearSelection,
      auditProduct,
      confirmAudit,
      batchApprove,
      batchReject,
      viewProduct,
      getStatusType,
      refreshData
    }
  }
}
</script>

<style scoped>
.product-audit {
  padding: 20px;
}

.audit-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.batch-actions {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.product-table {
  margin-bottom: 20px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 10px;
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
  font-weight: bold;
  margin-bottom: 5px;
}

.product-category {
  font-size: 12px;
  color: #666;
  margin-bottom: 3px;
}

.product-price {
  font-size: 14px;
  color: #e6a23c;
  font-weight: bold;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.detail-image {
  width: 100%;
  max-height: 300px;
  border-radius: 8px;
}

.detail-info {
  padding: 0 20px;
}

.detail-info h3 {
  margin-bottom: 15px;
  color: #333;
}

.detail-info p {
  margin-bottom: 10px;
  line-height: 1.6;
}

.detail-info strong {
  color: #666;
}
</style> 