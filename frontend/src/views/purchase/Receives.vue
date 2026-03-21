<template>
  <div class="receives-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>入库管理</span>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="订单状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="已确认" value="confirmed" />
            <el-option label="已入库" value="received" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="orders" v-loading="loading">
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="supplier_id" label="供应商ID" width="80" />
        <el-table-column prop="order_date" label="订单日期" width="160">
          <template #default="{ row }">{{ formatDate(row.order_date) }}</template>
        </el-table-column>
        <el-table-column prop="delivery_date" label="交货日期" width="160">
          <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button v-if="row.status === 'confirmed'" type="primary" size="small" @click="handleReceive(row)">入库</el-button>
            <el-button v-else size="small" @click="viewDetails(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 入库对话框 -->
    <el-dialog v-model="receiveDialogVisible" title="入库确认" width="600px">
      <el-form :model="receiveForm" label-width="80px">
        <el-form-item label="订单号">{{ currentOrder?.order_no }}</el-form-item>
        <el-divider>入库明细</el-divider>
        <el-table :data="orderItems">
          <el-table-column prop="material_id" label="物料ID" />
          <el-table-column prop="quantity" label="订单数量" />
          <el-table-column prop="received_qty" label="已入库" />
          <el-table-column label="本次入库">
            <template #default="{ row }">
              <el-input-number v-model="row.receive_qty" :min="0" :max="Number(row.quantity) - Number(row.received_qty || 0)" :precision="2" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="仓库">
            <template #default="{ row }">
              <el-select v-model="row.warehouse_id" size="small">
                <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <el-button @click="receiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReceive" :loading="receiving">确认入库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getPurchaseOrders, getPurchaseOrderItems, receiveOrder, getWarehouses } from '@/api'
import { ElMessage } from 'element-plus'

const orders = ref<any[]>([])
const loading = ref(false)
const queryForm = reactive({ status: '' })

const receiveDialogVisible = ref(false)
const currentOrder = ref<any>(null)
const orderItems = ref<any[]>([])
const warehouses = ref<any[]>([])
const receiving = ref(false)

const statusMap: Record<string, string> = {
  draft: '草稿', pending: '待审核', confirmed: '已确认', received: '已入库', completed: '已完成', cancelled: '已取消'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.status) params.status = queryForm.status
    const res = await getPurchaseOrders(params)
    orders.value = res.data.filter((o: any) => o.status === 'confirmed' || o.status === 'received')
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function getStatusLabel(status: string) { return statusMap[status] || status }
function getStatusTagType(status: string): string {
  if (status === 'received' || status === 'completed') return 'success'
  if (status === 'confirmed') return 'warning'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

async function handleReceive(order: any) {
  currentOrder.value = order
  const itemsRes = await getPurchaseOrderItems(order.id)
  orderItems.value = itemsRes.data.map((i: any) => ({
    ...i,
    receive_qty: Number(i.quantity) - Number(i.received_qty || 0),
    warehouse_id: 1
  }))
  receiveDialogVisible.value = true
}

function viewDetails(order: any) {
  currentOrder.value = order
  handleReceive(order)
  receiveDialogVisible.value = true
}

async function submitReceive() {
  receiving.value = true
  try {
    const items = orderItems.value
      .filter(i => i.receive_qty > 0)
      .map(i => ({
        material_id: i.material_id,
        quantity: i.receive_qty,
        warehouse_id: i.warehouse_id
      }))
    await receiveOrder(currentOrder.value.id, { items })
    ElMessage.success('入库成功')
    receiveDialogVisible.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '入库失败')
  } finally {
    receiving.value = false
  }
}

onMounted(async () => {
  const wRes = await getWarehouses()
  warehouses.value = wRes.data
  loadData()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>