<template>
  <div class="product-add">
    <div class="page-header">
      <h1>发布商品</h1>
      <el-button @click="$router.back()">返回</el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      class="product-form"
    >
      <!-- 基本信息 -->
      <el-card class="form-card">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入商品名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品分类" prop="categoryId">
              <el-select v-model="form.categoryId" placeholder="选择商品分类">
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品价格" prop="price">
              <el-input-number 
                v-model="form.price" 
                :precision="2" 
                :min="0" 
                :step="0.01"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品库存" prop="stock">
              <el-input-number 
                v-model="form.stock" 
                :min="0" 
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商品详细描述"
          />
        </el-form-item>
      </el-card>

      <!-- 商品图片 -->
      <el-card class="form-card">
        <template #header>
          <span>商品图片</span>
        </template>
        
        <el-form-item label="主图" prop="mainImage">
          <el-upload
            class="image-upload"
            :action="uploadAction"
            :show-file-list="false"
            :on-success="handleMainImageSuccess"
            :before-upload="beforeImageUpload"
          >
            <div class="upload-area" v-if="!form.mainImage">
              <el-icon size="48" color="#ddd"><Plus /></el-icon>
              <p>点击上传主图</p>
              <p class="upload-tip">建议尺寸：800x800px，大小不超过2MB</p>
            </div>
            <div class="image-preview" v-else>
              <el-image :src="form.mainImage" fit="cover" />
              <div class="image-actions">
                <el-button type="text" @click="removeMainImage">删除</el-button>
              </div>
            </div>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="商品图片">
          <el-upload
            class="image-list-upload"
            :action="uploadAction"
            list-type="picture-card"
            :on-success="handleImageSuccess"
            :on-remove="handleImageRemove"
            :before-upload="beforeImageUpload"
            :file-list="form.images"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <p class="upload-tip">最多上传9张图片，建议尺寸：800x800px</p>
        </el-form-item>
      </el-card>

      <!-- 商品规格 -->
      <el-card class="form-card">
        <template #header>
          <span>商品规格</span>
          <el-button type="text" @click="addSpecification" style="float: right;">
            <el-icon><Plus /></el-icon>
            添加规格
          </el-button>
        </template>
        
        <div v-if="form.specifications.length === 0" class="no-specs">
          <p>暂无规格，点击上方按钮添加规格</p>
        </div>
        
        <div v-else class="specifications">
          <div 
            v-for="(spec, index) in form.specifications" 
            :key="index"
            class="specification-item"
          >
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item :label="`规格${index + 1}名称`">
                  <el-input v-model="spec.name" placeholder="如：颜色、尺码" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="规格值">
                  <el-input 
                    v-model="spec.values" 
                    placeholder="多个值用逗号分隔，如：红色,蓝色,绿色"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-button 
                  type="danger" 
                  @click="removeSpecification(index)"
                  style="margin-top: 32px;"
                >
                  删除规格
                </el-button>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-card>

      <!-- 规格组合 -->
      <el-card class="form-card" v-if="form.specifications.length > 0">
        <template #header>
          <span>规格组合</span>
        </template>
        
        <el-table :data="specCombinations" border>
          <el-table-column 
            v-for="spec in form.specifications" 
            :key="spec.name"
            :label="spec.name"
            :prop="spec.name"
          />
          <el-table-column label="价格" width="150">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.price" 
                :precision="2" 
                :min="0" 
                :step="0.01"
                size="small"
              />
            </template>
          </el-table-column>
          <el-table-column label="库存" width="150">
            <template #default="{ row }">
              <el-input-number 
                v-model="row.stock" 
                :min="0" 
                :step="1"
                size="small"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 其他设置 -->
      <el-card class="form-card">
        <template #header>
          <span>其他设置</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品重量(kg)">
              <el-input-number 
                v-model="form.weight" 
                :precision="2" 
                :min="0" 
                :step="0.01"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品品牌">
              <el-input v-model="form.brand" placeholder="请输入商品品牌" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否上架">
              <el-switch v-model="form.isOnSale" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序权重">
              <el-input-number 
                v-model="form.sort" 
                :min="0" 
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <el-button @click="$router.back()">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          发布商品
        </el-button>
        <el-button @click="saveDraft" :loading="saving">
          保存草稿
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'ProductAdd',
  components: {
    Plus
  },
  setup() {
    const router = useRouter()
    const formRef = ref()
    const submitting = ref(false)
    const saving = ref(false)
    
    // 上传地址（模拟）
    const uploadAction = 'https://jsonplaceholder.typicode.com/posts/'
    
    // 商品分类
    const categories = ref([
      { id: 1, name: '手机数码' },
      { id: 2, name: '服装配饰' },
      { id: 3, name: '家居生活' },
      { id: 4, name: '美妆护肤' }
    ])
    
    // 表单数据
    const form = reactive({
      name: '',
      categoryId: '',
      price: 0,
      stock: 0,
      description: '',
      mainImage: '',
      images: [],
      specifications: [],
      weight: 0,
      brand: '',
      isOnSale: true,
      sort: 0
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入商品名称', trigger: 'blur' }
      ],
      categoryId: [
        { required: true, message: '请选择商品分类', trigger: 'change' }
      ],
      price: [
        { required: true, message: '请输入商品价格', trigger: 'blur' }
      ],
      stock: [
        { required: true, message: '请输入商品库存', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入商品描述', trigger: 'blur' }
      ],
      mainImage: [
        { required: true, message: '请上传商品主图', trigger: 'change' }
      ]
    }
    
    // 规格组合
    const specCombinations = computed(() => {
      if (form.specifications.length === 0) return []
      
      // 生成规格组合
      const combinations = []
      const specs = form.specifications.map(spec => 
        spec.values.split(',').map(v => v.trim()).filter(v => v)
      )
      
      const generateCombinations = (current, index) => {
        if (index === specs.length) {
          combinations.push({
            ...Object.fromEntries(current.map((value, i) => [form.specifications[i].name, value])),
            price: form.price,
            stock: form.stock
          })
          return
        }
        
        for (const value of specs[index]) {
          generateCombinations([...current, value], index + 1)
        }
      }
      
      generateCombinations([], 0)
      return combinations
    })
    
    // 方法
    const addSpecification = () => {
      form.specifications.push({
        name: '',
        values: ''
      })
    }
    
    const removeSpecification = (index) => {
      form.specifications.splice(index, 1)
    }
    
    const beforeImageUpload = (file) => {
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
    
    const handleMainImageSuccess = (response, file) => {
      // 模拟上传成功
      form.mainImage = URL.createObjectURL(file.raw)
      ElMessage.success('主图上传成功')
    }
    
    const handleImageSuccess = (response, file) => {
      // 模拟上传成功
      const imageUrl = URL.createObjectURL(file.raw)
      form.images.push({
        name: file.name,
        url: imageUrl
      })
      ElMessage.success('图片上传成功')
    }
    
    const handleImageRemove = (file, fileList) => {
      form.images = fileList
    }
    
    const removeMainImage = () => {
      form.mainImage = ''
    }
    
    const submitForm = async () => {
      try {
        await formRef.value.validate()
        submitting.value = true
        
        // 模拟提交
        setTimeout(() => {
          ElMessage.success('商品发布成功')
          router.push('/products')
        }, 2000)
      } catch (error) {
        ElMessage.error('请完善商品信息')
      } finally {
        submitting.value = false
      }
    }
    
    const saveDraft = () => {
      saving.value = true
      setTimeout(() => {
        ElMessage.success('草稿保存成功')
        saving.value = false
      }, 1000)
    }
    
    return {
      formRef,
      form,
      rules,
      categories,
      uploadAction,
      submitting,
      saving,
      specCombinations,
      addSpecification,
      removeSpecification,
      beforeImageUpload,
      handleMainImageSuccess,
      handleImageSuccess,
      handleImageRemove,
      removeMainImage,
      submitForm,
      saveDraft
    }
  }
}
</script>

<style scoped>
.product-add {
  max-width: 1000px;
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

.form-card {
  margin-bottom: 20px;
}

.image-upload {
  width: 200px;
}

.upload-area {
  width: 200px;
  height: 200px;
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

.upload-tip {
  font-size: 0.8rem;
  color: #999;
  margin: 5px 0 0 0;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 200px;
}

.image-preview .el-image {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

.image-actions {
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

.image-preview:hover .image-actions {
  opacity: 1;
}

.no-specs {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.specification-item {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
}

.form-actions {
  text-align: center;
  margin-top: 30px;
  padding: 20px 0;
  border-top: 1px solid #f0f0f0;
}

.form-actions .el-button {
  margin: 0 10px;
}
</style> 