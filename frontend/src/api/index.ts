import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Inventory API
export const getInventoryRecords = (params?: any) => api.get('/inventory/records', { params })
export const createInventoryRecord = (data: any) => api.post('/inventory/records', data)
export const updateInventoryRecord = (id: number, data: any) => api.put(`/inventory/records/${id}`, data)
export const deleteInventoryRecord = (id: number) => api.delete(`/inventory/records/${id}`)
export const getInventoryRecord = (id: number) => api.get(`/inventory/records/${id}`)

export const getStocks = (params?: any) => api.get('/inventory/stocks', { params })
export const getStockAlerts = () => api.get('/inventory/alerts')
export const checkStock = (data: any) => api.post('/inventory/check', data)
export const getStockByMaterialWarehouse = (materialId: number, warehouseId: number) =>
  api.get(`/inventory/stocks/${materialId}/${warehouseId}`)

// Base data API
export const getMaterials = (params?: any) => api.get('/materials', { params })
export const getWarehouses = (params?: any) => api.get('/warehouses', { params })
export const getSuppliers = (params?: any) => api.get('/suppliers', { params })
export const getCustomers = (params?: any) => api.get('/customers', { params })
export const getUsers = (params?: any) => api.get('/users', { params })

// Sales API
export const getSalesOrders = (params?: any) => api.get('/sales/orders', { params })
export const getSalesOrder = (id: number) => api.get(`/sales/orders/${id}`)
export const createSalesOrder = (data: any) => api.post('/sales/orders', data)
export const updateSalesOrderStatus = (id: number, status: string) =>
  api.put(`/sales/orders/${id}/status`, null, { params: { status } })
export const updateSalesOrder = (id: number, data: any) => api.put(`/sales/orders/${id}`, data)
export const getSalesOrderItems = (id: number) => api.get(`/sales/orders/${id}/items`)
export const shipOrder = (id: number, data: any) => api.post(`/sales/orders/${id}/ship`, data)

// Quotation API
export const getQuotations = (params?: any) => api.get('/sales/quotations', { params })
export const getQuotation = (id: number) => api.get(`/sales/quotations/${id}`)
export const createQuotation = (data: any) => api.post('/sales/quotations', data)
export const updateQuotation = (id: number, data: any) => api.put(`/sales/quotations/${id}`, data)
export const deleteQuotation = (id: number) => api.delete(`/sales/quotations/${id}`)
export const convertQuotation = (id: number) => api.post(`/sales/quotations/${id}/convert`)

// Purchase API
export const getPurchaseOrders = (params?: any) => api.get('/purchase/orders', { params })
export const getPurchaseOrder = (id: number) => api.get(`/purchase/orders/${id}`)
export const createPurchaseOrder = (data: any) => api.post('/purchase/orders', data)
export const updatePurchaseOrderStatus = (id: number, status: string) =>
  api.put(`/purchase/orders/${id}/status`, null, { params: { status } })
export const updatePurchaseOrder = (id: number, data: any) => api.put(`/purchase/orders/${id}`, data)
export const getPurchaseOrderItems = (id: number) => api.get(`/purchase/orders/${id}/items`)
export const receiveOrder = (id: number, data: any) => api.post(`/purchase/orders/${id}/receive`, data)

// Purchase Quotation API
export const getPurchaseQuotations = (params?: any) => api.get('/purchase/quotations', { params })
export const getPurchaseQuotation = (id: number) => api.get(`/purchase/quotations/${id}`)
export const createPurchaseQuotation = (data: any) => api.post('/purchase/quotations', data)
export const updatePurchaseQuotation = (id: number, data: any) => api.put(`/purchase/quotations/${id}`, data)
export const deletePurchaseQuotation = (id: number) => api.delete(`/purchase/quotations/${id}`)
export const convertPurchaseQuotation = (id: number) => api.post(`/purchase/quotations/${id}/convert`)

// Auth API
export const login = (username: string, password: string) =>
  api.post('/auth/login', { username, password })

// Production API - BOM
export const getBOMs = (params?: any) => api.get('/production/boms', { params })
export const getBOM = (id: number) => api.get(`/production/boms/${id}`)
export const createBOM = (data: any) => api.post('/production/boms', data)
export const updateBOM = (id: number, data: any) => api.put(`/production/boms/${id}`, data)
export const deleteBOM = (id: number) => api.delete(`/production/boms/${id}`)
export const getBOMItems = (id: number) => api.get(`/production/boms/${id}/items`)
export const updateBOMItems = (id: number, items: any[]) => api.put(`/production/boms/${id}/items`, { items })

