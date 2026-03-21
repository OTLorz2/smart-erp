<template>
  <div class="alerts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存预警</span>
          <el-button type="primary" @click="loadData" :loading="loading">刷新</el-button>
        </div>
      </template>
      <el-alert
        title="库存预警说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        以下物料库存低于安全库存或最小库存，请及时补货
      </el-alert>
      <el-table :data="alerts" v-loading="loading">
        <el-table-column prop="material_code" label="物料编码" />
        <el-table-column prop="material_name" label="物料名称" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="current_quantity" label="当前库存">
          <template #default="{ row }">
            <el-tag :type="getStockTagType(row)">{{ row.current_quantity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" />
        <el-table-column prop="min_stock" label="最小库存" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag v-if="row.current_quantity < row.min_stock" type="danger">低于最小库存</el-tag>
            <el-tag v-else-if="row.current_quantity < row.safety_stock" type="warning">低于安全库存</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="alerts.length === 0 && !loading" description="暂无预警数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStockAlerts } from '@/api'
import { ElMessage } from 'element-plus'

const alerts = ref<any[]>([])
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const res = await getStockAlerts()
    alerts.value = res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function getStockTagType(row: any): string {
  if (row.current_quantity < row.min_stock) return 'danger'
  if (row.current_quantity < row.safety_stock) return 'warning'
  return 'success'
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