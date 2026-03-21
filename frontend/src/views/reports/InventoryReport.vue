<template>
  <div class="inventory-report">
    <div class="header">
      <h1>库存报表</h1>
      <ExportButton data-type="inventory" />
    </div>

    <!-- Summary -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="8">
        <KPICard :value="summary.total_items" label="物料种类" :icon="Box" type="number" bg-color="#409eff" />
      </el-col>
      <el-col :span="8">
        <KPICard :value="summary.total_stocks" label="库存记录" :icon="Database" type="number" bg-color="#67c23a" />
      </el-col>
      <el-col :span="8">
        <KPICard :value="summary.total_value" label="库存价值" :icon="Money" type="currency" bg-color="#e6a23c" />
      </el-col>
    </el-row>

    <!-- Alerts -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>库存预警</span>
      </template>
      <el-table :data="alerts" max-height="300">
        <el-table-column prop="material_code" label="物料编码" width="150" />
        <el-table-column prop="material_name" label="物料名称" />
        <el-table-column prop="warehouse" label="仓库" width="120" />
        <el-table-column prop="current_stock" label="当前库存" width="100" />
        <el-table-column prop="safety_stock" label="安全库存" width="100" />
      </el-table>
      <el-empty v-if="!alerts.length" description="暂无预警" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Box, Database, Money } from '@element-plus/icons-vue'
import { getInventorySummary, getInventoryAlerts } from '@/api'
import ExportButton from '@/components/common/ExportButton.vue'
import KPICard from '@/components/stats/KPICard.vue'

const summary = ref({ total_items: 0, total_stocks: 0, total_value: 0 })
const alerts = ref<any[]>([])

onMounted(async () => {
  try {
    const [summaryRes, alertsRes] = await Promise.all([
      getInventorySummary(),
      getInventoryAlerts()
    ])
    summary.value = summaryRes.data
    alerts.value = alertsRes.data
  } catch (error) {
    console.error('Failed to load inventory report:', error)
  }
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-row {
  margin-bottom: 20px;
}
</style>