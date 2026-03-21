<template>
  <div>
    <el-button type="success" :icon="Upload" @click="openDialog">
      导入
    </el-button>

    <el-dialog v-model="dialogVisible" title="导入数据" width="500px">
      <div class="import-tips">
        <el-alert title="导入说明" type="info" :closable="false">
          <template #default>
            <p>1. 请先下载模板，按模板格式整理数据</p>
            <p>2. 支持 .xlsx 格式的 Excel 文件</p>
            <p>3. 请勿修改模板表头</p>
          </template>
        </el-alert>

        <div class="template-download">
          <el-button type="primary" link @click="downloadTemplate">
            <el-icon><Download /></el-icon>
            下载{{ title }}导入模板
          </el-button>
        </div>

        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".xlsx"
          drag
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处或 <em>点击上传</em>
          </div>
        </el-upload>

        <div v-if="selectedFile" class="file-info">
          <el-tag>{{ selectedFile.name }}</el-tag>
          <el-button type="primary" size="small" @click="validateFile" :loading="validating">
            验证数据
          </el-button>
        </div>

        <div v-if="validationResult" class="validation-result">
          <el-alert
            :type="validationResult.valid ? 'success' : 'error'"
            :title="validationResult.valid ? '验证通过' : '验证失败'"
          >
            <p v-if="validationResult.valid">
              共 {{ validationResult.totalRows }} 行数据待导入
            </p>
            <div v-else>
              <p v-for="(error, idx) in validationResult.errors" :key="idx">
                {{ error }}
              </p>
            </div>
          </el-alert>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmImport" :disabled="!validationResult?.valid">
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload, Download, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type UploadFile, type UploadRawFile } from 'element-plus'
import { downloadTemplate, validateImport } from '@/api'

const props = defineProps<{
  dataType: string
  title?: string
}>()

const dialogVisible = ref(false)
const uploadRef = ref()
const selectedFile = ref<UploadFile | null>(null)
const validating = ref(false)
const validationResult = ref<{ valid: boolean; totalRows?: number; errors?: string[] } | null>(null)

const openDialog = () => {
  dialogVisible.value = true
  selectedFile.value = null
  validationResult.value = null
}

const downloadTemplate = async () => {
  try {
    const response = await downloadTemplate(props.dataType)
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.dataType}_template.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error: any) {
    ElMessage.error(error.message || '模板下载失败')
  }
}

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file
  validationResult.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const validateFile = async () => {
  if (!selectedFile.value?.raw) return

  validating.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw as UploadRawFile)

    const response = await validateImport(formData, props.dataType)
    validationResult.value = response.data

    if (!response.data.valid) {
      ElMessage.error('数据验证失败')
    } else {
      ElMessage.success('数据验证通过')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '验证失败')
    validationResult.value = { valid: false, errors: [error.message] }
  } finally {
    validating.value = false
  }
}

const confirmImport = async () => {
  if (!selectedFile.value?.raw) return

  try {
    await ElMessageBox.confirm('确认导入数据？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    ElMessage.success('导入成功')
    dialogVisible.value = false
    emit('success')
  } catch {}
}

const emit = defineEmits(['success'])
</script>

<style scoped>
.import-tips {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.template-download {
  text-align: center;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.validation-result {
  margin-top: 12px;
}
</style>