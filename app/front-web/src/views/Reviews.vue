<template>
  <div class="reviews">
    <div class="page-header">
      <h1>评价管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="exportReviews">
          <el-icon><Download /></el-icon>
          导出评价
        </el-button>
      </div>
    </div>

    <!-- 评价统计 -->
    <el-row :gutter="20" class="review-stats">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">总评价数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon positive">
              <el-icon size="24"><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.positive }}</div>
              <div class="stat-label">好评</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon neutral">
              <el-icon size="24"><InfoFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.neutral }}</div>
              <div class="stat-label">中评</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon negative">
              <el-icon size="24"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.negative }}</div>
              <div class="stat-label">差评</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 评分概览 -->
    <el-card class="rating-overview">
      <template #header>
        <span>评分概览</span>
      </template>
      
      <el-row :gutter="40">
        <el-col :span="8">
          <div class="overall-rating">
            <div class="rating-score">{{ overallRating }}</div>
            <div class="rating-stars">
              <el-rate v-model="overallRating" disabled show-score />
            </div>
            <div class="rating-text">综合评分</div>
          </div>
        </el-col>
        
        <el-col :span="16">
          <div class="rating-breakdown">
            <div 
              v-for="(count, stars) in ratingBreakdown" 
              :key="stars"
              class="rating-item"
            >
              <span class="stars">{{ stars }}星</span>
              <el-progress 
                :percentage="(count / stats.total) * 100" 
                :stroke-width="8"
                :show-text="false"
              />
              <span class="count">{{ count }}</span>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 筛选栏 -->
    <el-card class="filter-card">
      <el-form :model="filters" inline>
        <el-form-item label="商品名称">
          <el-input v-model="filters.productName" placeholder="请输入商品名称" clearable />
        </el-form-item>
        <el-form-item label="评价等级">
          <el-select v-model="filters.rating" placeholder="选择评价等级" clearable>
            <el-option label="5星" value="5" />
            <el-option label="4星" value="4" />
            <el-option label="3星" value="3" />
            <el-option label="2星" value="2" />
            <el-option label="1星" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="评价状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable>
            <el-option label="已回复" value="replied" />
            <el-option label="未回复" value="unreplied" />
            <el-option label="已隐藏" value="hidden" />
          </el-select>
        </el-form-item>
        <el-form-item label="评价时间">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 评价列表 -->
    <el-card>
      <el-table :data="reviews" v-loading="loading">
        <el-table-column label="商品信息" min-width="200">
          <template #default="{ row }">
            <div class="product-info">
              <el-image
                :src="row.productImage"
                class="product-image"
                fit="cover"
              />
              <div class="product-details">
                <h4 class="product-name">{{ row.productName }}</h4>
                <p class="product-specs">{{ row.productSpecs }}</p>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="评价内容" min-width="300">
          <template #default="{ row }">
            <div class="review-content">
              <div class="review-rating">
                <el-rate v-model="row.rating" disabled />
                <span class="rating-text">{{ row.rating }}星</span>
              </div>
              <div class="review-text">{{ row.content }}</div>
              <div class="review-images" v-if="row.images && row.images.length > 0">
                <el-image
                  v-for="image in row.images"
                  :key="image"
                  :src="image"
                  class="review-image"
                  fit="cover"
                  :preview-src-list="row.images"
                />
              </div>
              <div class="review-time">{{ row.createTime }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="买家信息" width="150">
          <template #default="{ row }">
            <div class="customer-info">
              <div class="customer-name">{{ row.customerName }}</div>
              <div class="customer-avatar">
                <el-avatar :src="row.customerAvatar" />
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="商家回复" min-width="200">
          <template #default="{ row }">
            <div class="merchant-reply" v-if="row.reply">
              <div class="reply-content">{{ row.reply.content }}</div>
              <div class="reply-time">{{ row.reply.time }}</div>
            </div>
            <div v-else class="no-reply">
              <el-button type="text" size="small" @click="showReplyDialog(row)">
                回复评价
              </el-button>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="text" size="small" @click="showReplyDialog(row)">
              {{ row.reply ? '修改回复' : '回复' }}
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="toggleReviewVisibility(row)"
            >
              {{ row.hidden ? '显示' : '隐藏' }}
            </el-button>
            <el-button 
              type="text" 
              size="small" 
              @click="deleteReview(row)"
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

    <!-- 回复对话框 -->
    <el-dialog
      v-model="replyDialogVisible"
      title="回复评价"
      width="600px"
    >
      <el-form :model="replyForm" :rules="replyRules" ref="replyFormRef" label-width="100px">
        <el-form-item label="评价内容">
          <div class="review-preview">
            <div class="review-rating">
              <el-rate v-model="selectedReview.rating" disabled />
              <span class="rating-text">{{ selectedReview.rating }}星</span>
            </div>
            <div class="review-text">{{ selectedReview.content }}</div>
          </div>
        </el-form-item>
        <el-form-item label="回复内容" prop="content">
          <el-input
            v-model="replyForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply" :loading="replying">
          确认回复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Download, 
  Document, 
  CircleCheck, 
  InfoFilled, 
  Warning 
} from '@element-plus/icons-vue'

