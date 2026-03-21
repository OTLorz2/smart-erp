<template>
  <div class="quality-report">
    <div class="header">
      <h1>质量报表</h1>
    </div>

    <!-- Summary -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="6">
        <KPICard :value="summary.total" label="检验总数" :icon="Document" type="number" bg-color="#409eff" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.passed" label="合格数" :icon="CircleCheck" type="number" bg-color="#67c23a" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.failed" label="不合格数" :icon="CircleClose" type="number" bg-color="#f56c6c" />
      </el-col>
      <el-col :span="6">
        <KPICard :value="summary.pass_rate" label="合格率" :icon="TrendCharts" type="percent" bg-color="#e6a23c" />
      </el-col>
    </el-row>

    <!-- Defects -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>不良记录</span>
      </template>
      <el-table :data="defects" max-height="300">
        <el-table-column prop="record_no" label="检验单号" width="180" />
        <el-table-column prop="material_name" label="物料" />
        <el-table-column prop="defect_type" label="不良类型" width="120" />
        <el-table-column prop="defect_count" label="不良数量" width="100" />
        <el-table-column prop="created_at" label="检验日期" width="120" />
      </el-table>
      <el-empty v-if="!defects.length" description="暂无不良记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Document, CircleCheck, CircleClose, TrendCharts } from '@element-plus/icons-vue'
import { getQualitySummary, getQualityDefects } from '@/api'
import KPICard from '@/components/stats/KPICard.vue'

const summary = ref({ total: 0, passed: 0, failed: 0, pass_rate: 0 })
const defects = ref<any[]>([])

onMounted(async () => {
  try {
    const [summaryRes, defectsRes] = await Promise.all([
      getQualitySummary(),
      getQualityDefects()
    ])
    summary.value = summaryRes.data
    defects.value = defectsRes.data
  } catch (error) {
    console.error('Failed to load quality report:', error)
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