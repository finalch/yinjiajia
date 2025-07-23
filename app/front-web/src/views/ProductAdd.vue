<template>
  <el-form :model="form" label-width="100px" @submit.prevent="onSubmit">
    <el-form-item label="商品名称">
      <el-input v-model="form.name" />
    </el-form-item>
    <el-form-item label="描述">
      <el-input v-model="form.description" type="textarea" />
    </el-form-item>
    <el-form-item label="价格">
      <el-input-number v-model="form.price" :min="0" />
    </el-form-item>
    <el-form-item label="库存">
      <el-input-number v-model="form.stock" :min="0" />
    </el-form-item>
    <el-form-item label="分类">
      <el-select v-model="form.category_id" placeholder="请选择分类">
        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
      </el-select>
    </el-form-item>
    <el-form-item label="商品图片">
      <el-upload
        class="upload-demo"
        action=""
        :http-request="uploadImage"
        :show-file-list="false"
        :auto-upload="false"
        :before-upload="beforeUpload"
      >
        <el-button type="primary">上传图片</el-button>
      </el-upload>
      <img v-if="form.image_url" :src="form.image_url" style="max-width: 200px; margin-top: 10px;" />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">发布商品</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from '@/api/request'

const form = reactive({
  name: '',
  description: '',
  price: '',
  stock: '',
  category_id: '',
  image_url: ''
})
const categories = ref([])

onMounted(async () => {
  // 获取分类列表
  const res = await axios.get('/api/web/categories?merchant_id=1&status=active')
  categories.value = (res.data.data && res.data.data.list) ? res.data.data.list : []
})

const beforeUpload = (file) => {
  // 可做图片类型/大小校验
  return true
}

const uploadImage = async (option) => {
  const formData = new FormData()
  formData.append('file', option.file)
  const res = await axios.post('/api/web/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  form.image_url = res.data.url
  option.onSuccess(res.data, option.file)
}

const validateForm = () => {
  if (!form.name) {
    alert('商品名称不能为空')
    return false
  }
  if (!form.price || isNaN(form.price) || Number(form.price) <= 0) {
    alert('价格必须为大于0的数字')
    return false
  }
  if (!form.stock || isNaN(form.stock) || !Number.isInteger(Number(form.stock)) || Number(form.stock) < 0) {
    alert('库存必须为不小于0的整数')
    return false
  }
  if (!form.category_id) {
    alert('请选择商品分类')
    return false
  }
  if (!categories.value.find(cat => cat.id === form.category_id)) {
    alert('请选择有效的商品分类')
    return false
  }
  if (!form.image_url) {
    // alert('请先上传商品图片')
    // return false
  }
  return true
}

const onSubmit = async () => {
  if (!validateForm()) return
  // 带上 merchant_id
  const payload = { ...form, merchant_id: 1 }
  const res = await axios.post('/api/web/product/', payload)
  if (res.data && res.data.msg) {
    alert(res.data.msg)
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