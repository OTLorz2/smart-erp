<template>
  <div class="record-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑出入库单据' : '新建出入库单据' }}</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="单据类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择">
            <el-option label="采购入库" value="purchase_in" />
            <el-option label="生产入库" value="production_in" />
            <el-option label="其他入库" value="other_in" />
            <el-option label="销售出库" value="sales_out" />
            <el-option label="生产领料" value="production_out" />
            <el-option label="其他出库" value="other_out" />
          </el-select>
        </el-form-item>
        <el-form-item label="物料" prop="material_id">
          <el-select v-model="form.material_id" placeholder="请选择物料" filterable>
            <el-option v-for="m in materials" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库" prop="warehouse_id">
          <el-select v-model="form.warehouse_id" placeholder="请选择仓库">
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="单价" prop="unit_price">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="form.batch_no" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submit" :loading="saving">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMaterials, getWarehouses, createInventoryRecord, updateInventoryRecord, getInventoryRecord } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({
  type: '',
  material_id: null as number | null,
  warehouse_id: null as number | null,
  quantity: 1,
  unit_price: 0,
  batch_no: '',
  remark: ''
})

const rules = {
  type: [{ required: true, message: '请选择单据类型', trigger: 'change' }],
  material_id: [{ required: true, message: '请选择物料', trigger: 'change' }],
  warehouse_id: [{ required: true, message: '请选择仓库', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const materials = ref<any[]>([])
const warehouses = ref<any[]>([])

async function loadOptions() {
  const [mRes, wRes] = await Promise.all([
    getMaterials(),
    getWarehouses()
  ])
  materials.value = mRes.data
  warehouses.value = wRes.data
}

async function loadRecord() {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    const res = await getInventoryRecord(Number(id))
    Object.assign(form, res.data)
  }
}

async function submit() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateInventoryRecord(Number(route.params.id), form)
      ElMessage.success('更新成功')
    } else {
      await createInventoryRecord(form)
      ElMessage.success('创建成功')
    }
    router.push('/inventory/records')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  loadOptions()
  loadRecord()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>