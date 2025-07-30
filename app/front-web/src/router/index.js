import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/products',
    name: 'Products',
    component: () => import('../views/Products.vue')
  },
  {
    path: '/products/add',
    name: 'ProductAdd',
    component: () => import('../views/ProductAdd.vue')
  },
  {
    path: '/products/edit/:id',
    name: 'ProductEdit',
    component: () => import('../views/ProductEdit.vue')
  },
  {
    path: '/products/audit',
    name: 'ProductAudit',
    component: () => import('../views/ProductAudit.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue')
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/Orders.vue')
  },
  {
    path: '/logistics',
    name: 'Logistics',
    component: () => import('../views/Logistics.vue')
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('../views/Analytics.vue')
  },
  {
    path: '/finance',
    name: 'Finance',
    component: () => import('../views/Finance.vue')
  },
  {
    path: '/customer-service',
    name: 'CustomerService',
    component: () => import('../views/CustomerService.vue')
  },
  {
    path: '/reviews',
    name: 'Reviews',
    component: () => import('../views/Reviews.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 