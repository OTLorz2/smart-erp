<template>
  <div class="dashboard">
    <h1>欢迎使用 Smart-ERP</h1>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><Box /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.materialCount }}</div>
              <div class="stat-label">物料总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><ShoppingCart /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.salesOrderCount }}</div>
              <div class="stat-label">销售订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><ShoppingBag /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.purchaseOrderCount }}</div>
              <div class="stat-label">采购订单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.alertCount }}</div>
              <div class="stat-label">库存预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/materials')">新增物料</el-button>
            <el-button type="success" @click="$router.push('/sales/orders')">新建销售订单</el-button>
            <el-button type="warning" @click="$router.push('/purchase/orders')">新建采购订单</el-button>
            <el-button type="info" @click="$router.push('/inventory')">库存查询</el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>库存预警</span>
          </template>
          <el-empty v-if="alerts.length === 0" description="暂无预警" />
          <el-table v-else :data="alerts" max-height="200">
            <el-table-column prop="material_code" label="物料编码" />
            <el-table-column prop="material_name" label="物料名称" />
            <el-table-column prop="current_quantity" label="当前库存" />
            <el-table-column prop="safety_stock" label="安全库存" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import { Box, ShoppingCart, ShoppingBag, Warning } from '@element-plus/icons-vue'

const stats = ref({
  materialCount: 0,
  salesOrderCount: 0,
  purchaseOrderCount: 0,
  alertCount: 0
})

const alerts = ref<any[]>([])

onMounted(async () => {
  try {
    const [materialsRes, salesRes, purchaseRes, alertsRes] = await Promise.all([
      api.get('/base-data/materials?limit=1'),
      api.get('/sales/orders?limit=1'),
      api.get('/purchase/orders?limit=1'),
      api.get('/inventory/alerts')
    ])

    stats.value.materialCount = materialsRes.data.length || 0
    stats.value.salesOrderCount = salesRes.data.length || 0
    stats.value.purchaseOrderCount = purchaseRes.data.length || 0
    stats.value.alertCount = alertsRes.data.length || 0
    alerts.value = alertsRes.data
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>

<style scoped>
.dashboard h1 {
  margin-bottom: 20px;
  color: #333;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 40px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  color: #999;
  font-size: 14px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
</style>