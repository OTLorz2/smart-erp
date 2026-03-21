<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售订单</span>
          <el-button type="primary" @click="router.push('/sales/order-form')">新建订单</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="orders" v-loading="loading">
        <el-table-column prop="order_no" label="订单编号" />
        <el-table-column prop="customer_id" label="客户ID" />
        <el-table-column prop="order_date" label="订单日期">
          <template #default="{ row }">{{ formatDate(row.order_date) }}</template>
        </el-table-column>
        <el-table-column prop="delivery_date" label="交货日期">
          <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/sales/order-form/${row.id}`)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSalesOrders } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const orders = ref<any[]>([])
const loading = ref(false)
const queryForm = reactive({ status: '' })

const statusMap: Record<string, string> = {
  draft: '草稿', pending: '待审核', confirmed: '已确认', shipped: '已发货', completed: '已完成', cancelled: '已取消'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.status) params.status = queryForm.status
    const res = await getSalesOrders(params)
    orders.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.status = ''
  loadData()
}

function getStatusTagType(status: string): string {
  if (status === 'shipped' || status === 'completed') return 'success'
  if (status === 'confirmed') return 'warning'
  if (status === 'cancelled') return 'danger'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

onMounted(() => loadData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>