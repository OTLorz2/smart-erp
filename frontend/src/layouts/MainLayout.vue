<template>
  <el-container class="main-layout">
    <!-- Sidebar -->
    <el-aside width="220px">
      <div class="logo">
        <h3>Smart-ERP</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :router="true"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="base-data">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>基础数据</span>
          </template>
          <el-menu-item index="/users">用户管理</el-menu-item>
          <el-menu-item index="/materials">物料管理</el-menu-item>
          <el-menu-item index="/warehouses">仓库管理</el-menu-item>
          <el-menu-item index="/suppliers">供应商管理</el-menu-item>
          <el-menu-item index="/customers">客户管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory">库存查询</el-menu-item>
          <el-menu-item index="/inventory/records">出入库记录</el-menu-item>
          <el-menu-item index="/inventory/check">库存盘点</el-menu-item>
          <el-menu-item index="/inventory/alerts">库存预警</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="sales">
          <template #title>
            <el-icon><ShoppingCart /></el-icon>
            <span>销售管理</span>
          </template>
          <el-menu-item index="/sales/quotations">报价单</el-menu-item>
          <el-menu-item index="/sales/orders">销售订单</el-menu-item>
          <el-menu-item index="/sales/shipments">发货管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="purchase">
          <template #title>
            <el-icon><ShoppingBag /></el-icon>
            <span>采购管理</span>
          </template>
          <el-menu-item index="/purchase/quotations">询价单</el-menu-item>
          <el-menu-item index="/purchase/orders">采购订单</el-menu-item>
          <el-menu-item index="/purchase/receives">入库管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="production">
          <template #title>
            <el-icon><CPU /></el-icon>
            <span>生产管理</span>
          </template>
          <el-menu-item index="/production/boms">BOM配方</el-menu-item>
          <el-menu-item index="/production/routes">工艺路线</el-menu-item>
          <el-menu-item index="/production/orders">生产工单</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="quality">
          <template #title>
            <el-icon><CircleCheck /></el-icon>
            <span>质量管理</span>
          </template>
          <el-menu-item index="/quality/standards">质检标准</el-menu-item>
          <el-menu-item index="/quality/records">质检记录</el-menu-item>
          <el-menu-item index="/quality/unqualified">不良品管理</el-menu-item>
          <el-menu-item index="/quality/trace">质量追溯</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="reports">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>报表中心</span>
          </template>
          <el-menu-item index="/reports/inventory">库存报表</el-menu-item>
          <el-menu-item index="/reports/sales">销售报表</el-menu-item>
          <el-menu-item index="/reports/purchase">采购报表</el-menu-item>
          <el-menu-item index="/reports/production">生产报表</el-menu-item>
          <el-menu-item index="/reports/quality">质量报表</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <el-header>
        <div class="header-right">
          <!-- Notifications -->
          <el-popover placement="bottom" :width="320" trigger="click">
            <template #reference>
              <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
                <el-icon :size="20"><Bell /></el-icon>
              </el-badge>
            </template>
            <div class="notification-popover">
              <div class="notification-header">
                <span>通知中心</span>
                <el-button type="primary" link size="small" @click="markAllRead" v-if="notifications.length">
                  全部已读
                </el-button>
              </div>
              <div class="notification-list" v-if="notifications.length">
                <div
                  v-for="item in notifications"
                  :key="item.id"
                  class="notification-item"
                  :class="{ unread: !item.is_read }"
                  @click="handleNotificationClick(item)"
                >
                  <div class="notification-title">{{ item.title }}</div>
                  <div class="notification-content" v-if="item.content">{{ item.content }}</div>
                  <div class="notification-time">{{ formatTime(item.created_at) }}</div>
                </div>
              </div>
              <el-empty v-else description="暂无通知" :image-size="60" />
            </div>
          </el-popover>

          <span class="username">{{ authStore.user?.username }}</span>
          <el-button type="danger" link @click="handleLogout">
            退出登录
          </el-button>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { House, Setting, Box, ShoppingCart, ShoppingBag, CPU, CircleCheck, DataAnalysis, Bell } from '@element-plus/icons-vue'
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const notifications = ref<any[]>([])
const unreadCount = ref(0)

const activeMenu = computed(() => route.path)

const loadNotifications = async () => {
  try {
    const [notifRes, countRes] = await Promise.all([
      getNotifications({ limit: 10 }),
      getUnreadCount()
    ])
    notifications.value = notifRes.data
    unreadCount.value = countRes.data.unread_count
  } catch (error) {
    console.error('Failed to load notifications:', error)
  }
}

const handleNotificationClick = async (item: any) => {
  if (!item.is_read) {
    await markAsRead(item.id)
    item.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }
}

const markAllRead = async () => {
  try {
    await markAllAsRead()
    notifications.value.forEach((item: any) => item.is_read = true)
    unreadCount.value = 0
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  }
}

const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return time.slice(0, 10)
}

onMounted(() => {
  loadNotifications()
  // Refresh notifications every 60 seconds
  setInterval(loadNotifications, 60000)
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.el-aside {
  background: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #263445;
}

.logo h3 {
  color: #fff;
  margin: 0;
}

.el-menu-vertical {
  border: none;
  background: #304156;
}

.el-menu-item,
.el-sub-menu__title {
  color: #bfcbd9;
}

.el-menu-item:hover,
.el-sub-menu__title:hover {
  background: #263445 !important;
}

.el-menu-item.is-active {
  background: #409eff !important;
  color: #fff !important;
}

.el-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  color: #333;
}

.el-main {
  background: #f0f2f5;
  padding: 20px;
}

.notification-badge {
  cursor: pointer;
  padding: 4px;
}

.notification-popover {
  margin: -12px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 500;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #ecf5ff;
}

.notification-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.notification-content {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  font-size: 12px;
  color: #c0c4cc;
}
</style>