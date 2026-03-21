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
      </el-menu>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <el-header>
        <div class="header-right">
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { House, Setting, Box, ShoppingCart, ShoppingBag } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeMenu = computed(() => route.path)

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
</style>