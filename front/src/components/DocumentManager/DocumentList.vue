<template>
  <div class="document-list">
    <el-card shadow="always">
      <template #header>
        <div class="card-header">
          <span>文档列表</span>
          <el-button type="text" @click="refreshList" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="documents"
        style="width: 100%"
        :empty-text="loading ? '加载中...' : '暂无文档，请先上传'"
      >
        <el-table-column prop="filename" label="文档名称" width="300">
          <template #default="{ row }">
            <el-link type="primary" @click="showDocumentDetail(row)">{{ row.filename }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ row.size ? formatFileSize(row.size) : '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            {{ getFileExtension(row.filename) }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ row.upload_time ? formatDate(row.upload_time) : '未知' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="text" danger @click="confirmDelete(row.id, row.filename)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useDocumentStore } from '../../store';
import type { Document } from '../../types/document';

const documentStore = useDocumentStore();

// 从store获取文档列表和加载状态
const documents = computed(() => documentStore.documents);
const loading = computed(() => documentStore.loading);

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 获取文件扩展名
const getFileExtension = (fileName: string | undefined): string => {
  if (!fileName) return '未知';
  const parts = fileName.split('.');
  return parts.length > 1 ? parts.pop()?.toUpperCase() || '' : '未知';
};

// 格式化日期
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '未知';
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date);
};

// 刷新文档列表
const refreshList = async () => {
  try {
    await documentStore.fetchDocumentList();
  } catch (error) {
    ElMessage.error('刷新文档列表失败');
  }
};

// 显示文档详情
const showDocumentDetail = (document: Document) => {
  ElMessageBox.alert(`
    文档名称: ${document.filename}
    文件大小: ${document.size ? formatFileSize(document.size) : '未知'}
    文件类型: ${getFileExtension(document.filename)}
    上传时间: ${document.upload_time ? formatDate(document.upload_time) : '未知'}
    文档ID: ${document.id}
  `, '文档详情', {
    confirmButtonText: '确定',
    type: 'info'
  });
};

// 确认删除文档
const confirmDelete = async (documentId: string, documentName: string | undefined) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档 "${documentName}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await documentStore.deleteDocumentApi(documentId);
    refreshList();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除文档失败');
    }
  }
};

// 组件挂载时获取文档列表
onMounted(() => {
  refreshList();
});
</script>

<style scoped>
.document-list {
  width: 100%;
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-table {
  margin-top: 10px;
}
</style>