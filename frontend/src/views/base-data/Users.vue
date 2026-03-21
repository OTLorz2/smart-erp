<template>
  <div class="page">
    <el-card>
      <template #header><span>用户管理</span></template>
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">{{ roleMap[row.role] }}</template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const users = ref<any[]>([])
const loading = ref(false)
const roleMap: Record<string, string> = {
  admin: '管理员', sales: '业务员', warehouse: '仓库员', production: '生产员', qc: '质检员'
}

async function loadData() {
  loading.value = true
  try {
    const res = await api.get('/users')
    users.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
onMounted(() => loadData())
</script>