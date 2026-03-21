<template>
  <div class="order-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑工单' : '新建工单' }}</span>
        </div>
      </template>
      <el-form :model="form" label-width="120px">
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="选择产品" filterable @change="onProductChange">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划数量">
          <el-input-number v-model="form.quantity" :min="1" :precision="2" controls-position="right" />
        </el-form-item>
        <el-form-item label="计划开始日期">
          <el-date-picker v-model="form.start_date" type="datetime" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="计划结束日期">
          <el-date-picker v-model="form.end_date" type="datetime" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider>物料明细</el-divider>

        <div class="items-header">
          <el-button type="primary" size="small" @click="addItem">添加物料</el-button>
        </div>
        <el-table :data="form.items" border>
          <el-table-column label="物料" width="200">
            <template #default="{ row, $index }">
              <el-select v-model="row.material_id" placeholder="选择物料" filterable @change="onMaterialChange($index)">
                <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="material_name" label="物料名称" />
          <el-table-column label="用量" width="150">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0" :precision="2" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Report Production Section -->
        <template v-if="isEdit && currentOrder">
          <el-divider>报工记录</el-divider>
          <div class="report-section">
            <el-form :inline="true">
              <el-form-item label="报工数量">
                <el-input-number v-model="reportForm.quantity" :min="1" :precision="2" controls-position="right" />
              </el-form-item>
              <el-form-item label="备注">
                <el-input v-model="reportForm.remark" placeholder="备注" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleReport">提交报工</el-button>
              </el-form-item>
            </el-form>
          </div>
          <el-table :data="records" border v-if="records.length > 0">
            <el-table-column prop="quantity" label="报工数量" />
            <el-table-column prop="worker_id" label="报工人" />
            <el-table-column prop="created_at" label="报工时间">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="remark" label="备注" />
          </el-table>
        </template>

        <el-form-item style="margin-top: 20px">
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getProductionOrder, getProductionOrderItems, getProductionRecords,
  createProductionOrder, updateProductionOrder, updateProductionOrderItems,
  reportProduction, getMaterials
} from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const orderId = computed(() => Number(route.params.id))

const materials = ref<any[]>([])
const currentOrder = ref<any>(null)
const records = ref<any[]>([])

const form = reactive({
  product_id: null as number | null,
  quantity: 1,
  start_date: null as string | null,
  end_date: null as string | null,
  remark: '',
  items: [] as any[]
})

const reportForm = reactive({
  quantity: 1,
  remark: ''
})

onMounted(async () => {
  const matRes = await getMaterials()
  materials.value = matRes.data

  if (isEdit.value) {
    const res = await getProductionOrder(orderId.value)
    const data = res.data
    form.product_id = data.product_id
    form.quantity = data.quantity
    form.start_date = data.start_date
    form.end_date = data.end_date
    form.remark = data.remark || ''
    currentOrder.value = data

    const itemsRes = await getProductionOrderItems(orderId.value)
    form.items = itemsRes.data.map((item: any) => ({
      material_id: item.material_id,
      material_name: item.material?.name || '',
      quantity: item.quantity
    }))

    const recordsRes = await getProductionRecords(orderId.value)
    records.value = recordsRes.data
  }
})

function addItem() {
  form.items.push({ material_id: null, material_name: '', quantity: 0 })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

function onMaterialChange(index: number) {
  const item = form.items[index]
  const mat = materials.value.find(m => m.id === item.material_id)
  if (mat) item.material_name = mat.name
}

function onProductChange() {
  // Optional: auto-load BOM items when product is selected
}

async function handleSubmit() {
  if (!form.product_id) {
    return ElMessage.warning('请选择产品')
  }

  try {
    if (isEdit.value) {
      await updateProductionOrder(orderId.value, {
        quantity: form.quantity,
        start_date: form.start_date,
        end_date: form.end_date,
        remark: form.remark
      })
      await updateProductionOrderItems(orderId.value, form.items)
      ElMessage.success('更新成功')
    } else {
      const res = await createProductionOrder({
        product_id: form.product_id,
        quantity: form.quantity,
        start_date: form.start_date,
        end_date: form.end_date,
        remark: form.remark,
        items: form.items
      })
      ElMessage.success('创建成功')
    }
    router.push('/production/orders')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleReport() {
  if (!reportForm.quantity || reportForm.quantity <= 0) {
    return ElMessage.warning('请输入报工数量')
  }

  try {
    await reportProduction(orderId.value, {
      quantity: reportForm.quantity,
      remark: reportForm.remark
    })
    ElMessage.success('报工成功')
    reportForm.quantity = 1
    reportForm.remark = ''

    // Reload records
    const recordsRes = await getProductionRecords(orderId.value)
    records.value = recordsRes.data

    // Reload order to get updated completed_qty
    const orderRes = await getProductionOrder(orderId.value)
    currentOrder.value = orderRes.data
  } catch (error) {
    ElMessage.error('报工失败')
  }
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.items-header { margin-bottom: 10px; }
.report-section { margin-bottom: 15px; }
</style>