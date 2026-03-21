<template>
  <div class="routes-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>工艺路线</span>
          <el-button type="primary" @click="router.push('/production/route-form')">新建路线</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="生效" value="active" />
            <el-option label="作废" value="obsolete" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="routes" v-loading="loading">
        <el-table-column prop="route_no" label="路线编号" />
        <el-table-column prop="product_id" label="产品ID" />
        <el-table-column prop="version" label="版本" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/production/route-form/${row.id}`)">编辑</el-button>
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
import { getRoutes, deleteRoute } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const routes = ref<any[]>([])
const loading = ref(false)
const queryForm = reactive({ status: '' })

const statusMap: Record<string, string> = {
  draft: '草稿', active: '生效', obsolete: '作废'
}

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.status) params.status = queryForm.status
    const res = await getRoutes(params)
    routes.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.status = ''
  loadData()
}

function getStatusTagType(status: string): string {
  if (status === 'active') return 'success'
  if (status === 'obsolete') return 'danger'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确认删除此工艺路线?', '提示', { type: 'warning' })
    await deleteRoute(id)
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