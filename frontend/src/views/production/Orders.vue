<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生产工单</span>
          <el-button type="primary" @click="router.push('/production/order-form')">新建工单</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="待生产" value="pending" />
            <el-option label="生产中" value="in_progress" />
            <el-option label="质检通过" value="qc_passed" />
            <el-option label="质检失败" value="qc_failed" />
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
        <el-table-column prop="order_no" label="工单编号" />
        <el-table-column prop="product_id" label="产品ID" />
        <el-table-column prop="quantity" label="计划数量" />
        <el-table-column prop="completed_qty" label="已完成" />
        <el-table-column prop="start_date" label="计划开始">
          <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
        </el-table-column>
        <el-table-column prop="end_date" label="计划结束">
          <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/production/order-form/${row.id}`)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleStart(row.id)" v-if="row.status === 'pending'">开始</el-button>
            <el-button size="small" type="success" @click="handleComplete(row.id)" v-if="row.status === 'in_progress' || row.status === 'qc_passed'">完工</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProductionOrders, deleteProductionOrder, startProduction, completeProduction } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const orders = ref<any[]>([])
const loading = ref(false)
const queryForm = reactive({ status: '' })

const statusMap: Record<string, string> = {
  draft: '草稿', pending: '待生产', in_progress: '生产中', qc_passed: '质检通过',
  qc_failed: '质检失败', completed: '已完成', cancelled: '已取消'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.status) params.status = queryForm.status
    const res = await getProductionOrders(params)
    orders.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.status = ''
  loadData()
}

function getStatusTagType(status: string): string {
  if (status === 'completed') return 'success'
  if (status === 'in_progress') return 'warning'
  if (status === 'cancelled' || status === 'qc_failed') return 'danger'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

async function handleStart(id: number) {
  try {
    await startProduction(id)
    ElMessage.success('已开始生产')
    loadData()
  } catch (error) { ElMessage.error('操作失败') }
}

async function handleComplete(id: number) {
  try {
    await completeProduction(id)
    ElMessage.success('已完工')
    loadData()
  } catch (error) { ElMessage.error('操作失败') }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确认删除此工单?', '提示', { type: 'warning' })
    await deleteProductionOrder(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>