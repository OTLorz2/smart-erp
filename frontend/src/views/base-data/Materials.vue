<template>
  <div class="materials-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>物料管理</span>
          <el-button type="primary" @click="handleAdd">新增物料</el-button>
        </div>
      </template>

      <el-table :data="materials" v-loading="loading">
        <el-table-column prop="code" label="物料编码" width="120" />
        <el-table-column prop="name" label="物料名称" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag>{{ categoryMap[row.category] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格型号" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="safety_stock" label="安全库存" width="100" />
        <el-table-column prop="price" label="参考单价" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑物料' : '新增物料'"
      width="500px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="物料编码" prop="code">
          <el-input v-model="form.code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="物料名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category">
            <el-option label="原材料" value="raw" />
            <el-option label="半成品" value="semi" />
            <el-option label="成品" value="finished" />
            <el-option label="消耗品" value="consumable" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格型号">
          <el-input v-model="form.specification" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" />
        </el-form-item>
        <el-form-item label="安全库存">
          <el-input-number v-model="form.safety_stock" :min="0" />
        </el-form-item>
        <el-form-item label="参考单价">
          <el-input-number v-model="form.price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'

const materials = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()

const categoryMap: Record<string, string> = {
  raw: '原材料',
  semi: '半成品',
  finished: '成品',
  consumable: '消耗品'
}

const form = reactive({
  id: null as number | null,
  code: '',
  name: '',
  category: 'raw',
  specification: '',
  unit: '',
  safety_stock: 0,
  price: 0,
  description: ''
})

const rules = {
  code: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入物料名称', trigger: 'blur' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }]
}

async function loadData() {
  loading.value = true
  try {
    const res = await api.get('/base-data/materials')
    materials.value = res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    code: '',
    name: '',
    category: 'raw',
    specification: '',
    unit: '',
    safety_stock: 0,
    price: 0,
    description: ''
  })
  dialogVisible.value = true
}

function handleEdit(row: any) {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      if (isEdit.value) {
        await api.put(`/base-data/materials/${form.id}`, form)
        ElMessage.success('更新成功')
      } else {
        await api.post('/base-data/materials', form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  })
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除该物料吗？', '提示', {
      type: 'warning'
    })
    // Soft delete - just mark as inactive
    await api.put(`/base-data/materials/${row.id}`, { is_active: false })
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    // User cancelled
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>