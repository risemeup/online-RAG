<template>
  <div class="chat-message" :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }">
    <div class="message-avatar">
      <el-avatar :icon="message.role === 'user' ? User : Bot" />
    </div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-sender">{{ message.role === 'user' ? '您' : 'AI助手' }}</span>
        <span class="message-time">{{ formatTime(message.timestamp) }}</span>
      </div>
      <div class="message-text" v-html="formattedContent"></div>
      <!-- 显示来源信息 -->
      <div v-if="message.sources && message.sources.length > 0" class="message-sources">
        <el-divider content-position="left">
          <el-icon><Document /></el-icon>
          参考来源 ({{ message.sources.length }})
        </el-divider>
        <el-collapse>
          <el-collapse-item name="sources">
            <template #title>
              <div class="sources-title">
                <el-icon><FolderOpened /></el-icon>
                <span>查看来源文档详情</span>
              </div>
            </template>
            <div class="sources-container">
              <div v-for="(source, index) in message.sources" :key="source.metadata.chunk_id" class="source-item">
                <div class="source-header">
                  <div class="source-info">
                    <el-tag type="info" size="small" class="source-index">{{ index + 1 }}</el-tag>
                    <el-link type="primary" @click="showSourceDetail(source)" class="source-filename">
                      <el-icon><Document /></el-icon>
                      {{ source.metadata.filename }}
                    </el-link>
                  </div>
                  <div class="source-meta">
                    <el-tag size="small" type="success">{{ source.metadata.chunk_id }}</el-tag>
                  </div>
                </div>
                <div class="source-content">
                  <div class="content-preview">{{ truncateContent(source.content, 200) }}</div>
                  <el-button 
                    v-if="source.content.length > 200" 
                    type="text" 
                    size="small" 
                    @click="toggleContentExpansion(index)"
                    class="expand-btn"
                  >
                    {{ expandedSources.has(index) ? '收起' : '展开全文' }}
                  </el-button>
                  <div v-if="expandedSources.has(index)" class="full-content">
                    {{ source.content }}
                  </div>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { User, Document, FolderOpened } from '@element-plus/icons-vue';
import { Avatar as Bot } from '@element-plus/icons-vue';
import { ElAvatar, ElDivider, ElLink, ElCollapse, ElCollapseItem, ElTag, ElButton, ElIcon } from 'element-plus';
import { marked } from 'marked';
import type { Message, SourceDocument } from '../../types/chat';

// 配置marked解析器
marked.setOptions({
  breaks: true,
  gfm: true
});

// Props
const props = defineProps<{
  message: Message;
}>();

// 响应式状态
const expandedSources = ref(new Set<number>());

// 格式化消息内容（Markdown解析）
const formattedContent = computed(() => {
  return marked(props.message.content);
});

// 截断内容
const truncateContent = (content: string, maxLength: number): string => {
  if (content.length <= maxLength) return content;
  return content.substring(0, maxLength) + '...';
};

// 切换内容展开状态
const toggleContentExpansion = (index: number) => {
  if (expandedSources.value.has(index)) {
    expandedSources.value.delete(index);
  } else {
    expandedSources.value.add(index);
  }
};

// 格式化时间
const formatTime = (timestamp: Date | string): string => {
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  const now = new Date();
  
  // 判断是否为今天
  const isToday = (d: Date): boolean => {
    return d.toDateString() === now.toDateString();
  };
  
  // 判断是否为昨天
  const isYesterday = (d: Date): boolean => {
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    return d.toDateString() === yesterday.toDateString();
  };
  
  // 如果是今天，则显示具体时间
  if (isToday(date)) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }
  // 如果是昨天，则显示"昨天"和具体时间
  else if (isYesterday(date)) {
    return `昨天 ${date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}`;
  }
  // 否则显示日期和时间
  else {
    return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
  }
};

// 显示来源文档详情
const showSourceDetail = (source: SourceDocument) => {
  // 这里可以实现显示来源文档详情的逻辑
  console.log('查看来源文档:', source);
  // 可以通过事件通知父组件显示文档详情
  // emit('showSourceDetail', source);
};
</script>

<style scoped>
.chat-message {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.user-message {
  flex-direction: row-reverse;
}

.assistant-message {
  flex-direction: row;
}

.message-avatar {
  margin: 0 12px;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.user-message .message-content {
  text-align: right;
}

.system-message .message-content {
  text-align: left;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
  color: #666;
}

.user-message .message-header {
  flex-direction: row-reverse;
}

.message-sender {
  font-weight: 500;
  margin-right: 8px;
}

.message-time {
  color: #999;
  margin-left: 8px;
}

.message-text {
  background-color: #f5f5f5;
  padding: 12px 16px;
  border-radius: 12px;
  word-wrap: break-word;
  text-align: left;
  line-height: 1.6;
}

.user-message .message-text {
  background-color: #409eff;
  color: white;
}

.message-text :deep(code) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  background-color: rgba(27, 31, 35, 0.05);
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 85%;
}

.message-text :deep(pre) {
  background-color: rgba(27, 31, 35, 0.05);
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
}

.user-message .message-text :deep(code) {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-message .message-text :deep(pre) {
  background-color: rgba(255, 255, 255, 0.1);
}

.message-sources {
  margin-top: 12px;
  padding-top: 8px;
}

.sources-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.sources-container {
  max-height: 400px;
  overflow-y: auto;
}

.source-item {
  margin-bottom: 12px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #409eff;
  transition: all 0.2s ease;
}

.source-item:hover {
  background-color: #f0f2f5;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.source-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.source-index {
  min-width: 24px;
  text-align: center;
}

.source-filename {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.source-meta {
  display: flex;
  gap: 6px;
}

.source-content {
  font-size: 14px;
  color: #333;
  line-height: 1.6;
}

.content-preview {
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.expand-btn {
  padding: 0;
  height: auto;
  font-size: 12px;
}

.full-content {
  margin-top: 8px;
  padding: 8px;
  background-color: #fff;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  white-space: pre-wrap;
  font-size: 13px;
  line-height: 1.5;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>