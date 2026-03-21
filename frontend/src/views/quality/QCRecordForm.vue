<template>
  <div class="qc-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '质检详情' : '新建质检单' }}</span>
        </div>
      </template>
      <el-form :model="form" label-width="120px">
        <el-form-item label="质检类型">
          <el-select v-model="form.qc_type" placeholder="选择类型" :disabled="isEdit">
            <el-option label="来料检验(IQC)" value="iqc" />
            <el-option label="制程检验(IPQC)" value="ipqc" />
            <el-option label="成品检验(OQC)" value="oqc" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料">
          <el-select v-model="form.material_id" placeholder="选择物料" filterable :disabled="isEdit">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="检验数量">
          <el-input-number v-model="form.quantity" :min="1" :precision="2" controls-position="right" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="form.batch_no" placeholder="可选" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <template v-if="isEdit && currentRecord">
          <el-divider>质检结果</el-divider>
          <el-form-item label="合格数量">
            <el-input-number v-model="resultForm.qualified_qty" :min="0" :max="form.quantity" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="不合格数量">
            <el-input-number v-model="resultForm.unqualified_qty" :min="0" :max="form.quantity" :precision="2" controls-position="right" />
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
          <el-form-item>
            <el-button type="primary" @click="submitResult">保存结果</el-button>
          </el-form-item>

          <el-divider>不良品登记</el-divider>
          <el-form :inline="true">
            <el-form-item label="不良类型">
              <el-input v-model="unqualifiedForm.defect_type" placeholder="如: 外观缺陷" />
            </el-form-item>
            <el-form-item label="数量">
              <el-input-number v-model="unqualifiedForm.quantity" :min="1" :precision="2" controls-position="right" />
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="addUnqualified">登记不良品</el-button>
            </el-form-item>
          </el-form>
          <el-table :data="unqualifiedList" border>
            <el-table-column prop="defect_type" label="不良类型" />
            <el-table-column prop="quantity" label="数量" />
            <el-table-column prop="disposition" label="处理方式">
              <template #default="{ row, $index }">
                <el-select v-model="row.disposition" placeholder="待处理" @change="updateDisposition($index)">
                  <el-option label="报废" value="scrap" />
                  <el-option label="返工" value="rework" />
                  <el-option label="特采" value="special_accept" />
                  <el-option label="退货" value="return" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="disposition_date" label="处理日期">
              <template #default="{ row }">{{ formatDate(row.disposition_date) }}</template>
            </el-table-column>
          </el-table>
        </template>

        <el-form-item style="margin-top: 20px">
          <el-button type="primary" @click="handleSubmit" v-if="!isEdit">创建</el-button>
          <el-button @click="router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getQCRecord, createQCRecord, updateQCResult, getUnqualified, createUnqualified, updateUnqualified, getMaterials } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const recordId = computed(() => Number(route.params.id))

const materials = ref<any[]>([])
const currentRecord = ref<any>(null)
const unqualifiedList = ref<any[]>([])

const form = reactive({
  qc_type: '',
  material_id: null as number | null,
  quantity: 1,
  batch_no: '',
  remark: ''
})

const resultForm = reactive({
  qualified_qty: 0,
  unqualified_qty: 0,
  result: 'passed',
  remark: ''
})

const unqualifiedForm = reactive({
  defect_type: '',
  quantity: 1
})

onMounted(async () => {
  const matRes = await getMaterials()
  materials.value = matRes.data

  if (isEdit.value) {
    const res = await getQCRecord(recordId.value)
    const data = res.data
    form.qc_type = data.qc_type
    form.material_id = data.material_id
    form.quantity = data.quantity
    form.batch_no = data.batch_no || ''
    form.remark = data.remark || ''
    currentRecord.value = data

    resultForm.qualified_qty = data.qualified_qty || 0
    resultForm.unqualified_qty = data.unqualified_qty || 0
    resultForm.result = data.result || 'passed'
    resultForm.remark = data.remark || ''

    // Load unqualified records
    const unRes = await getUnqualified({ qc_record_id: recordId.value })
    unqualifiedList.value = unRes.data || []
  }
})

async function handleSubmit() {
  if (!form.qc_type || !form.material_id) {
    return ElMessage.warning('请填写必填项')
  }

  try {
    await createQCRecord(form)
    ElMessage.success('创建成功')
    router.push('/quality/records')
  } catch (error) { ElMessage.error('创建失败') }
}

async function submitResult() {
  try {
    await updateQCResult(recordId.value, resultForm)
    ElMessage.success('保存成功')
  } catch (error) { ElMessage.error('保存失败') }
}

async function addUnqualified() {
  if (!unqualifiedForm.defect_type) {
    return ElMessage.warning('请输入不良类型')
  }

  try {
    await createUnqualified({
      qc_record_id: recordId.value,
      defect_type: unqualifiedForm.defect_type,
      quantity: unqualifiedForm.quantity
    })
    ElMessage.success('登记成功')
    unqualifiedForm.defect_type = ''
    unqualifiedForm.quantity = 1

    // Reload
    const unRes = await getUnqualified({ qc_record_id: recordId.value })
    unqualifiedList.value = unRes.data || []
  } catch (error) { ElMessage.error('登记失败') }
}

async function updateDisposition(index: number) {
  const item = unqualifiedList.value[index]
  try {
    await updateUnqualified(item.id, { disposition: item.disposition })
    ElMessage.success('更新成功')
  } catch (error) { ElMessage.error('更新失败') }
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>