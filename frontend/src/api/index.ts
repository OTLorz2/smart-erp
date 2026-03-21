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

export default api