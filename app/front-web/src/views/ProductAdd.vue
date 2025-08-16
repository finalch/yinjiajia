<template>
  <div class="product-add">
    <div class="page-header">
      <h1>新增商品</h1>
    </div>
    
    <el-form :model="form" label-width="100px" @submit.prevent="onSubmit">
      <!-- 基本信息 -->
      <el-card class="form-card">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-form-item label="商品名称" required>
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        
        <el-form-item label="商品描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入商品描述" />
        </el-form-item>
        
        <el-form-item label="商品分组" required>
          <el-select v-model="form.group_id" placeholder="请选择分组">
            <el-option v-for="cat in groups" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品品类" required>
          <el-select v-model="form.category_uuid" placeholder="请选择品类">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品主图" required>
          <div class="main-image-upload">
            <el-upload
              class="upload-demo"
              action=""
              :http-request="uploadMainImage"
              :show-file-list="false"
              :auto-upload="true"
              :before-upload="beforeImageUpload"
            >
              <div v-if="!form.main_image" class="upload-area">
                <el-icon size="48" color="#ddd"><Picture /></el-icon>
                <p>点击上传主图</p>
                <p style="font-size: 12px; color: #999;">建议尺寸：400x400px，不超过5MB</p>
              </div>
              <div v-else class="image-preview">
                <el-image :src="form.main_image" fit="cover" />
                <div class="image-actions">
                  <el-button type="text" @click="removeMainImage">删除</el-button>
                </div>
              </div>
            </el-upload>
          </div>
        </el-form-item>
        
        <el-form-item label="商品图片">
          <el-upload
            class="upload-demo"
            action=""
            :http-request="uploadImage"
            :show-file-list="true"
            :auto-upload="true"
            :before-upload="beforeImageUpload"
            :on-remove="handleImageRemove"
            :file-list="imageFileList"
            list-type="picture-card"
            :limit="9"
          >
            <el-button type="primary">上传图片</el-button>
            <template #tip>
              <div class="el-upload__tip">
                最多上传9张图片，每张不超过5MB
              </div>
            </template>
          </el-upload>
      
        </el-form-item>
        
        <el-form-item label="商品视频">
          <el-upload
            class="upload-demo"
            action=""
            :http-request="uploadVideo"
            :show-file-list="true"
            :auto-upload="true"
            :before-upload="beforeVideoUpload"
            :on-remove="handleVideoRemove"
            :file-list="videoFileList"
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

      <!-- 规格设置 -->
      <el-card class="form-card">
        <template #header>
          <span>规格设置</span>
        </template>
        
        <el-form-item label="是否多规格">
          <el-switch v-model="form.has_specs" />
          <span style="margin-left: 10px; color: #666;">开启后可以设置多种规格（如颜色、尺寸等）</span>
        </el-form-item>
        
        <!-- 无规格时的基础价格和库存 -->
        <template v-if="!form.has_specs">
          <el-form-item label="基础价格" required>
            <el-input-number v-model="form.price" :min="0" :precision="2" placeholder="请输入价格" />
          </el-form-item>
          
          <el-form-item label="基础库存" required>
            <el-input-number v-model="form.stock" :min="0" placeholder="请输入库存" />
          </el-form-item>
        </template>
        
        <!-- 多规格设置 -->
        <template v-if="form.has_specs">
          <!-- 规格类型管理 -->
          <el-form-item label="规格类型">
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
          <el-form-item label="规格组合">
            <div class="spec-combinations">
              <div v-for="(combo, index) in form.spec_combinations" :key="index" class="spec-combo-item">
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
        </template>
      </el-card>

      <!-- 提交按钮 -->
      <el-form-item>
        <el-button type="primary" @click="onSubmit" :loading="submitting">发布商品</el-button>
        <el-button @click="$router.go(-1)">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, shallowRef, onBeforeUnmount } from 'vue'
