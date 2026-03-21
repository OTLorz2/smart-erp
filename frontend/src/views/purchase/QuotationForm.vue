<template>
  <div class="quotation-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑询价单' : '新建询价单' }}</span>
        </div>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" placeholder="请选择供应商" filterable>
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="回复日期">
          <el-date-picker v-model="form.reply_date" type="datetime" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider>询价明细</el-divider>
        <el-button type="primary" size="small" @click="addItem">添加物料</el-button>
        <el-table :data="form.items" style="margin-top: 15px">
          <el-table-column label="物料">
            <template #default="{ row, $index }">
              <el-select v-model="row.material_id" placeholder="选择物料" filterable>
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
import { getSuppliers, getMaterials, createPurchaseQuotation, updatePurchaseQuotation, getPurchaseQuotation } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({
  supplier_id: null as number | null,
  reply_date: null as Date | null,
  remark: '',
  items: [] as any[]
})

const rules = {
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }]
}

const suppliers = ref<any[]>([])
const materials = ref<any[]>([])

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + (item.total_price || 0), 0)
})

async function loadOptions() {
  const [sRes, mRes] = await Promise.all([getSuppliers(), getMaterials()])
  suppliers.value = sRes.data
  materials.value = mRes.data
}

async function loadQuotation() {
  const id = route.params.id
  if (id) {
    isEdit.value = true
    const res = await getPurchaseQuotation(Number(id))
    Object.assign(form, res.data)
    if (!form.items) form.items = []
  }
}

function addItem() {
  form.items.push({ material_id: null, quantity: 1, unit_price: 0, total_price: 0 })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

function calcRowTotal(item: any) {
  item.total_price = (item.quantity || 0) * (item.unit_price || 0)
}

async function submit() {
  await formRef.value.validate()
  saving.value = true
  try {
    const data = {
      supplier_id: form.supplier_id,
      reply_date: form.reply_date,
      remark: form.remark,
      items: form.items.filter(i => i.material_id).map(i => ({
        material_id: i.material_id,
        quantity: i.quantity,
        unit_price: i.unit_price,
        total_price: i.total_price
      }))
    }
    if (isEdit.value) {
      await updatePurchaseQuotation(Number(route.params.id), data)
      ElMessage.success('更新成功')
    } else {
      await createPurchaseQuotation(data)
      ElMessage.success('创建成功')
    }
    router.push('/purchase/quotations')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

function goBack() { router.back() }

onMounted(() => { loadOptions(); loadQuotation() })
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>