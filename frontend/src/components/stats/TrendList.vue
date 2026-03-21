<template>
  <el-card class="trend-list" :body-style="{ padding: '20px' }">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <el-radio-group v-model="timeRange" size="small" @change="loadData">
          <el-radio-button value="7">近7天</el-radio-button>
          <el-radio-button value="30">近30天</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>
    <div v-else class="trend-content">
      <div v-for="item in data" :key="item.date" class="trend-item">
        <span class="trend-date">{{ item.date }}</span>
        <span class="trend-value">{{ formatValue(item.amount) }}</span>
      </div>
      <el-empty v-if="!data.length" description="暂无数据" :image-size="60" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  type?: 'currency' | 'number'
  fetchData: (days: number) => Promise<{ date: string; amount: number }[]>
}>()

const loading = ref(false)
const data = ref<{ date: string; amount: number }[]>([])
const timeRange = ref('7')

const loadData = async () => {
  loading.value = true
  try {
    data.value = await props.fetchData(parseInt(timeRange.value))
  } catch (error) {
    console.error('Failed to load trend data:', error)
  } finally {
    loading.value = false
  }
}

const formatValue = (value: number) => {
  if (props.type === 'currency') {
    return `¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
  }
  return value.toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})

defineExpose({ reload: loadData })
</script>

<style scoped>
.trend-list {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
  font-size: 24px;
  color: #409eff;
}

.trend-content {
  max-height: 300px;
  overflow-y: auto;
}

.trend-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.trend-item:last-child {
  border-bottom: none;
}

.trend-date {
  color: #606266;
}

.trend-value {
  font-weight: 500;
  color: #303133;
}
</style>