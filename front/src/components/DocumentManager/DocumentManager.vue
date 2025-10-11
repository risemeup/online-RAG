<template>
  <div class="document-manager">
    <el-card shadow="always">
      <template #header>
        <div class="card-header">
          <span>文档管理</span>
          <el-badge :value="documentCount" type="primary" />
        </div>
      </template>
      
      <DocumentUpload />
      <DocumentList />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import DocumentUpload from './DocumentUpload.vue';
import DocumentList from './DocumentList.vue';
import { useDocumentStore } from '../../store';

const documentStore = useDocumentStore();
const documentCount = computed(() => documentStore.documentCount);
</script>

<style scoped>
.document-manager {
  width: 100%;
  height: 100%;
}

.document-manager :deep(.el-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.document-manager :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>