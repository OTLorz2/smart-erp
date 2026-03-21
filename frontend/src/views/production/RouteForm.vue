<template>
  <div class="route-form-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑工艺路线' : '新建工艺路线' }}</span>
        </div>
      </template>
      <el-form :model="form" label-width="120px">
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="选择产品" filterable>
            <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="form.version" placeholder="如: v1" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="草稿" value="draft" />
            <el-option label="生效" value="active" />
            <el-option label="作废" value="obsolete" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>

        <el-divider>工序步骤</el-divider>

        <div class="steps-header">
          <el-button type="primary" size="small" @click="addStep">添加工序</el-button>
        </div>
        <el-table :data="form.steps" border>
          <el-table-column label="工序序号" width="100">
            <template #default="{ row, $index }">
              <el-input-number v-model="row.step_no" :min="1" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column prop="step_name" label="工序名称" width="200">
            <template #default="{ row }">
              <el-input v-model="row.step_name" placeholder="工序名称" />
            </template>
          </el-table-column>
          <el-table-column prop="station_id" label="工站/设备" width="150">
            <template #default="{ row }">
              <el-select v-model="row.station_id" placeholder="选择设备" clearable filterable>
                <el-option v-for="m in materials" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="standard_time" label="标准工时(分)" width="120">
            <template #default="{ row }">
              <el-input-number v-model="row.standard_time" :min="0" :precision="2" controls-position="right" />
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注">
            <template #default="{ row }">
              <el-input v-model="row.remark" placeholder="备注" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ $index }">
              <el-button type="danger" size="small" @click="removeStep($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-form-item style="margin-top: 20px">
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getRoute, getRouteSteps, createRoute, updateRoute, updateRouteSteps, getMaterials } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const routeId = computed(() => Number(route.params.id))

const materials = ref<any[]>([])
const form = reactive({
  product_id: null as number | null,
  version: 'v1',
  status: 'draft',
  remark: '',
  steps: [] as any[]
})

onMounted(async () => {
  const matRes = await getMaterials()
  materials.value = matRes.data

  if (isEdit.value) {
    const res = await getRoute(routeId.value)
    const data = res.data
    form.product_id = data.product_id
    form.version = data.version
    form.status = data.status
    form.remark = data.remark || ''

    const stepsRes = await getRouteSteps(routeId.value)
    form.steps = stepsRes.data.map((s: any) => ({
      step_no: s.step_no,
      step_name: s.step_name,
      station_id: s.station_id,
      standard_time: s.standard_time,
      remark: s.remark || ''
    }))
  }
})

function addStep() {
  form.steps.push({ step_no: form.steps.length + 1, step_name: '', station_id: null, standard_time: 0, remark: '' })
}

function removeStep(index: number) {
  form.steps.splice(index, 1)
}

async function handleSubmit() {
  if (!form.product_id) {
    return ElMessage.warning('请选择产品')
  }

  try {
    if (isEdit.value) {
      await updateRoute(routeId.value, {
        version: form.version,
        status: form.status,
        remark: form.remark
      })
      await updateRouteSteps(routeId.value, form.steps)
      ElMessage.success('更新成功')
    } else {
      const res = await createRoute({
        product_id: form.product_id,
        version: form.version,
        remark: form.remark
      })
      if (form.steps.length > 0) {
        await updateRouteSteps(res.data.id, form.steps)
      }
      ElMessage.success('创建成功')
    }
    router.push('/production/routes')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.steps-header { margin-bottom: 10px; }
</style>