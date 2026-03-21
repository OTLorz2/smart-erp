<template>
  <div class="records-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>出入库记录</span>
          <el-button type="primary" @click="router.push('/inventory/record-form')">新建</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="单据类型">
          <el-select v-model="queryForm.record_type" placeholder="全部" clearable>
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="生产入库" value="production_in" />
            <el-option label="其他入库" value="other_in" />
            <el-option label="销售出库" value="sales_out" />
            <el-option label="生产领料" value="production_out" />
            <el-option label="其他出库" value="other_out" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="records" v-loading="loading">
        <el-table-column prop="record_no" label="单据编号" width="180" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="material_id" label="物料ID" width="80" />
        <el-table-column prop="warehouse_id" label="仓库ID" width="80" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="unit_price" label="单价" />
        <el-table-column prop="total_price" label="总价" />
        <el-table-column prop="batch_no" label="批次号" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/inventory/record-form/${row.id}`)">编辑</el-button>
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
import { getInventoryRecords, deleteInventoryRecord } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const records = ref<any[]>([])
const loading = ref(false)

const queryForm = reactive({
  record_type: ''
})

const typeMap: Record<string, string> = {
  purchase_in: '采购入库',
  production_in: '生产入库',
  other_in: '其他入库',
  sales_out: '销售出库',
  production_out: '生产领料',
  other_out: '其他出库'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.record_type) {
      params.record_type = queryForm.record_type
    }
    const res = await getInventoryRecords(params)
    records.value = res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function resetQuery() {
  queryForm.record_type = ''
  loadData()
}

function getTypeLabel(type: string): string {
  return typeMap[type] || type
}

function getTypeTagType(type: string): string {
  if (type.includes('_in')) return 'success'
  if (type.includes('_out')) return 'warning'
  return 'info'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', { type: 'warning' })
    await deleteInventoryRecord(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => loadData())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>