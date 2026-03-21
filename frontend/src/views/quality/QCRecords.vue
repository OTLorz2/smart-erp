<template>
  <div class="qc-records-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>质检记录</span>
          <el-button type="primary" @click="router.push('/quality/record-form')">新建质检单</el-button>
        </div>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="质检类型">
          <el-select v-model="queryForm.qc_type" placeholder="全部" clearable>
            <el-option label="来料检验(IQC)" value="iqc" />
            <el-option label="制程检验(IPQC)" value="ipqc" />
            <el-option label="成品检验(OQC)" value="oqc" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="全部" clearable>
            <el-option label="待质检" value="pending" />
            <el-option label="合格" value="passed" />
            <el-option label="不合格" value="failed" />
            <el-option label="返工" value="rework" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="records" v-loading="loading">
        <el-table-column prop="record_no" label="质检单号" />
        <el-table-column prop="qc_type" label="质检类型">
          <template #default="{ row }">{{ qcTypeMap[row.qc_type] }}</template>
        </el-table-column>
        <el-table-column prop="batch_no" label="批次号" />
        <el-table-column prop="material_id" label="物料ID" />
        <el-table-column prop="quantity" label="检验数量" />
        <el-table-column prop="qualified_qty" label="合格数量" />
        <el-table-column prop="unqualified_qty" label="不合格数量" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">{{ statusMap[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inspect_date" label="检验日期">
          <template #default="{ row }">{{ formatDate(row.inspect_date) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/quality/record-form/${row.id}`)">详情</el-button>
            <el-button size="small" type="primary" @click="handleResult(row)" v-if="row.status === 'pending'">录入结果</el-button>
            <el-button size="small" type="info" @click="handleTrace(row.id)">追溯</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="resultDialog" title="录入质检结果" width="400px">
      <el-form :model="resultForm" label-width="100px">
        <el-form-item label="合格数量">
          <el-input-number v-model="resultForm.qualified_qty" :min="0" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="不合格数量">
          <el-input-number v-model="resultForm.unqualified_qty" :min="0" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="检验结果">
          <el-select v-model="resultForm.result">
            <el-option label="合格" value="passed" />
            <el-option label="不合格" value="failed" />
            <el-option label="返工" value="rework" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="resultForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resultDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResult">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="traceDialog" title="质量追溯" width="600px">
      <el-descriptions :column="2" border v-if="traceData">
        <el-descriptions-item label="质检单号">{{ traceData.qc_record?.record_no }}</el-descriptions-item>
        <el-descriptions-item label="质检类型">{{ qcTypeMap[traceData.qc_record?.qc_type] }}</el-descriptions-item>
        <el-descriptions-item label="物料">{{ traceData.material?.name }}</el-descriptions-item>
        <el-descriptions-item label="批次号">{{ traceData.qc_record?.batch_no }}</el-descriptions-item>
        <el-descriptions-item label="追溯类型">{{ traceData.source_type }}</el-descriptions-item>
      </el-descriptions>
      <el-divider>不良品记录</el-divider>
      <el-table :data="traceData?.unqualified_records || []" v-if="traceData?.unqualified_records?.length">
        <el-table-column prop="defect_type" label="不良类型" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="disposition" label="处理方式">
          <template #default="{ row }">{{ dispositionMap[row.disposition] }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="无不良品记录" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getQCBRecords, updateQCResult, getQCTrace } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const records = ref<any[]>([])
const loading = ref(false)
const resultDialog = ref(false)
const traceDialog = ref(false)
const currentId = ref(0)
const traceData = ref<any>(null)

const queryForm = reactive({ qc_type: '', status: '' })
const resultForm = reactive({ qualified_qty: 0, unqualified_qty: 0, result: 'passed', remark: '' })

const qcTypeMap: Record<string, string> = { iqc: 'IQC', ipqc: 'IPQC', oqc: 'OQC' }
const statusMap: Record<string, string> = { pending: '待质检', passed: '合格', failed: '不合格', rework: '返工' }
const dispositionMap: Record<string, string> = { scrap: '报废', rework: '返工', special_accept: '特采', return: '退货' }

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.qc_type) params.qc_type = queryForm.qc_type
    if (queryForm.status) params.status = queryForm.status
    const res = await getQCBRecords(params)
    records.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.qc_type = ''
  queryForm.status = ''
  loadData()
}

function getStatusTagType(status: string): string {
  if (status === 'passed') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'rework') return 'warning'
  return 'info'
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

function handleResult(row: any) {
  currentId.value = row.id
  resultForm.qualified_qty = row.quantity
  resultForm.unqualified_qty = 0
  resultForm.result = 'passed'
  resultForm.remark = ''
  resultDialog.value = true
}

async function submitResult() {
  try {
    await updateQCResult(currentId.value, resultForm)
    ElMessage.success('保存成功')
    resultDialog.value = false
    loadData()
  } catch (error) { ElMessage.error('保存失败') }
}

async function handleTrace(id: number) {
  try {
    const res = await getQCTrace(id)
    traceData.value = res.data
    traceDialog.value = true
  } catch (error) { ElMessage.error('获取追溯信息失败') }
}

onMounted(() => loadData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>