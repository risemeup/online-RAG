<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="page-header">
          <h1>RAG智能文档助手</h1>
          <p>上传文档，构建知识库，获取智能回答</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="main-content">
      <!-- 文档管理区域 - 占比30% -->
      <el-col :span="7">
        <DocumentManager />
      </el-col>
      
      <!-- 智能问答区域 - 占比70% -->
      <el-col :span="17">
        <el-card shadow="always" class="chat-card">
          <template #header>
            <div class="card-header">
              <span>智能问答</span>
              <el-tag type="info" size="small">基于您上传的文档内容</el-tag>
            </div>
          </template>
          <ChatInterface />
        </el-card>
      </el-col>
    </el-row>

  </div>
</template>

<script setup lang="ts">
import DocumentManager from '../components/DocumentManager/DocumentManager.vue';
import ChatInterface from '../components/ChatInterface/ChatInterface.vue';
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  font-size: 36px;
  margin-bottom: 10px;
  font-weight: 600;
}

.page-header p {
  font-size: 18px;
  opacity: 0.9;
}

.main-content {
  min-height: calc(100vh - 200px);
}

.chat-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>