<template>
  <div class="inventory-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>库存查询</span>
        </div>
      </template>
      <el-table :data="stocks" v-loading="loading">
        <el-table-column prop="material_code" label="物料编码" />
        <el-table-column prop="material_name" label="物料名称" />
        <el-table-column prop="warehouse_name" label="仓库" />
        <el-table-column prop="quantity" label="当前库存" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const stocks = ref<any[]>([])
const loading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const res = await api.get('/inventory/stocks')
    stocks.value = res.data
  } catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}
onMounted(() => loadData())
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>