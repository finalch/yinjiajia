<template>
  <div class="product-edit">
    <div class="page-header">
      <h1>编辑商品</h1>
      <div class="header-actions">
        <el-button @click="$router.back()">返回</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving">
          保存商品
        </el-button>
      </div>
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
              <el-select v-model="form.categoryId" placeholder="选择商品分类" style="width: 100%">
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
                :min="0" 
                :precision="2"
                style="width: 100%"
                placeholder="请输入商品价格"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存数量" prop="stock">
              <el-input-number 
                v-model="form.stock" 
                :min="0" 
                :precision="0"
                style="width: 100%"
                placeholder="请输入库存数量"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入商品描述"
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
              <el-icon size="48" color="#ddd"><Picture /></el-icon>
              <p>点击上传主图</p>
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
            class="images-upload"
            :action="uploadAction"
            list-type="picture-card"
            :on-success="handleImageSuccess"
            :on-remove="handleImageRemove"
            :before-upload="beforeImageUpload"
            :file-list="form.images"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
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
        
        <div v-for="(spec, index) in form.specifications" :key="index" class="specification-item">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item :label="`规格${index + 1}`" :prop="`specifications.${index}.name`">
                <el-input v-model="spec.name" placeholder="规格名称" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="规格值" :prop="`specifications.${index}.value`">
                <el-input v-model="spec.value" placeholder="规格值" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="价格调整">
                <el-input-number 
                  v-model="spec.priceAdjustment" 
                  :precision="2"
                  style="width: 100%"
                  placeholder="价格调整"
                />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="库存调整">
                <el-input-number 
                  v-model="spec.stockAdjustment" 
                  :precision="0"
                  style="width: 100%"
                  placeholder="库存调整"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-button 
            type="text" 
            @click="removeSpecification(index)"
            style="color: #f56c6c;"
          >
            删除规格
          </el-button>
        </div>
      </el-card>

      <!-- 商品详情 -->
      <el-card class="form-card">
        <template #header>
          <span>商品详情</span>
        </template>
        
        <el-form-item label="详情内容" prop="detail">
          <el-input
            v-model="form.detail"
            type="textarea"
            :rows="8"
            placeholder="请输入商品详情内容"
          />
        </el-form-item>
      </el-card>

      <!-- 销售设置 -->
      <el-card class="form-card">
        <template #header>
          <span>销售设置</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品状态" prop="status">
              <el-radio-group v-model="form.status">
                <el-radio label="active">上架</el-radio>
                <el-radio label="inactive">下架</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否推荐">
              <el-switch v-model="form.recommended" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排序权重" prop="sort">
              <el-input-number 
                v-model="form.sort" 
                :min="0" 
                :step="1"
                style="width: 100%"
                placeholder="排序权重"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="销量权重" prop="salesWeight">
              <el-input-number 
                v-model="form.salesWeight" 
                :min="0" 
                :step="1"
                style="width: 100%"
                placeholder="销量权重"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, Plus } from '@element-plus/icons-vue'

export default {
  name: 'ProductEdit',
  components: {
    Picture,
    Plus
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const formRef = ref()
    const saving = ref(false)
    
    // 商品分类
    const categories = ref([
      { id: 1, name: '手机数码' },
      { id: 2, name: '服装配饰' },
      { id: 3, name: '家居生活' },
      { id: 4, name: '美妆护肤' },
      { id: 5, name: '运动户外' }
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
      detail: '',
      status: 'active',
      recommended: false,
      sort: 0,
      salesWeight: 0
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入商品名称', trigger: 'blur' },
        { min: 2, max: 100, message: '商品名称长度在 2 到 100 个字符', trigger: 'blur' }
      ],
      categoryId: [
        { required: true, message: '请选择商品分类', trigger: 'change' }
      ],
      price: [
        { required: true, message: '请输入商品价格', trigger: 'blur' },
        { type: 'number', min: 0, message: '商品价格不能小于0', trigger: 'blur' }
      ],
      stock: [
        { required: true, message: '请输入库存数量', trigger: 'blur' },
        { type: 'number', min: 0, message: '库存数量不能小于0', trigger: 'blur' }
      ],
      description: [
        { required: true, message: '请输入商品描述', trigger: 'blur' },
        { max: 500, message: '商品描述不能超过500个字符', trigger: 'blur' }
      ],
      mainImage: [
        { required: true, message: '请上传商品主图', trigger: 'change' }
      ],
      detail: [
        { required: true, message: '请输入商品详情', trigger: 'blur' }
      ],
      status: [
        { required: true, message: '请选择商品状态', trigger: 'change' }
      ]
    }
    
    // 上传地址（模拟）
    const uploadAction = 'https://jsonplaceholder.typicode.com/posts/'
    
    // 方法
    const loadProductData = () => {
      const productId = route.params.id
      // 模拟加载商品数据
      form.name = 'Apple iPhone 15 Pro'
      form.categoryId = 1
      form.price = 7999
      form.stock = 100
      form.description = 'Apple iPhone 15 Pro，搭载A17 Pro芯片，配备48MP主摄，支持USB-C接口。'
      form.mainImage = 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      form.images = [
        {
          name: 'image1.jpg',
          url: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
        },
        {
          name: 'image2.jpg',
          url: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
        }
      ]
      form.specifications = [
        {
          name: '颜色',
          value: '暗紫色',
          priceAdjustment: 0,
          stockAdjustment: 0
        },
        {
          name: '存储',
          value: '256GB',
          priceAdjustment: 0,
          stockAdjustment: 0
        }
      ]
      form.detail = 'Apple iPhone 15 Pro 详细规格参数...'
      form.status = 'active'
      form.recommended = true
      form.sort = 1
      form.salesWeight = 100
    }
    
    const saveProduct = async () => {
      try {
        await formRef.value.validate()
        saving.value = true
        
        setTimeout(() => {
          ElMessage.success('商品保存成功')
          saving.value = false
          router.push('/products')
        }, 1000)
      } catch (error) {
        ElMessage.error('请完善商品信息')
      }
    }
    
    const beforeImageUpload = (file) => {
      const isImage = file.type.startsWith('image/')
      const isLt5M = file.size / 1024 / 1024 < 5
      
      if (!isImage) {
        ElMessage.error('只能上传图片文件!')
        return false
      }
      if (!isLt5M) {
        ElMessage.error('图片大小不能超过 5MB!')
        return false
      }
      return true
    }
    
    const handleMainImageSuccess = (response, file) => {
      // 模拟上传成功
      form.mainImage = URL.createObjectURL(file.raw)
      ElMessage.success('主图上传成功')
    }
    
    const removeMainImage = () => {
      form.mainImage = ''
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
    
    const addSpecification = () => {
      form.specifications.push({
        name: '',
        value: '',
        priceAdjustment: 0,
        stockAdjustment: 0
      })
    }
    
    const removeSpecification = (index) => {
      form.specifications.splice(index, 1)
    }
    
    // 页面加载时获取商品数据
    onMounted(() => {
      loadProductData()
    })
    
    return {
      formRef,
      saving,
      categories,
      form,
      rules,
      uploadAction,
      saveProduct,
      beforeImageUpload,
      handleMainImageSuccess,
      removeMainImage,
      handleImageSuccess,
      handleImageRemove,
      addSpecification,
      removeSpecification
    }
  }
}
</script>

<style scoped>
.product-edit {
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

.product-form {
  margin-bottom: 30px;
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

.images-upload {
  width: 100%;
}

.specification-item {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 15px;
  background-color: #fafafa;
}

.specification-item:last-child {
  margin-bottom: 0;
}
</style> 