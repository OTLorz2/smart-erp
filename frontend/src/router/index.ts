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
      {
        path: 'inventory/records',
        name: 'InventoryRecords',
        component: () => import('@/views/inventory/Records.vue')
      },
      {
        path: 'inventory/record-form',
        name: 'RecordForm',
        component: () => import('@/views/inventory/RecordForm.vue')
      },
      {
        path: 'inventory/record-form/:id',
        name: 'RecordFormEdit',
        component: () => import('@/views/inventory/RecordForm.vue')
      },
      {
        path: 'inventory/check',
        name: 'StockCheck',
        component: () => import('@/views/inventory/StockCheck.vue')
      },
      {
        path: 'inventory/alerts',
        name: 'StockAlerts',
        component: () => import('@/views/inventory/Alerts.vue')
      },
      // Sales
      {
        path: 'sales/orders',
        name: 'SalesOrders',
        component: () => import('@/views/sales/Orders.vue')
      },
      {
        path: 'sales/order-form',
        name: 'SalesOrderForm',
        component: () => import('@/views/sales/OrderForm.vue')
      },
      {
        path: 'sales/order-form/:id',
        name: 'SalesOrderFormEdit',
        component: () => import('@/views/sales/OrderForm.vue')
      },
      {
        path: 'sales/quotations',
        name: 'SalesQuotations',
        component: () => import('@/views/sales/Quotations.vue')
      },
      {
        path: 'sales/quotation-form',
        name: 'SalesQuotationForm',
        component: () => import('@/views/sales/QuotationForm.vue')
      },
      {
        path: 'sales/quotation-form/:id',
        name: 'SalesQuotationFormEdit',
        component: () => import('@/views/sales/QuotationForm.vue')
      },
      {
        path: 'sales/shipments',
        name: 'SalesShipments',
        component: () => import('@/views/sales/Shipments.vue')
      },
      // Purchase
      {
        path: 'purchase/orders',
        name: 'PurchaseOrders',
        component: () => import('@/views/purchase/Orders.vue')
      },
      {
        path: 'purchase/order-form',
        name: 'PurchaseOrderForm',
        component: () => import('@/views/purchase/OrderForm.vue')
      },
      {
        path: 'purchase/order-form/:id',
        name: 'PurchaseOrderFormEdit',
        component: () => import('@/views/purchase/OrderForm.vue')
      },
      {
        path: 'purchase/quotations',
        name: 'PurchaseQuotations',
        component: () => import('@/views/purchase/Quotations.vue')
      },
      {
        path: 'purchase/quotation-form',
        name: 'PurchaseQuotationForm',
        component: () => import('@/views/purchase/QuotationForm.vue')
      },
      {
        path: 'purchase/quotation-form/:id',
        name: 'PurchaseQuotationFormEdit',
        component: () => import('@/views/purchase/QuotationForm.vue')
      },
      {
        path: 'purchase/receives',
        name: 'PurchaseReceives',
        component: () => import('@/views/purchase/Receives.vue')
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