export default {
  name: 'Reviews',
  components: {
    Download,
    Document,
    CircleCheck,
    InfoFilled,
    Warning
  },
  setup() {
    const loading = ref(false)
    const replyDialogVisible = ref(false)
    const replying = ref(false)
    const replyFormRef = ref()
    const selectedReview = ref({})
    
    // 统计数据
    const stats = ref({
      total: 156,
      positive: 128,
      neutral: 20,
      negative: 8
    })
    
    // 综合评分
    const overallRating = ref(4.2)
    
    // 评分分布
    const ratingBreakdown = ref({
      5: 85,
      4: 43,
      3: 20,
      2: 5,
      1: 3
    })
    
    // 筛选条件
    const filters = reactive({
      productName: '',
      rating: '',
      status: '',
      dateRange: []
    })
    
    // 分页
    const currentPage = ref(1)
    const pageSize = ref(20)
    const total = ref(156)
    
    // 回复表单
    const replyForm = reactive({
      content: ''
    })
    
    const replyRules = {
      content: [
        { required: true, message: '请输入回复内容', trigger: 'blur' },
        { min: 5, max: 500, message: '回复内容长度在 5 到 500 个字符', trigger: 'blur' }
      ]
    }
    
    // 评价列表
    const reviews = ref([
      {
        id: 1,
        productName: 'Apple iPhone 15 Pro',
        productSpecs: '暗紫色 256GB',
        productImage: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        rating: 5,
        content: '商品质量很好，包装也很精美，物流速度快，客服态度也很好，非常满意的一次购物体验！',
        images: [
          'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
          'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
        ],
        customerName: '张三',
        customerAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        createTime: '2024-01-15 14:30:00',
        reply: {
          content: '感谢您的好评！我们会继续努力提供更好的服务。',
          time: '2024-01-15 15:00:00'
        },
        hidden: false
      },
      {
        id: 2,
        productName: 'MacBook Pro 14英寸',
        productSpecs: 'M2 Pro芯片 16G 512G',
        productImage: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        rating: 4,
        content: '电脑性能不错，但是价格有点贵，希望能有更多优惠活动。',
        images: [],
        customerName: '李四',
        customerAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        createTime: '2024-01-14 16:20:00',
        reply: null,
        hidden: false
      },
      {
        id: 3,
        productName: 'AirPods Pro',
        productSpecs: '白色',
        productImage: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg',
        rating: 3,
        content: '音质一般，降噪效果没有宣传的那么好，有点失望。',
        images: [
          'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
        ],
        customerName: '王五',
        customerAvatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        createTime: '2024-01-13 10:15:00',
        reply: {
          content: '非常抱歉给您带来不好的体验，我们会认真改进产品质量。',
          time: '2024-01-13 11:00:00'
        },
        hidden: false
      }
    ])
    
    // 方法
    const handleSearch = () => {
      loading.value = true
      setTimeout(() => {
        loading.value = false
        ElMessage.success('搜索完成')
      }, 1000)
    }
    
    const resetFilters = () => {
      filters.productName = ''
      filters.rating = ''
      filters.status = ''
      filters.dateRange = []
      handleSearch()
    }
    
    const showReplyDialog = (review) => {
      selectedReview.value = review
      replyForm.content = review.reply?.content || ''
      replyDialogVisible.value = true
    }
    
    const submitReply = async () => {
      try {
        await replyFormRef.value.validate()
        replying.value = true
        
        setTimeout(() => {
          // 更新评价的回复
          selectedReview.value.reply = {
            content: replyForm.content,
            time: new Date().toLocaleString('zh-CN')
          }
          
          ElMessage.success('回复成功')
          replyDialogVisible.value = false
          replying.value = false
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善回复内容')
      }
    }
    
    const toggleReviewVisibility = async (review) => {
      const action = review.hidden ? '显示' : '隐藏'
      try {
        await ElMessageBox.confirm(`确定要${action}这条评价吗？`, '确认操作')
        review.hidden = !review.hidden
        ElMessage.success(`${action}成功`)
      } catch {
        // 用户取消
      }
    }
    
    const deleteReview = async (review) => {
      try {
        await ElMessageBox.confirm('确定要删除这条评价吗？此操作不可恢复！', '确认删除', {
          type: 'warning'
        })
        ElMessage.success('删除成功')
      } catch {
        // 用户取消
      }
    }
    
    const exportReviews = () => {
      ElMessage.success('评价导出功能开发中...')
    }
    
    const handleSizeChange = (val) => {
      pageSize.value = val
      // 重新加载数据
    }
    
    const handleCurrentChange = (val) => {
      currentPage.value = val
      // 重新加载数据
    }
    
    return {
      loading,
      replyDialogVisible,
      replying,
      replyFormRef,
      selectedReview,
      stats,
      overallRating,
      ratingBreakdown,
      filters,
      reviews,
      currentPage,
      pageSize,
      total,
      replyForm,
      replyRules,
      handleSearch,
      resetFilters,
      showReplyDialog,
      submitReply,
      toggleReviewVisibility,
      deleteReview,
      exportReviews,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.reviews {
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

.review-stats {
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

.stat-icon.positive {
  background-color: #f6ffed;
  color: #52c41a;
}

.stat-icon.neutral {
  background-color: #fff7e6;
  color: #fa8c16;
}

.stat-icon.negative {
  background-color: #fff2e8;
  color: #ff4d4f;
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

.rating-overview {
  margin-bottom: 20px;
}

.overall-rating {
  text-align: center;
}

.rating-score {
  font-size: 3rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.rating-stars {
  margin-bottom: 10px;
}

.rating-text {
  color: #666;
  font-size: 1rem;
}

.rating-breakdown {
  padding: 20px 0;
}

.rating-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-item .stars {
  width: 40px;
  color: #666;
  font-size: 0.9rem;
}

.rating-item .el-progress {
  flex: 1;
  margin: 0 15px;
}

.rating-item .count {
  width: 40px;
  text-align: right;
  color: #666;
  font-size: 0.9rem;
}

.filter-card {
  margin-bottom: 20px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-image {
  width: 50px;
  height: 50px;
  border-radius: 4px;
}

.product-details {
  flex: 1;
}

.product-name {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 0.9rem;
}

.product-specs {
  margin: 0;
  color: #666;
  font-size: 0.8rem;
}

.review-content {
  padding: 10px 0;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.rating-text {
  color: #666;
  font-size: 0.9rem;
}

.review-text {
  color: #333;
  line-height: 1.5;
  margin-bottom: 10px;
}

.review-images {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.review-image {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  cursor: pointer;
}

.review-time {
  color: #999;
  font-size: 0.8rem;
}

.customer-info {
  text-align: center;
}

.customer-name {
  margin-bottom: 10px;
  color: #333;
  font-weight: 500;
}

.merchant-reply {
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.reply-content {
  color: #333;
  line-height: 1.5;
  margin-bottom: 5px;
}

.reply-time {
  color: #999;
  font-size: 0.8rem;
}

.no-reply {
  color: #999;
  font-style: italic;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.review-preview {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 10px;
}
</style> 