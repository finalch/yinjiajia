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
        

        
        <!-- 无规格时的基础价格和库存 -->
        <!-- <template v-if="!form.hasSpecs">
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
        </template> -->
        <el-form-item label="商品描述" prop="description">
          <el-input v-model="form.description" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品详情" prop="detail">
          <div class="rich-editor-container">
            <Toolbar
              style="border-bottom: 1px solid #ccc"
              :editor="editorRef"
              :defaultConfig="toolbarConfig"
              :mode="mode"
            />
            <Editor
              style="height: 400px; overflow-y: hidden;"
              v-model="form.detail"
              :defaultConfig="editorConfig"
              :mode="mode"
              @onCreated="handleCreated"
            />
          </div>
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
            :limit="9"
          >
            <el-icon><Plus /></el-icon>
            <template #tip>
              <div class="el-upload__tip">
                最多上传9张图片，每张不超过5MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="商品视频">
          <el-upload
            class="video-upload"
            :action="uploadAction"
            list-type="text"
            :on-success="handleVideoSuccess"
            :on-remove="handleVideoRemove"
            :before-upload="beforeVideoUpload"
            :file-list="form.videos"
            accept="video/*"
            :limit="1"
          >
            <el-button type="primary">上传视频</el-button>
            <template #tip>
              <div class="el-upload__tip">
                最多上传1个视频，大小不超过100MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-card>



      <!-- 规格设置 -->
      <el-card class="form-card">
        <template #header>
          <span>规格设置</span>
        </template>
        
        <el-form-item label="是否多规格">
          <el-switch v-model="form.hasSpecs" />
          <span style="margin-left: 10px; color: #666;">开启后可以设置多种规格（如颜色、尺寸等）</span>
        </el-form-item>
        
        <!-- 规格类型管理 -->
        <el-form-item label="规格类型" v-if="form.hasSpecs">
          <div class="spec-types">
            <div v-for="(spec, index) in form.specs" :key="index" class="spec-type-item">
              <el-input v-model="spec.name" placeholder="规格名称（如：颜色）" style="width: 200px;" />
              <el-input v-model="spec.values" placeholder="规格值，用逗号分隔（如：红色,蓝色,绿色）" style="width: 300px; margin-left: 10px;" />
              <el-input-number v-model="spec.sort_order" :min="0" placeholder="排序" style="width: 100px; margin-left: 10px;" />
              <el-button type="danger" size="small" @click="removeSpec(index)" style="margin-left: 10px;">删除</el-button>
            </div>
            <el-button type="primary" @click="addSpec">添加规格类型</el-button>
          </div>
        </el-form-item>
        
        <!-- 规格组合管理 -->
        <el-form-item label="规格组合" v-if="form.hasSpecs">
          <div class="spec-combinations">
            <div v-for="(combo, index) in form.specCombinations" :key="index" class="spec-combo-item">
              <div class="combo-header">
                <span class="combo-title">组合 {{ index + 1 }}</span>
                <el-button type="danger" size="small" @click="removeSpecCombination(index)">删除</el-button>
              </div>
              
              <div class="combo-content">
                <!-- 规格值选择 -->
                <div class="spec-values">
                  <div v-for="spec in form.specs" :key="spec.name" class="spec-value-item">
                    <span class="spec-label">{{ spec.name }}：</span>
                    <el-select v-model="combo.spec_values[spec.name]" placeholder="请选择">
                      <el-option 
                        v-for="value in spec.values.split(',').map(v => v.trim())" 
                        :key="value" 
                        :label="value" 
                        :value="value" 
                      />
                    </el-select>
                  </div>
                </div>
                
                <!-- 价格和库存 -->
                <div class="combo-pricing">
                  <el-form-item label="价格" required>
                    <el-input-number v-model="combo.price" :min="0" :precision="2" placeholder="价格" />
                  </el-form-item>
                  
                  <el-form-item label="库存" required>
                    <el-input-number v-model="combo.stock" :min="0" placeholder="库存" />
                  </el-form-item>
                  
                  <el-form-item label="规格图片">
                    <el-upload
                      class="upload-demo"
                      action=""
                      :http-request="(option) => uploadSpecImage(option, index)"
                      :show-file-list="false"
                      :auto-upload="false"
                      :before-upload="beforeUpload"
                    >
                      <el-button size="small">上传图片</el-button>
                    </el-upload>
                    <img v-if="combo.image_url" :src="combo.image_url" style="max-width: 100px; margin-top: 5px;" />
                  </el-form-item>
                </div>
              </div>
            </div>
            
            <el-button type="primary" @click="addSpecCombination">添加规格组合</el-button>
          </div>
        </el-form-item>
      </el-card>




    </el-form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, shallowRef, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Picture, Plus } from '@element-plus/icons-vue'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import axios from '@/api/request'

