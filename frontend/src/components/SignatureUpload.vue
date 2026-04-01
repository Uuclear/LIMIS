<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, Delete, Upload, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, UploadProps, UploadUserFile } from 'element-plus'
import { uploadSignature, deleteSignature, getMySignature } from '@/api/system'

const loading = ref(false)
const signatureUrl = ref<string | null>(null)
const hasSignature = ref(false)
const canSignReport = ref(false)
const signatureUpdatedAt = ref<string | null>(null)

// 文件上传列表
const fileList = ref<UploadUserFile[]>([])

// 是否可以上传
const canUpload = computed(() => {
  return !hasSignature.value
})

// 获取签名信息
async function fetchSignature() {
  try {
    const res: any = await getMySignature()
    if (res.code === 200) {
      hasSignature.value = res.data.has_signature
      signatureUrl.value = res.data.signature_url
      canSignReport.value = res.data.can_sign_report
      signatureUpdatedAt.value = res.data.signature_updated_at
    }
  } catch (error) {
    console.error('获取签名信息失败', error)
  }
}

// 上传前校验
const beforeUpload: UploadProps['beforeUpload'] = (rawFile) => {
  // 检查文件类型
  const isImage = ['image/png', 'image/jpeg', 'image/jpg'].includes(rawFile.type)
  if (!isImage) {
    ElMessage.error('签名文件格式仅支持PNG/JPG')
    return false
  }
  
  // 检查文件大小（2MB）
  const isLt2M = rawFile.size / 1024 / 1024 < 2
  if (!isLt2M) {
    ElMessage.error('签名文件大小不能超过2MB')
    return false
  }
  
  return true
}

// 自定义上传
const handleUpload: UploadProps['httpRequest'] = async (options) => {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('signature', options.file)
    
    const res: any = await uploadSignature(formData)
    if (res.code === 200) {
      ElMessage.success('签名上传成功')
      await fetchSignature()
      fileList.value = []
    } else {
      ElMessage.error(res.message || '上传失败')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    loading.value = false
  }
}

// 删除签名
async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除当前签名吗？删除后需要重新上传。', '提示', {
      type: 'warning',
    })
    
    loading.value = true
    const res: any = await deleteSignature()
    if (res.code === 200) {
      ElMessage.success('签名已删除')
      hasSignature.value = false
      signatureUrl.value = null
      canSignReport.value = false
      signatureUpdatedAt.value = null
    }
  } catch (error) {
    // 用户取消
  } finally {
    loading.value = false
  }
}

onMounted(fetchSignature)
</script>

<template>
  <el-card shadow="never" class="signature-upload">
    <template #header>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span>电子签名管理</span>
        <el-tag v-if="hasSignature" type="success" size="small">
          <el-icon><Check /></el-icon> 已上传
        </el-tag>
        <el-tag v-else type="warning" size="small">未上传</el-tag>
      </div>
    </template>
    
    <div class="signature-content">
      <!-- 签名预览 -->
      <div v-if="hasSignature && signatureUrl" class="signature-preview">
        <el-image 
          :src="signatureUrl" 
          fit="contain"
          style="width: 300px; height: 150px; border: 1px dashed #dcdfe6; border-radius: 4px;"
          :preview-src-list="[signatureUrl]"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Plus /></el-icon>
              <span>加载失败</span>
            </div>
          </template>
        </el-image>
        <div class="signature-info">
          <p v-if="signatureUpdatedAt">
            <span class="label">上传时间：</span>
            <span>{{ signatureUpdatedAt }}</span>
          </p>
          <p>
            <span class="label">签署权限：</span>
            <el-tag :type="canSignReport ? 'success' : 'danger'" size="small">
              {{ canSignReport ? '可签署报告' : '无签署权限' }}
            </el-tag>
          </p>
        </div>
      </div>
      
      <!-- 上传区域 -->
      <div v-if="!hasSignature" class="upload-area">
        <el-upload
          v-model:file-list="fileList"
          class="signature-uploader"
          :auto-upload="true"
          :show-file-list="false"
          :before-upload="beforeUpload"
          :http-request="handleUpload"
          accept=".png,.jpg,.jpeg"
          drag
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将签名图片拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PNG/JPG 格式，大小不超过 2MB
            </div>
          </template>
        </el-upload>
      </div>
      
      <!-- 操作按钮 -->
      <div class="signature-actions">
        <el-button 
          v-if="hasSignature"
          type="danger" 
          :icon="Delete" 
          :loading="loading"
          @click="handleDelete"
        >
          删除签名
        </el-button>
        
        <el-alert
          v-if="hasSignature && !canSignReport"
          type="warning"
          title="提示"
          description="您已上传签名，但暂无报告签署权限。请联系管理员分配授权签字人角色。"
          :closable="false"
          show-icon
          style="margin-top: 16px;"
        />
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.signature-upload {
  max-width: 600px;
}

.signature-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.signature-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.signature-info {
  text-align: center;
}

.signature-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
}

.signature-info .label {
  color: #909399;
}

.upload-area {
  display: flex;
  justify-content: center;
}

.signature-uploader {
  width: 100%;
}

.signature-uploader :deep(.el-upload-dragger) {
  width: 300px;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.image-error {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
}

.signature-actions {
  display: flex;
  justify-content: center;
}
</style>