import axios from '@/api/request'
import { Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import '@wangeditor/editor/dist/css/style.css'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import authService from '../services/authService'
import { getMerchantInfo, clearAuth } from '../router/auth'

const form = reactive({
  name: '',
  description: '',
  detail: '',
  price: '',
  stock: '',
  group_id: '',
  category_uuid: '',
  main_image: '',
  images: [],
  videos: [],
  has_specs: false,
  specs: [],
  spec_combinations: []
})
// 商家信息
// const merchantInfo = ref(getMerchantInfo())
const currentMerchantId = computed(() => {
      const userInfo = authService.getUserInfo()
      return userInfo?.merchant_id || userInfo?.id
    })

const groups = ref([])
const categories = ref([])
const submitting = ref(false)

// 计算属性：转换图片列表为Element Plus格式
const imageFileList = computed(() => {
  const fileList = form.images.map((img, index) => ({
    uid: index,
    name: img.name,
    url: img.url,
    status: 'success'
  }))
  console.log('imageFileList 计算属性更新:', fileList)
  return fileList
})

// 计算属性：转换视频列表为Element Plus格式
const videoFileList = computed(() => {
  return form.videos.map((video, index) => ({
    uid: index,
    name: video.name,
    url: video.url,
    status: 'success'
  }))
})

onMounted(async () => {
  console.log('组件挂载，当前商家ID:', currentMerchantId.value)
  
  // 检查登录状态
  if (!authService.isLoggedIn()) {
    console.warn('用户未登录，使用默认商家ID')
    // 可以在这里跳转到登录页面或者使用默认值
  }
  
  // 获取分组列表
  try {
    const merchantId = currentMerchantId.value || 1 // 如果没有商家ID，使用默认值1
    console.log('使用商家ID:', merchantId)
    
    // 先测试不带参数的请求
    console.log('测试分组接口...')
    const testRes = await axios.get('/api/web/groups')
    console.log('分组接口测试响应:', testRes)
    
    const res = await axios.get('/api/web/groups', {
      params: {
        merchant_id: merchantId,
        status: 'active'
      }
    })
    console.log('分组接口响应:', res)
    groups.value = (res.data && res.data.data && res.data.data.list) ? res.data.data.list : []
    console.log('分组数据设置完成:', groups.value)
  } catch (error) {
    console.error('获取分组列表失败:', error)
    groups.value = []
  }
  
  // 获取品类列表
  try {
    console.log('测试品类接口...')
    const categoryRes = await axios.get('/api/g/category')
    console.log('品类接口响应:', categoryRes)
    categories.value = (categoryRes.data && categoryRes.data.data && categoryRes.data.data.list) ? categoryRes.data.data.list : []
    console.log('品类数据设置完成:', categories.value)
  } catch (error) {
    console.error('获取品类列表失败:', error)
    categories.value = []
  }
})

// 组件销毁时销毁编辑器
onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})

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

