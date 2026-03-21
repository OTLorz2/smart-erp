<template>
  <div class="order-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑销售订单' : '新建销售订单' }}</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="客户" prop="customer_id">
          <el-select v-model="form.customer_id" placeholder="请选择客户" filterable>
            <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="交货日期">
          <el-date-picker v-model="form.delivery_date" type="datetime" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider>订单明细</el-divider>
        <el-button type="primary" size="small" @click="addItem">添加物料</el-button>
        <el-table :data="form.items" style="margin-top: 15px">
          <el-table-column label="物料">
            <template #default="{ row, $index }">
              <el-select v-model="row.material_id" placeholder="选择物料" filterable @change="onMaterialChange($index)">
                <el-option v-for="m in materials" :key="m.id" :label="`${m.code} - ${m.name}`" :value="m.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0.01" :precision="2" @change="calcRowTotal(row)" />
            </template>
          </el-table-column>
          <el-table-column label="单价">
            <template #default="{ row }">
              <el-input-number v-model="row.unit_price" :min="0" :precision="2" @change="calcRowTotal(row)" />
            </template>
          </el-table-column>
          <el-table-column label="总价">
            <template #default="{ row }">{{ row.total_price }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 15px; text-align: right">
          <span>合计金额: <strong>{{ totalAmount }}</strong></span>
        </div>

        <el-form-item style="margin-top: 20px">
          <el-button type="primary" @click="submit" :loading="saving">保存</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCustomers, getMaterials, createSalesOrder, getSalesOrder, getSalesOrderItems } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({
  customer_id: null as number | null,
  delivery_date: null as Date | null,
  remark: '',
  items: [] as any[]
})

const rules = {
  customer_id: [{ required: true, message: '请选择客户', trigger: 'change' }]
}

const customers = ref<any[]>([])
const materials = ref<any[]>([])

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.total_price || 0), 0)
})

async function loadOptions() {
  const [cRes, mRes] = await Promise.all([getCustomers(), getMaterials()])
  customers.value = cRes.data
  materials.value = mRes.data
}

async function loadOrder() {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    const [orderRes, itemsRes] = await Promise.all([
      getSalesOrder(Number(id)),
      getSalesOrderItems(Number(id))
    ])
    form.customer_id = orderRes.data.customer_id
    form.delivery_date = orderRes.data.delivery_date ? new Date(orderRes.data.delivery_date) : null
    form.remark = orderRes.data.remark
    form.items = itemsRes.data.map((i: any) => ({
      material_id: i.material_id,
      quantity: Number(i.quantity),
      unit_price: Number(i.unit_price),
      total_price: Number(i.total_price)
    }))
  }
}

function addItem() {
  form.items.push({ material_id: null, quantity: 1, unit_price: 0, total_price: 0 })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

function onMaterialChange(index: number) {
  const item = form.items[index]
  const material = materials.value.find(m => m.id === item.material_id)
  if (material && item.unit_price === 0) {
    item.unit_price = Number(material.price) || 0
  }
  calcRowTotal(item)
}

function calcRowTotal(item: any) {
  item.total_price = (item.quantity || 0) * (item.unit_price || 0)
}

async function submit() {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = {
      customer_id: form.customer_id,
      delivery_date: form.delivery_date,
      remark: form.remark,
      items: form.items.filter(i => i.material_id).map(i => ({
        material_id: i.material_id,
        quantity: i.quantity,
        unit_price: i.unit_price,
        total_price: i.total_price
      }))
    }
    await createSalesOrder(data)
    ElMessage.success('创建成功')
    router.push('/sales/orders')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

function goBack() { router.back() }

onMounted(() => { loadOptions(); if (route.params.id) loadOrder() })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>