export default {
  name: 'ProductEdit',
  components: {
    Picture,
    Plus,
    Editor,
    Toolbar
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
      videos: [],
      hasSpecs: false,
      specs: [],
      specCombinations: [],
      detail: ''
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
      ]
    }
    
    // 上传地址（模拟）
    const uploadAction = 'https://jsonplaceholder.typicode.com/posts/'
    
    // 方法
    const loadProductData = async () => {
      const productId = route.params.id
      try {
        const res = await axios.get(`/api/web/product/${productId}`)
        if (res.data && res.data.code === 200) {
          const product = res.data.data
          
          // 填充基本信息
          form.name = product.name
          form.categoryId = product.category_id
          form.description = product.description || ''
          form.detail = product.detail || ''
          form.hasSpecs = product.has_specs || false
          
          // 处理图片和视频
          if (product.image_url) {
            const images = product.image_url.split('$%%$')
            if (images.length > 0) {
              form.mainImage = images[0]
              form.images = images.slice(1).map((url, index) => ({
                name: `image${index + 1}.jpg`,
                url: url
              }))
            }
          }
          
          if (product.video_url) {
            form.videos = [{
              name: 'video.mp4',
              url: product.video_url
            }]
          }
          
          // 处理规格信息
          if (product.has_specs && product.specs) {
            form.specs = product.specs.map(spec => ({
              name: spec.name,
              values: Array.isArray(spec.values) ? spec.values.join(',') : spec.values,
              sort_order: spec.sort_order || 0
            }))
          }
          
          if (product.has_specs && product.spec_combinations) {
            form.specCombinations = product.spec_combinations.map(combo => ({
              spec_values: combo.spec_values,
              price: combo.price,
              stock: combo.stock,
              image_url: combo.image_url || ''
            }))
          } else {
            // 无规格商品
            form.price = product.price
            form.stock = product.stock
          }
        }
      } catch (error) {
        console.error('加载商品数据失败:', error)
        ElMessage.error('加载商品数据失败')
      }
    }
    
    const saveProduct = async () => {
      try {
        await formRef.value.validate()
        saving.value = true
        
        const productId = route.params.id
        
        // 准备提交数据
        const payload = {
          name: form.name,
          description: form.description,
          detail: form.detail,
          category_id: form.categoryId,
          main_image: form.mainImage,
          images: form.images.map(img => img.url),
          videos: form.videos.map(video => video.url),
          has_specs: form.hasSpecs
        }
        
        if (!form.hasSpecs) {
          // 无规格商品
          payload.price = form.price
          payload.stock = form.stock
        } else {
          // 多规格商品
          payload.specs = form.specs.map(spec => ({
            name: spec.name,
            values: JSON.stringify(spec.values.split(',').map(v => v.trim())),
            sort_order: spec.sort_order
          }))
          
          payload.spec_combinations = form.specCombinations.map(combo => ({
            spec_values: JSON.stringify(combo.spec_values),
            price: combo.price,
            stock: combo.stock,
            image_url: combo.image_url
          }))
        }
        
        const res = await axios.put(`/api/web/product/${productId}`, payload)
        
        if (res.data && res.data.code === 200) {
          ElMessage.success('商品保存成功')
          router.push('/products')
        } else {
          ElMessage.error(res.data.message || '保存失败')
        }
      } catch (error) {
        console.error('保存商品失败:', error)
        ElMessage.error('保存失败，请重试')
      } finally {
        saving.value = false
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

    // wangEditor 富文本编辑器配置
    const editorRef = shallowRef()
    const mode = 'default'
    const toolbarConfig = {}
    const editorConfig = {
      placeholder: '请输入商品详情...',
      MENU_CONF: {
        uploadImage: {
          server: '/api/web/media/upload-image',
          fieldName: 'file',
          maxFileSize: 5 * 1024 * 1024, // 5MB
          maxNumberOfFiles: 10,
          allowedFileTypes: ['image/*'],
          onBeforeUpload(file) {
            return file
          },
          onProgress(progress) {
            console.log('progress', progress)
          },
          onSuccess(file, res) {
            console.log('success', file, res)
          },
          onFailed(file, res) {
            console.log('failed', file, res)
          },
          onError(file, err, res) {
            console.log('error', file, err, res)
          },
          customInsert(res, insertFn) {
            if (res.code === 200) {
              insertFn(res.url, res.alt, res.href)
            }
          }
        },
        uploadVideo: {
          server: '/api/web/media/upload-video',
          fieldName: 'file',
          maxFileSize: 100 * 1024 * 1024, // 100MB
          maxNumberOfFiles: 1,
          allowedFileTypes: ['video/*'],
          onBeforeUpload(file) {
            return file
          },
          onProgress(progress) {
            console.log('progress', progress)
          },
          onSuccess(file, res) {
            console.log('success', file, res)
          },
          onFailed(file, res) {
            console.log('failed', file, res)
          },
          onError(file, err, res) {
            console.log('error', file, err, res)
          },
          customInsert(res, insertFn) {
            if (res.code === 200) {
              insertFn(res.url)
            }
          }
        }
      }
    }

    const handleCreated = (editor) => {
      editorRef.value = editor
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
    
    const beforeVideoUpload = (file) => {
      const isVideo = file.type.startsWith('video/')
      const isLt100M = file.size / 1024 / 1024 < 100
      
      if (!isVideo) {
        ElMessage.error('只能上传视频文件!')
        return false
      }
      if (!isLt100M) {
        ElMessage.error('视频大小不能超过 100MB!')
        return false
      }
      return true
    }
    
    const handleVideoSuccess = (response, file) => {
      // 模拟上传成功
      const videoUrl = URL.createObjectURL(file.raw)
      form.videos.push({
        name: file.name,
        url: videoUrl
      })
      ElMessage.success('视频上传成功')
    }
    
    const handleVideoRemove = (file, fileList) => {
      form.videos = fileList
    }
    

    
    // 多规格相关方法
    const addSpec = () => {
      form.specs.push({
        name: '',
        values: '',
        sort_order: form.specs.length
      })
    }
    
    const removeSpec = (index) => {
      form.specs.splice(index, 1)
      // 重新生成规格组合
      generateSpecCombinations()
    }
    
    const addSpecCombination = () => {
      const spec_values = {}
      form.specs.forEach(spec => {
        spec_values[spec.name] = ''
      })
      
      form.specCombinations.push({
        spec_values,
        price: '',
        stock: '',
        image_url: ''
      })
    }
    
    const removeSpecCombination = (index) => {
      form.specCombinations.splice(index, 1)
    }
    
    const generateSpecCombinations = () => {
      if (form.specs.length === 0) {
        form.specCombinations = []
        return
      }
      
      // 获取所有规格的值
      const specValues = form.specs.map(spec => 
        spec.values.split(',').map(v => v.trim()).filter(v => v)
      )
      
      // 生成所有可能的组合
      const combinations = generateCombinations(specValues)
      
      // 更新规格组合
      form.specCombinations = combinations.map(combo => {
        const spec_values = {}
        form.specs.forEach((spec, index) => {
          spec_values[spec.name] = combo[index]
        })
        
        return {
          spec_values,
          price: '',
          stock: '',
          image_url: ''
        }
      })
    }
    
    const generateCombinations = (arrays) => {
      if (arrays.length === 0) return []
      if (arrays.length === 1) return arrays[0].map(item => [item])
      
      const [first, ...rest] = arrays
      const restCombinations = generateCombinations(rest)
      
      return first.flatMap(item => 
        restCombinations.map(combo => [item, ...combo])
      )
    }
    
    const beforeUpload = (file) => {
      // 可做图片类型/大小校验
      return true
    }
    
    const uploadSpecImage = async (option, index) => {
      const formData = new FormData()
      formData.append('file', option.file)
      // 这里应该调用实际的上传API
      // const res = await axios.post('/api/web/upload-image', formData, {
      //   headers: { 'Content-Type': 'multipart/form-data' }
      // })
      // form.specCombinations[index].image_url = res.data.url
      
      // 模拟上传成功
      form.specCombinations[index].image_url = URL.createObjectURL(option.file)
      option.onSuccess({ url: form.specCombinations[index].image_url }, option.file)
    }
    
    // 页面加载时获取商品数据
    onMounted(async () => {
      await loadProductData()
    })
    
    // 组件销毁时销毁编辑器
    onBeforeUnmount(() => {
      const editor = editorRef.value
      if (editor == null) return
      editor.destroy()
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
      handleVideoSuccess,
      handleVideoRemove,
      addSpec,
      removeSpec,
      addSpecCombination,
      removeSpecCombination,
      beforeUpload,
      uploadSpecImage,
      // wangEditor 相关
      editorRef,
      mode,
      toolbarConfig,
      editorConfig,
      handleCreated
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

.spec-types {
  margin-bottom: 20px;
}

.spec-type-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background-color: #fafafa;
}

.spec-combinations {
  margin-top: 20px;
}

.spec-combo-item {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #fff;
}

.combo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.combo-title {
  font-weight: bold;
  color: #333;
}

.combo-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.spec-values {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spec-value-item {
  display: flex;
  align-items: center;
}

.spec-label {
  min-width: 80px;
  font-weight: 500;
  color: #333;
}

.combo-pricing {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

@media (max-width: 768px) {
  .combo-content {
    grid-template-columns: 1fr;
  }
  
  .spec-type-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .spec-type-item > * {
    margin-bottom: 10px;
  }
}

/* 富文本编辑器样式 */
.rich-editor-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}
</style> 