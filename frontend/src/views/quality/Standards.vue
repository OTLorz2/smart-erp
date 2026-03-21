<template>
  <div class="standards-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>质检标准</span>
          <el-button type="primary" @click="showDialog = true">新建标准</el-button>
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
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="standards" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="material_id" label="物料ID" />
        <el-table-column prop="qc_type" label="质检类型">
          <template #default="{ row }">{{ qcTypeMap[row.qc_type] }}</template>
        </el-table-column>
        <el-table-column prop="item_name" label="检验项目" />
        <el-table-column prop="standard" label="标准值" />
        <el-table-column prop="tolerance" label="公差范围" />
        <el-table-column prop="inspector_level" label="检验等级" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" :title="isEdit ? '编辑标准' : '新建标准'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="物料">
          <el-select v-model="form.material_id" placeholder="选择物料" filterable>
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="质检类型">
          <el-select v-model="form.qc_type" placeholder="选择类型">
            <el-option label="来料检验(IQC)" value="iqc" />
            <el-option label="制程检验(IPQC)" value="ipqc" />
            <el-option label="成品检验(OQC)" value="oqc" />
          </el-select>
        </el-form-item>
        <el-form-item label="检验项目">
          <el-input v-model="form.item_name" />
        </el-form-item>
        <el-form-item label="标准值">
          <el-input v-model="form.standard" />
        </el-form-item>
        <el-form-item label="公差范围">
          <el-input v-model="form.tolerance" />
        </el-form-item>
        <el-form-item label="检验等级">
          <el-input v-model="form.inspector_level" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getQCStandards, createQCStandard, updateQCStandard, deleteQCStandard, getMaterials } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const standards = ref<any[]>([])
const materials = ref<any[]>([])
const loading = ref(false)
const showDialog = ref(false)
const isEdit = ref(false)
const editId = ref(0)

const queryForm = reactive({ qc_type: '' })
const form = reactive({
  material_id: null as number | null,
  qc_type: '',
  item_name: '',
  standard: '',
  tolerance: '',
  inspector_level: '',
  remark: ''
})

const qcTypeMap: Record<string, string> = { iqc: 'IQC', ipqc: 'IPQC', oqc: 'OQC' }

async function loadData() {
  loading.value = true
  try {
    const params: any = {}
    if (queryForm.qc_type) params.qc_type = queryForm.qc_type
    const res = await getQCStandards(params)
    standards.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function resetQuery() {
  queryForm.qc_type = ''
  loadData()
}

async function loadMaterials() {
  const res = await getMaterials()
  materials.value = res.data
}

function handleEdit(row: any) {
  isEdit.value = true
  editId.value = row.id
  form.material_id = row.material_id
  form.qc_type = row.qc_type
  form.item_name = row.item_name
  form.standard = row.standard || ''
  form.tolerance = row.tolerance || ''
  form.inspector_level = row.inspector_level || ''
  form.remark = row.remark || ''
  showDialog.value = true
}

async function handleSubmit() {
  if (!form.material_id || !form.qc_type || !form.item_name) {
    return ElMessage.warning('请填写必填项')
  }

  try {
    if (isEdit.value) {
      await updateQCStandard(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createQCStandard(form)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    loadData()
    resetForm()
  } catch (error) { ElMessage.error('操作失败') }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确认删除此标准?', '提示', { type: 'warning' })
    await deleteQCStandard(id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function resetForm() {
  isEdit.value = false
  editId.value = 0
  form.material_id = null
  form.qc_type = ''
  form.item_name = ''
  form.standard = ''
  form.tolerance = ''
  form.inspector_level = ''
  form.remark = ''
}

onMounted(() => { loadData(); loadMaterials() })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>