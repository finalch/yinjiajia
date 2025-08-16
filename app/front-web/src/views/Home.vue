<template>
  <div class="home">
    <!-- 轮播图 -->
    <el-carousel height="400px" class="banner">
      <el-carousel-item v-for="banner in banners" :key="banner.id">
        <img :src="banner.image" :alt="banner.title" class="banner-image">
        <div class="banner-content">
          <h2>{{ banner.title }}</h2>
          <p>{{ banner.description }}</p>
          <el-button type="primary" size="large" @click="handleBannerClick(banner)">
            {{ banner.buttonText }}
          </el-button>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 商品分类 -->
    <div class="groups">
      <h2 class="section-title">商品分类</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="group in groups" :key="group.id">
          <el-card class="group-card" @click="goToCategory(group.id)">
            <div class="group-icon">
              <i :class="group.icon"></i>
            </div>
            <h3>{{ group.name }}</h3>
            <p>{{ group.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 热门商品 -->
    <div class="hot-products">
      <h2 class="section-title">热门商品</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="product in hotProducts" :key="product.id">
          <el-card class="product-card" @click="goToProduct(product.id)">
            <img :src="product.image" :alt="product.name" class="product-image">
            <div class="product-info">
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">¥{{ product.price }}</p>
              <el-button type="primary" size="small" @click.stop="addToCart(product)">
                加入购物车
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 新品推荐 -->
    <div class="new-products">
      <h2 class="section-title">新品推荐</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="product in newProducts" :key="product.id">
          <el-card class="product-card" @click="goToProduct(product.id)">
            <img :src="product.image" :alt="product.name" class="product-image">
            <div class="product-info">
              <h3 class="product-name">{{ product.name }}</h3>
              <p class="product-price">¥{{ product.price }}</p>
              <el-button type="primary" size="small" @click.stop="addToCart(product)">
                加入购物车
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'Home',
  setup() {
    const router = useRouter()

    // 轮播图数据
    const banners = ref([
      {
        id: 1,
        title: '新品上市',
        description: '最新款iPhone 15系列，性能更强大',
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-1316-736.jpg',
        buttonText: '立即购买',
        link: '/product/1001'
      },
      {
        id: 2,
        title: '限时优惠',
        description: '全场商品8折起，限时抢购',
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-1316-736.jpg',
        buttonText: '查看详情',
        link: '/shop'
      }
    ])

    // 商品分类
    const groups = ref([
      {
        id: 1,
        name: '手机数码',
        description: '最新手机、平板、电脑',
        icon: 'el-icon-mobile-phone'
      },
      {
        id: 2,
        name: '服装配饰',
        description: '时尚服装、鞋帽、箱包',
        icon: 'el-icon-shopping-bag-1'
      },
      {
        id: 3,
        name: '家居生活',
        description: '家具、家电、生活用品',
        icon: 'el-icon-house'
      },
      {
        id: 4,
        name: '美妆护肤',
        description: '化妆品、护肤品、香水',
        icon: 'el-icon-present'
      }
    ])

    // 热门商品
    const hotProducts = ref([
      {
        id: 1001,
        name: 'Apple iPhone 15 Pro',
        price: 7999,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 1002,
        name: 'MacBook Pro 14英寸',
        price: 14999,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 1003,
        name: 'AirPods Pro',
        price: 1899,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 1004,
        name: 'iPad Air',
        price: 4399,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      }
    ])

    // 新品推荐
    const newProducts = ref([
      {
        id: 2001,
        name: 'Apple Watch Series 9',
        price: 2999,
        image: 'https://img.alicdn.com/imgextra/i1/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2002,
        name: 'Sony WH-1000XM5',
        price: 2899,
        image: 'https://img.alicdn.com/imgextra/i3/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2003,
        name: 'Nintendo Switch OLED',
        price: 2299,
        image: 'https://img.alicdn.com/imgextra/i4/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      },
      {
        id: 2004,
        name: 'DJI Mini 3 Pro',
        price: 4799,
        image: 'https://img.alicdn.com/imgextra/i2/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg'
      }
    ])

    const handleBannerClick = (banner) => {
      router.push(banner.link)
    }

    const goToCategory = (categoryId) => {
      router.push(`/shop?group=${categoryId}`)
    }

    const goToProduct = (productId) => {
      router.push(`/product/${productId}`)
    }

    const addToCart = (product) => {
      ElMessage.success(`已将 ${product.name} 加入购物车`)
    }

    return {
      banners,
      groups,
      hotProducts,
      newProducts,
      handleBannerClick,
      goToCategory,
      goToProduct,
      addToCart
    }
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.banner {
  margin-bottom: 40px;
  border-radius: 8px;
  overflow: hidden;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-content {
  position: absolute;
  top: 50%;
  left: 50px;
  transform: translateY(-50%);
  color: white;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.banner-content h2 {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.banner-content p {
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 20px;
  color: #333;
}

.groups {
  margin-bottom: 40px;
}

.group-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.group-card:hover {
  transform: translateY(-5px);
}

.group-icon {
  font-size: 3rem;
  color: #409eff;
  margin-bottom: 15px;
}

.group-card h3 {
  margin-bottom: 10px;
  color: #333;
}

.group-card p {
  color: #666;
}

.hot-products,
.new-products {
  margin-bottom: 40px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

.product-info {
  padding: 15px 0;
}

.product-name {
  font-size: 1rem;
  margin-bottom: 10px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price {
  font-size: 1.2rem;
  font-weight: bold;
  color: #e74c3c;
  margin-bottom: 10px;
}
</style> 