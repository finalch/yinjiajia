import { createRouter, createWebHistory } from 'vue-router'

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
    path: '/my-order',
    name: 'MyOrder',
    component: () => import('../views/myorder.vue')
  },
  {
    path: '/customer-service',
    name: 'CustomerService',
    component: () => import('../views/customer-service.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 