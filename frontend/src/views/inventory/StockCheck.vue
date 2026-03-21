<template>
  <div class="stock-check-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存盘点</span>
        </div>
      </template>
      <el-alert title="库存盘点说明" type="info" :closable="false" style="margin-bottom: 20px">
        选择物料和仓库，输入实际盘点数量，系统将自动计算差异
      </el-alert>
      <el-form :inline="true" :model="checkForm">
        <el-form-item label="物料">
          <el-select v-model="checkForm.material_id" placeholder="请选择物料" filterable clearable>
            <el-option v-for="m in materials" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库">
          <el-select v-model="checkForm.warehouse_id" placeholder="请选择仓库" clearable>
            <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="实际数量">
          <el-input-number v-model="checkForm.actual_quantity" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="addCheckItem" :disabled="!canAdd">添加盘点项</el-button>
          <el-button type="success" @click="submitCheck" :loading="checking" :disabled="checkList.length === 0">提交盘点</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="checkList" style="margin-top: 20px" v-if="checkList.length > 0">
        <el-table-column prop="material_code" label="物料编码" />
        <el-table-column prop="material_name" label="物料名称" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="system_quantity" label="系统库存" />
        <el-table-column prop="actual_quantity" label="实际数量" />
        <el-table-column prop="difference" label="差异">
          <template #default="{ row }">
            <span :class="row.difference > 0 ? 'text-success' : row.difference < 0 ? 'text-danger' : ''">
              {{ row.difference > 0 ? '+' : '' }}{{ row.difference }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="{ $index }">
            <el-button type="danger" size="small" @click="removeCheckItem($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getMaterials, getWarehouses, getStocks, checkStock } from '@/api'
import { ElMessage } from 'element-plus'

const materials = ref<any[]>([])
const warehouses = ref<any[]>([])
const stocks = ref<any[]>([])

const checkForm = reactive({
  material_id: null as number | null,
  warehouse_id: null as number | null,
  actual_quantity: 0
})

const checkList = ref<any[]>([])
const checking = ref(false)

const canAdd = computed(() =>
  checkForm.material_id && checkForm.warehouse_id && checkForm.actual_quantity > 0
)

async function loadOptions() {
  const [mRes, wRes, sRes] = await Promise.all([
    getMaterials(),
    getWarehouses(),
    getStocks()
  ])
  materials.value = mRes.data
  warehouses.value = wRes.data
  stocks.value = sRes.data
}

function addCheckItem() {
  const material = materials.value.find(m => m.id === checkForm.material_id)
  const warehouse = warehouses.value.find(w => w.id === checkForm.warehouse_id)
  const stock = stocks.value.find(s =>
    s.material_id === checkForm.material_id && s.warehouse_id === checkForm.warehouse_id
  )

  if (!material || !warehouse) {
    ElMessage.warning('请选择物料和仓库')
    return
  }

  const systemQty = stock?.quantity || 0
  const diff = checkForm.actual_quantity - systemQty

  checkList.value.push({
    material_id: checkForm.material_id,
    material_code: material.code,
    material_name: material.name,
    warehouse_id: checkForm.warehouse_id,
    warehouse_name: warehouse.name,
    system_quantity: systemQty,
    actual_quantity: checkForm.actual_quantity,
    difference: diff
  })

  checkForm.material_id = null
  checkForm.warehouse_id = null
  checkForm.actual_quantity = 0
}

function removeCheckItem(index: number) {
  checkList.value.splice(index, 1)
}

async function submitCheck() {
  if (checkList.value.length === 0) return
  checking.value = true
  try {
    const data = checkList.value.map(item => ({
      material_id: item.material_id,
      warehouse_id: item.warehouse_id,
      actual_quantity: item.actual_quantity
    }))
    const res = await checkStock(data)
    ElMessage.success('盘点完成')
    console.log('盘点结果:', res.data)
    checkList.value = []
  } catch (error) {
    ElMessage.error('盘点失败')
  } finally {
    checking.value = false
  }
}

onMounted(() => loadOptions())
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-success {
  color: #67c23a;
}
.text-danger {
  color: #f56c6c;
}
</style>