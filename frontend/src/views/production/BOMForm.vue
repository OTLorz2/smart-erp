<template>
  <div class="bom-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑BOM' : '新建BOM' }}</span>
        </div>
      </template>
      <el-form :model="form" label-width="120px">
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="选择产品" filterable @change="loadBOMItems">
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" placeholder="如: v1" />
        </el-form-item>
        <el-form-item label="生效日期">
          <el-date-picker v-model="form.effective_date" type="datetime" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
            <el-option label="生效" value="active" />
            <el-option label="作废" value="obsolete" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider>配方明细</el-divider>

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
          <el-table-column label="用量" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="0" :precision="4" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column label="损耗率%" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.scrap_rate" :min="0" :max="100" :precision="2" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeItem($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

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
import { getBOM, getBOMItems, createBOM, updateBOM, updateBOMItems, getMaterials } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const bomId = computed(() => Number(route.params.id))

const materials = ref<any[]>([])
const form = reactive({
  product_id: null as number | null,
  version: 'v1',
  effective_date: null as string | null,
  status: 'draft',
  remark: '',
  items: [] as any[]
})

onMounted(async () => {
  // Load materials
  const matRes = await getMaterials()
  materials.value = matRes.data

  if (isEdit.value) {
    const res = await getBOM(bomId.value)
    const data = res.data
    form.product_id = data.product_id
    form.version = data.version
    form.effective_date = data.effective_date
    form.status = data.status
    form.remark = data.remark || ''

    const itemsRes = await getBOMItems(bomId.value)
    form.items = itemsRes.data.map((item: any) => ({
      material_id: item.material_id,
      material_name: item.material?.name || '',
      quantity: item.quantity,
      scrap_rate: item.scrap_rate
    }))
  }
})

function addItem() {
  form.items.push({ material_id: null, material_name: '', quantity: 0, scrap_rate: 0 })
}

function removeItem(index: number) {
  form.items.splice(index, 1)
}

function onMaterialChange(index: number) {
  const item = form.items[index]
  const mat = materials.value.find(m => m.id === item.material_id)
  if (mat) item.material_name = mat.name
}

async function handleSubmit() {
  if (!form.product_id) {
    return ElMessage.warning('请选择产品')
  }

  try {
    if (isEdit.value) {
      await updateBOM(bomId.value, {
        version: form.version,
        effective_date: form.effective_date,
        status: form.status,
        remark: form.remark
      })
      await updateBOMItems(bomId.value, form.items)
      ElMessage.success('更新成功')
    } else {
      const res = await createBOM({
        product_id: form.product_id,
        version: form.version,
        effective_date: form.effective_date,
        remark: form.remark
      })
      if (form.items.length > 0) {
        await updateBOMItems(res.data.id, form.items)
      }
      ElMessage.success('创建成功')
    }
    router.push('/production/boms')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function loadBOMItems() {
  // Optional: load existing BOM items if selecting from existing BOM
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.items-header { margin-bottom: 10px; }
</style>