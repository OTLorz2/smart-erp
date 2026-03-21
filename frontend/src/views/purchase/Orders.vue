<template>
  <div class="orders-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>采购订单</span>
          <el-button type="primary" @click="handleAdd">新建订单</el-button>
        </div>
      </template>
      <el-table :data="orders" v-loading="loading">
        <el-table-column prop="order_no" label="订单编号" />
        <el-table-column label="供应商" />
        <el-table-column prop="order_date" label="订单日期" />
        <el-table-column prop="total_amount" label="金额" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">{{ statusMap[row.status] }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const orders = ref<any[]>([])
const loading = ref(false)
const statusMap: Record<string, string> = {
  draft: '草稿', pending: '待审核', confirmed: '已确认', received: '已入库', completed: '已完成', cancelled: '已取消'
}

async function loadData() {
  loading.value = true
  try { const res = await api.get('/purchase/orders'); orders.value = res.data }
  catch (error) { ElMessage.error('加载失败') }
  finally { loading.value = false }
}

function handleAdd() { ElMessage.info('新建订单功能开发中') }
onMounted(() => loadData())
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center}</style>