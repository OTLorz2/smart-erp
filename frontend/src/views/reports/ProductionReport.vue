<template>
  <div class="production-report">
    <div class="header">
      <h1>生产报表</h1>
    </div>

    <!-- Summary -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <KPICard :value="summary.total_orders" label="生产订单总数" :icon="Document" type="number" bg-color="#409eff" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.completed" label="已完成" :icon="CircleCheck" type="number" bg-color="#67c23a" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.in_progress" label="生产中" :icon="Loading" type="number" bg-color="#e6a23c" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.pending" label="待生产" :icon="Clock" type="number" bg-color="#909399" />
      </el-col>
    </el-row>

    <!-- Efficiency -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>生产效率</span>
      </template>
      <el-table :data="efficiency" max-height="300">
        <el-table-column prop="order_no" label="订单编号" width="180" />
        <el-table-column prop="efficiency" label="完成率" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.efficiency" :color="getProgressColor(row.efficiency)" />
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!efficiency.length" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Document, CircleCheck, Loading, Clock } from '@element-plus/icons-vue'
import { getProductionSummary, getProductionEfficiency } from '@/api'
import KPICard from '@/components/stats/KPICard.vue'

const summary = ref({ total_orders: 0, completed: 0, in_progress: 0, pending: 0 })
const efficiency = ref<any[]>([])

const getProgressColor = (value: number) => {
  if (value >= 100) return '#67c23a'
  if (value >= 80) return '#409eff'
  if (value >= 60) return '#e6a23c'
  return '#f56c6c'
}

onMounted(async () => {
  try {
    const [summaryRes, efficiencyRes] = await Promise.all([
      getProductionSummary(),
      getProductionEfficiency()
    ])
    summary.value = summaryRes.data
    efficiency.value = efficiencyRes.data
  } catch (error) {
    console.error('Failed to load production report:', error)
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