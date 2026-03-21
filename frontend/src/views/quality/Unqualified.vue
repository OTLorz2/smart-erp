<template>
  <div class="unqualified-page">
    <el-card>
      <template #header>
        <span>不良品管理</span>
      </template>
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="处理方式">
          <el-select v-model="queryForm.disposition" placeholder="全部" clearable>
            <el-option label="报废" value="scrap" />
            <el-option label="返工" value="rework" />
            <el-option label="特采" value="special_accept" />
            <el-option label="退货" value="return" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="records" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="qc_record_id" label="质检单ID" />
        <el-table-column prop="defect_type" label="不良类型" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="disposition" label="处理方式">
          <template #default="{ row }">
            <el-tag :type="getDispositionTagType(row.disposition)">{{ dispositionMap[row.disposition] || '待处理' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="disposition_date" label="处理日期">
          <template #default="{ row }">{{ formatDate(row.disposition_date) }}</template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleDispose(row)" v-if="!row.disposition">处理</el-button>
            <el-button size="small" @click="handleUpdate(row)" v-else>更新</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="处理不良品" width="400px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="不良类型">
          <el-input v-model="form.defect_type" disabled />
        </el-form-item>
        <el-form-item label="数量">
          <el-input v-model="form.quantity" disabled />
        </el-form-item>
        <el-form-item label="处理方式">
          <el-select v-model="form.disposition" placeholder="选择处理方式">
            <el-option label="报废" value="scrap" />
            <el-option label="返工" value="rework" />
            <el-option label="特采" value="special_accept" />
            <el-option label="退货" value="return" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getUnqualified, updateUnqualified } from '@/api'
import { ElMessage } from 'element-plus'

const records = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editId = ref(0)

const queryForm = reactive({ disposition: '' })
const form = reactive({
  defect_type: '',
  quantity: 0,
  disposition: null as string | null,
  remark: ''
})

const dispositionMap: Record<string, string> = { scrap: '报废', rework: '返工', special_accept: '特采', return: '退货' }

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.disposition) params.disposition = queryForm.disposition
    const res = await getUnqualified(params)
    records.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.disposition = ''
  loadData()
}

function getDispositionTagType(disposition: string): string {
  if (disposition === 'scrap') return 'danger'
  if (disposition === 'rework') return 'warning'
  if (disposition === 'special_accept') return 'success'
  if (disposition === 'return') return 'info'
  return ''
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

function handleDispose(row: any) {
  editId.value = row.id
  form.defect_type = row.defect_type
  form.quantity = row.quantity
  form.disposition = null
  form.remark = row.remark || ''
  dialogVisible.value = true
}

function handleUpdate(row: any) {
  editId.value = row.id
  form.defect_type = row.defect_type
  form.quantity = row.quantity
  form.disposition = row.disposition
  form.remark = row.remark || ''
  dialogVisible.value = true
}

async function submitForm() {
  if (!form.disposition) {
    return ElMessage.warning('请选择处理方式')
  }

  try {
    await updateUnqualified(editId.value, { disposition: form.disposition, remark: form.remark })
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (error) { ElMessage.error('保存失败') }
}

onMounted(() => loadData())
</script>