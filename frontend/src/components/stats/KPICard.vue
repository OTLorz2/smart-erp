<template>
  <el-card class="kpi-card" :body-style="{ padding: '20px' }">
    <div class="kpi-content">
      <div class="kpi-icon" :style="{ backgroundColor: bgColor }">
        <el-icon :size="24">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="kpi-data">
        <div class="kpi-value">{{ formatValue }}</div>
        <div class="kpi-label">{{ label }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  value: number | string
  label: string
  icon: any
  type?: 'currency' | 'number' | 'percent' | 'text'
  bgColor?: string
}>()

const formatValue = computed(() => {
  if (props.type === 'currency') {
    return `¥${Number(props.value).toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
  } else if (props.type === 'percent') {
    return `${props.value}%`
  } else if (props.type === 'number') {
    return Number(props.value).toLocaleString('zh-CN')
  }
  return props.value
})
</script>

<style scoped>
.kpi-card {
  height: 100%;
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.kpi-data {
  flex: 1;
}

.kpi-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.kpi-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>