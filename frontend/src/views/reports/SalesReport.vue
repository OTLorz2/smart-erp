<template>
  <div class="sales-report">
    <div class="header">
      <h1>销售报表</h1>
      <ExportButton data-type="sales" />
    </div>

    <!-- Summary -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="8">
        <KPICard :value="summary.total_amount" label="销售总额" :icon="Money" type="currency" bg-color="#409eff" />
      </el-col>
      <el-col :span="8">
        <KPICard :value="summary.order_count" label="订单数量" :icon="Document" type="number" bg-color="#67c23a" />
      </el-col>
      <el-col :span="8">
        <KPICard :value="summary.avg_amount" label="平均订单金额" :icon="TrendCharts" type="currency" bg-color="#e6a23c" />
      </el-col>
    </el-row>

    <!-- Date filter -->
    <el-card style="margin-top: 20px;">
      <el-form inline>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadSalesData"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <!-- By Customer -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>按客户统计</span>
      </template>
      <el-table :data="byCustomer" max-height="300">
        <el-table-column prop="customer_name" label="客户" />
        <el-table-column prop="total_amount" label="销售额" width="150">
          <template #default="{ row }">
            ¥{{ row.total_amount.toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- By Product -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>按产品统计</span>
      </template>
      <el-table :data="byProduct" max-height="300">
        <el-table-column prop="material_name" label="产品" />
        <el-table-column prop="quantity" label="销售数量" width="120" />
        <el-table-column prop="amount" label="销售金额" width="150">
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Money, Document, TrendCharts } from '@element-plus/icons-vue'
import { getSalesSummary, getSalesByCustomer, getSalesByProduct } from '@/api'
import ExportButton from '@/components/common/ExportButton.vue'
import KPICard from '@/components/stats/KPICard.vue'

const summary = ref({ total_amount: 0, order_count: 0, avg_amount: 0 })
const byCustomer = ref<any[]>([])
const byProduct = ref<any[]>([])
const dateRange = ref<[Date, Date] | null>(null)

const loadSalesData = async () => {
  try {
    const params: any = {}
    if (dateRange.value) {
      params.start_date = dateRange.value[0].toISOString().slice(0, 10)
      params.end_date = dateRange.value[1].toISOString().slice(0, 10)
    }

    const [summaryRes, customerRes, productRes] = await Promise.all([
      getSalesSummary(params),
      getSalesByCustomer(),
      getSalesByProduct()
    ])
    summary.value = summaryRes.data
    byCustomer.value = customerRes.data
    byProduct.value = productRes.data
  } catch (error) {
    console.error('Failed to load sales report:', error)
  }
}

onMounted(() => {
  loadSalesData()
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