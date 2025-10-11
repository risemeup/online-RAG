<template>
  <div class="document-upload">
    <el-upload
      class="upload-demo"
      :action="uploadUrl"
      :on-success="handleSuccess"
      :on-error="handleError"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      :file-list="fileList"
      :auto-upload="false"
      drag
      multiple
    >
      <el-icon><Upload /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip text-center">
          支持 PDF、Word、文本等格式文件，单个文件不超过50MB
        </div>
      </template>
    </el-upload>
    <div class="upload-actions">
      <el-button type="primary" @click="submitUpload" :loading="uploading">
        开始上传
      </el-button>
      <el-button @click="clearFiles">清空列表</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage, ElUpload, ElButton, ElIcon } from 'element-plus';
import { Upload } from '@element-plus/icons-vue';
import { API_BASE_URL, FILE_SIZE_LIMIT, SUPPORTED_FILE_TYPES } from '../../utils/config';
import { useDocumentStore } from '../../store';
import type { UploadProps, UploadFile } from 'element-plus';

const documentStore = useDocumentStore();
const uploading = ref(false);
const fileList = ref<UploadFile[]>([]);

// 上传URL
const uploadUrl = computed(() => `${API_BASE_URL}/documents/`);

// 提交上传
const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件');
    return;
  }

  uploading.value = true;

  try {
    // 逐个上传文件
    for (const uploadFile of fileList.value) {
      if (uploadFile.raw) {
        await documentStore.uploadDocument(uploadFile.raw);
      }
    }
    
    // 上传完成后清空文件列表
    fileList.value = [];
    
    // 重新获取文档列表
    await documentStore.fetchDocumentList();
  } catch (error) {
    console.error('上传文件失败:', error);
  } finally {
    uploading.value = false;
  }
};

// 清空文件列表
const clearFiles = () => {
  fileList.value = [];
};

// 处理文件选择变化
const handleFileChange: UploadProps['onChange'] = (_uploadFile, uploadFiles) => {
  // 更新文件列表
  fileList.value = uploadFiles;
};

// 文件上传前的校验
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 检查文件大小
  const isLt50M = file.size < FILE_SIZE_LIMIT;
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB!');
    return false;
  }

  // 检查文件类型
  const isTypeValid = SUPPORTED_FILE_TYPES.includes(file.type);
  if (!isTypeValid) {
    ElMessage.error('只支持PDF、Word、文本等格式的文件!');
    return false;
  }

  return false; // 阻止自动上传，使用手动上传
};

// 上传成功处理
const handleSuccess: UploadProps['onSuccess'] = (_response, uploadFile) => {
  ElMessage.success(`${uploadFile.name} 上传成功`);
};

// 上传失败处理
const handleError: UploadProps['onError'] = (error, uploadFile) => {
  ElMessage.error(`${uploadFile.name} 上传失败`);
  console.error('文件上传失败:', error);
};
</script>

<style scoped>
.document-upload {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.upload-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}
</style>