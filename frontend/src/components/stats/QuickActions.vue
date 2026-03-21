<template>
  <el-card class="quick-actions" :body-style="{ padding: '20px' }">
    <template #header>
      <span>快捷操作</span>
    </template>
    <div class="actions-grid">
      <div
        v-for="action in actions"
        :key="action.key"
        class="action-item"
        @click="handleAction(action)"
      >
        <div class="action-icon" :style="{ backgroundColor: action.color }">
          <el-icon :size="20">
            <component :is="action.icon" />
          </el-icon>
        </div>
        <div class="action-label">{{ action.label }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  ShoppingCart,
  ShoppingCartFull,
  Box,
  Document,
  Plus,
  User
} from '@element-plus/icons-vue'

const router = useRouter()

interface Action {
  key: string
  label: string
  icon: any
  color: string
  path: string
}

const actions: Action[] = [
  { key: 'sales_order', label: '新建销售订单', icon: ShoppingCart, color: '#409eff', path: '/sales/orders/new' },
  { key: 'purchase_order', label: '新建采购订单', icon: ShoppingCartFull, color: '#67c23a', path: '/purchase/orders/new' },
  { key: 'production_order', label: '新建生产订单', icon: Box, color: '#e6a23c', path: '/production/orders/new' },
  { key: 'inventory_record', label: '库存流水', icon: Document, color: '#909399', path: '/inventory/records' },
  { key: 'material', label: '物料管理', icon: Plus, color: '#f56c6c', path: '/base-data/materials' },
  { key: 'customer', label: '客户管理', icon: User, color: '#c71585', path: '/base-data/customers' },
]

const handleAction = (action: Action) => {
  router.push(action.path)
}
</script>

<style scoped>
.quick-actions {
  height: 100%;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.action-item:hover {
  background-color: #f5f7fa;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.action-label {
  font-size: 12px;
  color: #606266;
  text-align: center;
}
</style>