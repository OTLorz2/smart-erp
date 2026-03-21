<template>
  <div class="quotations-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报价单</span>
          <el-button type="primary" @click="router.push('/sales/quotation-form')">新建报价单</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="已发送" value="sent" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已过期" value="expired" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="quotations" v-loading="loading">
        <el-table-column prop="quote_no" label="报价单号" width="180" />
        <el-table-column prop="customer_id" label="客户ID" width="80" />
        <el-table-column prop="quote_date" label="报价日期" width="160">
          <template #default="{ row }">{{ formatDate(row.quote_date) }}</template>
        </el-table-column>
        <el-table-column prop="valid_date" label="有效期至" width="160">
          <template #default="{ row }">{{ formatDate(row.valid_date) }}</template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/sales/quotation-form/${row.id}`)">编辑</el-button>
            <el-button size="small" type="success" @click="handleConvert(row.id)" :disabled="row.status !== 'confirmed'">转订单</el-button>
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
import { getQuotations, convertQuotation, deleteQuotation } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const quotations = ref<any[]>([])
const loading = ref(false)

const queryForm = reactive({ status: '' })

const statusMap: Record<string, string> = {
  draft: '草稿', sent: '已发送', confirmed: '已确认', expired: '已过期', cancelled: '已取消'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.status) params.status = queryForm.status
    const res = await getQuotations(params)
    quotations.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.status = ''
  loadData()
}

function getStatusLabel(status: string) { return statusMap[status] || status }
function getStatusTagType(status: string): string {
  if (status === 'confirmed') return 'success'
  if (status === 'draft') return 'info'
  if (status === 'cancelled' || status === 'expired') return 'danger'
  return 'warning'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

async function handleConvert(id: number) {
  try {
    await ElMessageBox.confirm('确定要将此报价单转为销售订单吗？', '提示', { type: 'info' })
    await convertQuotation(id)
    ElMessage.success('已转为销售订单')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除此报价单吗？', '提示', { type: 'warning' })
    await deleteQuotation(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>