const uploadMainImage = async (option) => {
  console.log('开始上传主图:', option.file.name)
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await axios.post('/api/web/media/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    console.log('主图上传响应:', res.data)
    
    if (res.code === 200) {
      form.main_image = res.data.url
      console.log('主图上传成功:', form.main_image)
      ElMessage.success('主图上传成功')
      option.onSuccess(res.data, option.file)
    } else {
      throw new Error(res.data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传主图失败:', error)
    ElMessage.error('上传主图失败: ' + error.message)
    option.onError(error)
  }
}

const uploadImage = async (option) => {
  console.log('开始上传图片:', option.file.name)
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await axios.post('/api/web/media/upload-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    console.log('图片上传响应:', res.data)
    
    if (res.code === 200) {
      // 添加到图片列表
      form.images.push({
        name: option.file.name,
        url: res.data.url
      })
      
      console.log('图片上传成功，当前图片列表:', form.images)
      ElMessage.success('图片上传成功')
      option.onSuccess(res.data, option.file)
    } else {
      throw new Error(res.data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传图片失败:', error)
    ElMessage.error('上传图片失败: ' + error.message)
    option.onError(error)
  }
}

const uploadVideo = async (option) => {
  console.log('开始上传视频:', option.file.name)
  const formData = new FormData()
  formData.append('file', option.file)
  try {
    const res = await axios.post('/api/web/media/upload-video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    console.log('视频上传响应:', res.data)
    
    if (res.data.code === 200) {
      // 添加到视频列表
      form.videos.push({
        name: option.file.name,
        url: res.data.url
      })
      
      console.log('视频上传成功，当前视频列表:', form.videos)
      ElMessage.success('视频上传成功')
      option.onSuccess(res.data, option.file)
    } else {
      throw new Error(res.data.message || '上传失败')
    }
  } catch (error) {
    console.error('上传视频失败:', error)
    ElMessage.error('上传视频失败: ' + error.message)
    option.onError(error)
  }
}

const handleImageRemove = (file, fileList) => {
  // 根据uid找到要删除的图片
  const index = form.images.findIndex(img => img.name === file.name)
  if (index > -1) {
    form.images.splice(index, 1)
  }
}

const handleVideoRemove = (file, fileList) => {
  // 根据uid找到要删除的视频
  const index = form.videos.findIndex(video => video.name === file.name)
  if (index > -1) {
    form.videos.splice(index, 1)
  }
}

const removeMainImage = () => {
  form.main_image = ''
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



const uploadSpecImage = async (option, index) => {
  const formData = new FormData()
  formData.append('file', option.file)
  const res = await axios.post('/api/web/media/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  form.spec_combinations[index].image_url = res.data.url
  option.onSuccess(res.data, option.file)
}

// 添加规格类型
const addSpec = () => {
  form.specs.push({
    name: '',
    values: '',
    sort_order: form.specs.length
  })
}

// 删除规格类型
const removeSpec = (index) => {
  form.specs.splice(index, 1)
  // 重新生成规格组合
  generateSpecCombinations()
}

// 添加规格组合
const addSpecCombination = () => {
  const spec_values = {}
  form.specs.forEach(spec => {
    spec_values[spec.name] = ''
  })
  
  form.spec_combinations.push({
    spec_values,
    price: '',
    stock: '',
    image_url: ''
  })
}

// 删除规格组合
const removeSpecCombination = (index) => {
  form.spec_combinations.splice(index, 1)
}

// 生成规格组合
const generateSpecCombinations = () => {
  if (form.specs.length === 0) {
    form.spec_combinations = []
    return
  }
  
  // 获取所有规格的值
  const specValues = form.specs.map(spec => 
    spec.values.split(',').map(v => v.trim()).filter(v => v)
  )
  
  // 生成所有可能的组合
  const combinations = generateCombinations(specValues)
  
  // 更新规格组合
  form.spec_combinations = combinations.map(combo => {
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

// 生成组合的辅助函数
const generateCombinations = (arrays) => {
  if (arrays.length === 0) return []
  if (arrays.length === 1) return arrays[0].map(item => [item])
  
  const [first, ...rest] = arrays
  const restCombinations = generateCombinations(rest)
  
  return first.flatMap(item => 
    restCombinations.map(combo => [item, ...combo])
  )
}

// 监听规格变化，自动生成组合
const watchSpecs = () => {
  if (form.has_specs && form.specs.length > 0) {
    const hasValidSpecs = form.specs.every(spec => 
      spec.name && spec.values && spec.values.split(',').some(v => v.trim())
    )
    
    if (hasValidSpecs) {
      generateSpecCombinations()
    }
  }
}

const validateForm = () => {
  if (!form.name) {
    alert('商品名称不能为空')
    return false
  }
  
  if (!form.group_id) {
    alert('请选择商品分组')
    return false
  }
  
  if (!form.category_uuid) {
    alert('请选择商品品类')
    return false
  }
  
  if (!form.has_specs) {
    // 无规格商品验证
    if (!form.price || isNaN(form.price) || Number(form.price) <= 0) {
      alert('价格必须为大于0的数字')
      return false
    }
    if (!form.stock || isNaN(form.stock) || !Number.isInteger(Number(form.stock)) || Number(form.stock) < 0) {
      alert('库存必须为不小于0的整数')
      return false
    }
  } else {
    // 多规格商品验证
    if (form.specs.length === 0) {
      alert('请至少添加一个规格类型')
      return false
    }
    
    const hasValidSpecs = form.specs.every(spec => 
      spec.name && spec.values && spec.values.split(',').some(v => v.trim())
    )
    
    if (!hasValidSpecs) {
      alert('请完善规格类型信息')
      return false
    }
    
    if (form.spec_combinations.length === 0) {
      alert('请添加规格组合')
      return false
    }
    
    const hasValidCombos = form.spec_combinations.every(combo => 
      combo.price && combo.stock && 
      !isNaN(combo.price) && Number(combo.price) > 0 &&
      !isNaN(combo.stock) && Number.isInteger(Number(combo.stock)) && Number(combo.stock) >= 0
    )
    
    if (!hasValidCombos) {
      alert('请完善所有规格组合的价格和库存信息')
      return false
    }
  }
  
  // 验证图片和视频
  console.log('验证主图:', form.main_image)
  console.log('验证图片列表:', form.images)
  
  if (!form.main_image) {
    alert('请先上传商品主图')
    return false
  }
  
  if (form.images.length === 0) {
    alert('请至少上传一张商品图片')
    return false
  }
  
  return true
}

const onSubmit = async () => {
  if (!validateForm()) return
  
  submitting.value = true
  
  try {
    // 准备提交数据
    const payload = {
      name: form.name,
      description: form.description,
      detail: form.detail,
      group_id: form.group_id,
      category_uuid: form.category_uuid,
      main_image: form.main_image,
      images: form.images.map(img => img.url),
      videos: form.videos.map(video => video.url),
      merchant_id: 1,
      has_specs: form.has_specs
    }
    

    
    if (!form.has_specs) {
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
      
      payload.spec_combinations = form.spec_combinations.map(combo => ({
        spec_values: JSON.stringify(combo.spec_values),
        price: combo.price,
        stock: combo.stock,
        image_url: combo.image_url
      }))
    }
    
    const res = await axios.post('/api/web/product/', payload)
    
    if (res.data && res.data.code === 200) {
      alert('商品发布成功！')
      // 跳转到商品列表
      window.location.href = '/products'
    } else {
      alert(res.data.message || '发布失败')
    }
  } catch (error) {
    console.error('发布商品失败:', error)
    alert('发布失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 监听规格变化
const watchSpecsDebounced = () => {
  setTimeout(watchSpecs, 500)
}

// 暴露方法给模板
defineExpose({
  addSpec,
  removeSpec,
  addSpecCombination,
  removeSpecCombination,
  watchSpecsDebounced
})
</script>

<style scoped>
.product-add {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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

.main-image-upload {
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