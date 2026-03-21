<template>
  <div class="trace-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>质量追溯</span>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="质检单号">
          <el-input v-model="recordNo" placeholder="输入质检单号" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
        </el-form-item>
      </el-form>

      <template v-if="traceData">
        <el-divider>基本信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="质检单号">{{ traceData.qc_record?.record_no }}</el-descriptions-item>
          <el-descriptions-item label="质检类型">{{ qcTypeMap[traceData.qc_record?.qc_type] }}</el-descriptions-item>
          <el-descriptions-item label="物料">{{ traceData.material?.name }}</el-descriptions-item>
          <el-descriptions-item label="批次号">{{ traceData.qc_record?.batch_no }}</el-descriptions-item>
          <el-descriptions-item label="检验数量">{{ traceData.qc_record?.quantity }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(traceData.qc_record?.status)">{{ statusMap[traceData.qc_record?.status] }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="合格数量">{{ traceData.qc_record?.qualified_qty }}</el-descriptions-item>
          <el-descriptions-item label="不合格数量">{{ traceData.qc_record?.unqualified_qty }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>追溯信息</el-divider>
        <el-alert :title="`追溯来源: ${traceData.source_type === 'purchase' ? '采购入库' : traceData.source_type === 'production' ? '生产工单' : '无'}`" type="info" :closable="false" />

        <template v-if="traceData.source_type === 'production' && traceData.production_orders?.length">
          <el-table :data="traceData.production_orders" border style="margin-top: 15px">
            <el-table-column prop="order_no" label="工单编号" />
            <el-table-column prop="product_id" label="产品ID" />
            <el-table-column prop="quantity" label="计划数量" />
            <el-table-column prop="completed_qty" label="已完成" />
            <el-table-column prop="status" label="状态" />
          </el-table>
        </template>

        <el-divider>不良品记录</el-divider>
        <el-table :data="traceData.unqualified_records" border v-if="traceData.unqualified_records?.length">
          <el-table-column prop="defect_type" label="不良类型" />
          <el-table-column prop="quantity" label="数量" />
          <el-table-column prop="disposition" label="处理方式">
            <template #default="{ row }">{{ dispositionMap[row.disposition] || '待处理' }}</template>
          </el-table-column>
          <el-table-column prop="disposition_date" label="处理日期">
            <template #default="{ row }">{{ formatDate(row.disposition_date) }}</template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" />
        </el-table>
        <el-empty v-else description="无不良品记录" />
      </template>

      <el-empty v-else description="请输入质检单号进行追溯查询" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { getQCBRecords, getQCTrace } from '@/api'
import { ElMessage } from 'element-plus'

const recordNo = ref('')
const traceData = ref<any>(null)

const qcTypeMap: Record<string, string> = { iqc: 'IQC', ipqc: 'IPQC', oqc: 'OQC' }
const statusMap: Record<string, string> = { pending: '待质检', passed: '合格', failed: '不合格', rework: '返工' }
const dispositionMap: Record<string, string> = { scrap: '报废', rework: '返工', special_accept: '特采', return: '退货' }

async function handleSearch() {
  if (!recordNo.value) {
    return ElMessage.warning('请输入质检单号')
  }

  try {
    // Find the QC record by record_no - fetch all and filter locally
    const res = await getQCBRecords({})
    const records = res.data.filter((r: any) => r.record_no === recordNo.value)

    if (!records || records.length === 0) {
      return ElMessage.warning('未找到质检记录')
    }

    // Get trace info
    const traceRes = await getQCTrace(records[0].id)
    traceData.value = traceRes.data
  } catch (error) {
    ElMessage.error('查询失败')
  }
}

function getStatusTagType(status: string): string {
  if (status === 'passed') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'rework') return 'warning'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>