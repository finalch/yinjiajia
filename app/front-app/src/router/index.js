import { createRouter, createWebHistory } from 'vue-router'
import { getToken, clearToken, clearUser } from '@/utils/auth.js'
import { authApi } from '@/utils/api.js'

const routes = [
  {
    path: '/',
    name: 'Shop',
    component: () => import('../views/shop.vue')
  },
  {
    path: '/purchase',
    name: 'Purchase',
    component: () => import('../views/purchase.vue')
  },
  {
    path: '/cart',
    name: 'CartList',
    component: () => import('../views/cartList.vue')
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/product-detail.vue')
  },
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('../views/payment.vue')
  },
  {
    path: '/pay-result',
    name: 'PayResult',
    component: () => import('../views/pay-result.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/profile.vue')
  },
  {
    path: '/address',
    name: 'Address',
    component: () => import('../views/address.vue')
  },
  {
    path: '/address-list',
    name: 'AddressList',
    component: () => import('../views/address-list.vue')
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('../views/checkout.vue')
  },
  {
    path: '/payment-method',
    redirect: '/checkout'
  },
  {
    path: '/my-order',
    name: 'MyOrder',
    component: () => import('../views/myorder.vue')
  },
  {
    path: '/customer-service',
    name: 'CustomerService',
    component: () => import('../views/customer-service.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/register.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 启动/路由切换登录态校验（演示版）
let hasValidated = false
router.beforeEach(async (to, from, next) => {
  const publicPages = new Set(['Login', 'Register'])
  if (publicPages.has(to.name)) return next()

  const token = getToken()
  if (!token) return next({ name: 'Login', query: { redirect: to.fullPath } })

  if (hasValidated) return next()
  try {
    const res = await authApi.validate(token)
    if (res.data.code === 200 && res.data.data && res.data.data.valid) {
      hasValidated = true
      return next()
    }
  } catch (e) {
    // ignore
  }
  clearToken()
  clearUser()
  return next({ name: 'Login', query: { redirect: to.fullPath } })
})

export default router 