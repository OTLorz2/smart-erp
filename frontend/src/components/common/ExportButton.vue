<template>
  <el-dropdown @command="handleExport" trigger="click">
    <el-button type="primary" :icon="Download" :loading="loading">
      导出
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
        <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { exportData } from '@/api'

const props = defineProps<{
  dataType: string
}>()

const loading = ref(false)

const handleExport = async (format: string) => {
  loading.value = true
  try {
    const response = await exportData(props.dataType, format)
    const blob = new Blob([response.data], {
      type: format === 'excel'
        ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        : 'text/csv;charset=utf-8-sig'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.dataType}_${new Date().toISOString().slice(0, 10)}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  } finally {
    loading.value = false
  }
}
</script>