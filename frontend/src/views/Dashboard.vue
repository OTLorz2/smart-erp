<template>
  <div class="dashboard">
    <h1>经营概览</h1>

    <!-- KPI Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <KPICard
          :value="summary.today_sales"
          label="今日销售"
          :icon="Money"
          type="currency"
          bg-color="#409eff"
        />
      </el-col>
      <el-col :span="6">
        <KPICard
          :value="summary.month_sales"
          label="本月销售"
          :icon="TrendCharts"
          type="currency"
          bg-color="#67c23a"
        />
      </el-col>
      <el-col :span="6">
        <KPICard
          :value="summary.pending_orders"
          label="待处理订单"
          :icon="Document"
          type="number"
          bg-color="#e6a23c"
        />
      </el-col>
      <el-col :span="6">
        <KPICard
          :value="summary.inventory_value"
          label="库存价值"
          :icon="Box"
          type="currency"
          bg-color="#f56c6c"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <KPICard
          :value="summary.low_stock_items"
          label="库存预警"
          :icon="Warning"
          type="number"
          bg-color="#909399"
        />
      </el-col>
      <el-col :span="6">
        <KPICard
          :value="summary.pending_purchases"
          label="待采购"
          :icon="ShoppingBag"
          type="number"
          bg-color="#c71585"
        />
      </el-col>
    </el-row>

    <!-- Trends and Alerts -->
    <el-row :gutter="20">
      <el-col :span="12">
        <TrendList
          title="销售趋势"
          type="currency"
          :fetch-data="fetchSalesTrends"
        />
      </el-col>
      <el-col :span="12">
        <AlertList
          title="预警提醒"
          :fetch-alerts="fetchAlerts"
        />
      </el-col>
    </el-row>

    <!-- Quick Actions -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <QuickActions />
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Money, TrendCharts, Document, Box, Warning, ShoppingBag } from '@element-plus/icons-vue'
import { getDashboardSummary, getDashboardTrends, getDashboardAlerts } from '@/api'
import KPICard from '@/components/stats/KPICard.vue'
import TrendList from '@/components/stats/TrendList.vue'
import AlertList from '@/components/stats/AlertList.vue'
import QuickActions from '@/components/stats/QuickActions.vue'

const summary = ref({
  today_sales: 0,
  month_sales: 0,
  pending_orders: 0,
  inventory_value: 0,
  low_stock_items: 0,
  pending_purchases: 0
})

const fetchSalesTrends = async (days: number) => {
  try {
    const response = await getDashboardTrends(days)
    return response.data.sales || []
  } catch (error) {
    console.error('Failed to fetch sales trends:', error)
    return []
  }
}

const fetchAlerts = async () => {
  try {
    const response = await getDashboardAlerts()
    return response.data || []
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    return []
  }
}

onMounted(async () => {
  try {
    const response = await getDashboardSummary()
    summary.value = response.data
  } catch (error) {
    console.error('Failed to load dashboard summary:', error)
  }
})
</script>

<style scoped>
.dashboard h1 {
  margin-bottom: 20px;
  color: #333;
}

.stats-row {
  margin-bottom: 20px;
}
</style>