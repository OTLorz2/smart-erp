<template>
  <el-card class="alert-list" :body-style="{ padding: '20px' }">
    <template #header>
      <div class="card-header">
        <span>{{ title }}</span>
        <el-badge :value="alerts.length" :hidden="!alerts.length" type="warning">
          <el-button text @click="loadAlerts">刷新</el-button>
        </el-badge>
      </div>
    </template>
    <div v-if="loading" class="loading">
      <el-icon class="is-loading"><Loading /></el-icon>
    </div>
    <div v-else class="alert-content">
      <el-alert
        v-for="(alert, idx) in alerts"
        :key="idx"
        :title="alert.title"
        :type="alert.level === 'warning' ? 'warning' : 'info'"
        :description="alert.content"
        show-icon
        :closable="false"
        class="alert-item"
      />
      <el-empty v-if="!alerts.length" description="暂无预警" :image-size="60" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Alert {
  type: string
  level: string
  title: string
  content: string
}

const props = defineProps<{
  title: string
  fetchAlerts: () => Promise<Alert[]>
}>()

const loading = ref(false)
const alerts = ref<Alert[]>([])

const loadAlerts = async () => {
  loading.value = true
  try {
    alerts.value = await props.fetchAlerts()
  } catch (error) {
    console.error('Failed to load alerts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAlerts()
})

defineExpose({ reload: loadAlerts })
</script>

<style scoped>
.alert-list {
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

.alert-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.alert-item {
  margin: 0;
}
</style>