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
      },
      // Production
      {
        path: 'production/boms',
        name: 'ProductionBOMs',
        component: () => import('@/views/production/BOMs.vue')
      },
      {
        path: 'production/bom-form',
        name: 'BOMForm',
        component: () => import('@/views/production/BOMForm.vue')
      },
      {
        path: 'production/bom-form/:id',
        name: 'BOMFormEdit',
        component: () => import('@/views/production/BOMForm.vue')
      },
      {
        path: 'production/routes',
        name: 'ProcessRoutes',
        component: () => import('@/views/production/Routes.vue')
      },
      {
        path: 'production/route-form',
        name: 'RouteForm',
        component: () => import('@/views/production/RouteForm.vue')
      },
      {
        path: 'production/route-form/:id',
        name: 'RouteFormEdit',
        component: () => import('@/views/production/RouteForm.vue')
      },
      {
        path: 'production/orders',
        name: 'ProductionOrders',
        component: () => import('@/views/production/Orders.vue')
      },
      {
        path: 'production/order-form',
        name: 'ProductionOrderForm',
        component: () => import('@/views/production/OrderForm.vue')
      },
      {
        path: 'production/order-form/:id',
        name: 'ProductionOrderFormEdit',
        component: () => import('@/views/production/OrderForm.vue')
      },
      // Quality
      {
        path: 'quality/standards',
        name: 'QCStandards',
        component: () => import('@/views/quality/Standards.vue')
      },
      {
        path: 'quality/records',
        name: 'QCRecords',
        component: () => import('@/views/quality/QCRecords.vue')
      },
      {
        path: 'quality/record-form',
        name: 'QCRecordForm',
        component: () => import('@/views/quality/QCRecordForm.vue')
      },
      {
        path: 'quality/record-form/:id',
        name: 'QCRecordFormEdit',
        component: () => import('@/views/quality/QCRecordForm.vue')
      },
      {
        path: 'quality/unqualified',
        name: 'UnqualifiedRecords',
        component: () => import('@/views/quality/Unqualified.vue')
      },
      {
        path: 'quality/trace',
        name: 'QualityTrace',
        component: () => import('@/views/quality/Trace.vue')
      },
      // Reports
      {
        path: 'reports/inventory',
        name: 'InventoryReport',
        component: () => import('@/views/reports/InventoryReport.vue')
      },
      {
        path: 'reports/sales',
        name: 'SalesReport',
        component: () => import('@/views/reports/SalesReport.vue')
      },
      {
        path: 'reports/purchase',
        name: 'PurchaseReport',
        component: () => import('@/views/reports/PurchaseReport.vue')
      },
      {
        path: 'reports/production',
        name: 'ProductionReport',
        component: () => import('@/views/reports/ProductionReport.vue')
      },
      {
        path: 'reports/quality',
        name: 'QualityReport',
        component: () => import('@/views/reports/QualityReport.vue')
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