// Production API - Routes
export const getRoutes = (params?: any) => api.get('/production/routes', { params })
export const getRoute = (id: number) => api.get(`/production/routes/${id}`)
export const createRoute = (data: any) => api.post('/production/routes', data)
export const updateRoute = (id: number, data: any) => api.put(`/production/routes/${id}`, data)
export const deleteRoute = (id: number) => api.delete(`/production/routes/${id}`)
export const getRouteSteps = (id: number) => api.get(`/production/routes/${id}/steps`)
export const updateRouteSteps = (id: number, steps: any[]) => api.put(`/production/routes/${id}/steps`, { steps })

// Production API - Orders
export const getProductionOrders = (params?: any) => api.get('/production/orders', { params })
export const getProductionOrder = (id: number) => api.get(`/production/orders/${id}`)
export const createProductionOrder = (data: any) => api.post('/production/orders', data)
export const updateProductionOrder = (id: number, data: any) => api.put(`/production/orders/${id}`, data)
export const deleteProductionOrder = (id: number) => api.delete(`/production/orders/${id}`)
export const updateProductionOrderStatus = (id: number, status: string) =>
  api.put(`/production/orders/${id}/status`, null, { params: { status } })
export const getProductionOrderItems = (id: number) => api.get(`/production/orders/${id}/items`)
export const updateProductionOrderItems = (id: number, items: any[]) => api.put(`/production/orders/${id}/items`, { items })
export const getProductionRecords = (id: number) => api.get(`/production/orders/${id}/records`)
export const reportProduction = (id: number, data: any) => api.post(`/production/orders/${id}/report`, data)
export const startProduction = (id: number) => api.post(`/production/orders/${id}/start`)
export const completeProduction = (id: number) => api.post(`/production/orders/${id}/complete`)

// Quality API - Standards
export const getQCStandards = (params?: any) => api.get('/quality/standards', { params })
export const getQCStandard = (id: number) => api.get(`/quality/standards/${id}`)
export const createQCStandard = (data: any) => api.post('/quality/standards', data)
export const updateQCStandard = (id: number, data: any) => api.put(`/quality/standards/${id}`, data)
export const deleteQCStandard = (id: number) => api.delete(`/quality/standards/${id}`)

// Quality API - Records
export const getQCBRecords = (params?: any) => api.get('/quality/records', { params })
export const getQCRecord = (id: number) => api.get(`/quality/records/${id}`)
export const createQCRecord = (data: any) => api.post('/quality/records', data)
export const updateQCResult = (id: number, data: any) => api.put(`/quality/records/${id}/result`, data)
export const updateQCStatus = (id: number, status: string) => api.put(`/quality/records/${id}/status`, null, { params: { status } })
export const getQCTrace = (id: number) => api.get(`/quality/records/${id}/trace`)

// Quality API - Unqualified
export const getUnqualified = (params?: any) => api.get('/quality/unqualified', { params })
export const createUnqualified = (data: any) => api.post('/quality/unqualified', data)
export const updateUnqualified = (id: number, data: any) => api.put(`/quality/unqualified/${id}`, data)

// Reports API - Export/Import
export const exportData = (dataType: string, format: string = 'excel') =>
  api.get('/reports/export', { params: { data_type: dataType, format }, responseType: 'blob' })

export const downloadTemplate = (dataType: string) =>
  api.get(`/reports/export/template/${dataType}`, { responseType: 'blob' })

export const validateImport = (file: FormData, dataType: string) =>
  api.post('/reports/import/validate', file, { params: { data_type: dataType } })

// Reports API - Dashboard
export const getDashboardSummary = () => api.get('/reports/dashboard/summary')
export const getDashboardTrends = (days: number = 7) => api.get('/reports/dashboard/trends', { params: { days } })
export const getDashboardAlerts = () => api.get('/reports/dashboard/alerts')

// Reports API - Inventory
export const getInventorySummary = () => api.get('/reports/inventory/summary')
export const getInventoryAlerts = () => api.get('/reports/inventory/alerts')

// Reports API - Sales
export const getSalesSummary = (params?: any) => api.get('/reports/sales/summary', { params })
export const getSalesByCustomer = () => api.get('/reports/sales/by-customer')
export const getSalesByProduct = () => api.get('/reports/sales/by-product')

// Reports API - Purchase
export const getPurchaseSummary = (params?: any) => api.get('/reports/purchase/summary', { params })
export const getPurchaseBySupplier = () => api.get('/reports/purchase/by-supplier')

// Reports API - Production
export const getProductionSummary = () => api.get('/reports/production/summary')
export const getProductionEfficiency = () => api.get('/reports/production/efficiency')

// Reports API - Quality
export const getQualitySummary = () => api.get('/reports/quality/summary')
export const getQualityDefects = () => api.get('/reports/quality/defects')

// Notifications API
export const getNotifications = (params?: any) => api.get('/notifications', { params })
export const getUnreadCount = () => api.get('/notifications/unread-count')
export const markAsRead = (id: number) => api.put(`/notifications/${id}/read`)
export const markAllAsRead = () => api.put('/notifications/read-all')
export const deleteNotification = (id: number) => api.delete(`/notifications/${id}`)

export default api