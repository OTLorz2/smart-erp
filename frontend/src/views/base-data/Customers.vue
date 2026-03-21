<template>
  <div class="page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary" @click="handleAdd">新增客户</el-button>
        </div>
      </template>
      <el-table :data="customers" v-loading="loading">
        <el-table-column prop="code" label="编码" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="contact" label="联系人" />
        <el-table-column prop="phone" label="电话" />
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑' : '新增'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="编码"><el-input v-model="form.code" :disabled="isEdit" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
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
import { ElMessage } from 'element-plus'

const customers = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null as number|null, code: '', name: '', contact: '', phone: '' })

async function loadData() {
  loading.value = true
  try {
    const res = await api.get('/base-data/customers')
    customers.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function handleAdd() {
  isEdit.value = false; Object.assign(form, { id: null, code: '', name: '', contact: '', phone: '' }); dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (isEdit.value) await api.put(`/base-data/customers/${form.id}`, form)
    else await api.post('/base-data/customers', form)
    ElMessage.success('成功')
    dialogVisible.value = false
    loadData()
  } catch (error: any) { ElMessage.error(error.response?.data?.detail || '失败') }
}

onMounted(() => loadData())
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>