import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      // Base Data
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/base-data/Users.vue')
      },
      {
        path: 'materials',
        name: 'Materials',
        component: () => import('@/views/base-data/Materials.vue')
      },
      {
        path: 'warehouses',
        name: 'Warehouses',
        component: () => import('@/views/base-data/Warehouses.vue')
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/base-data/Suppliers.vue')
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/base-data/Customers.vue')
      },
      // Inventory
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryList.vue')
      },
      // Sales
      {
        path: 'sales/orders',
        name: 'SalesOrders',
        component: () => import('@/views/sales/Orders.vue')
      },
      // Purchase
      {
        path: 'purchase/orders',
        name: 'PurchaseOrders',
        component: () => import('@/views/purchase/Orders.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router