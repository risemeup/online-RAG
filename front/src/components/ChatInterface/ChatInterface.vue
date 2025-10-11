<template>
  <div class="chat-interface">
    <div class="chat-header">
      <h2>RAG智能文档助手</h2>
      <el-button type="text" @click="clearChat">
        <el-icon><Delete /></el-icon>
        清空聊天
      </el-button>
    </div>
    
    <div class="chat-messages" ref="chatContainer">

      <!-- 欢迎消息 -->
      <div v-if="!hasMessages" class="welcome-message">
        <el-empty description="暂无聊天记录，上传文档后开始提问吧！" />
      </div>
      
      <!-- 消息列表 -->
      <ChatMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
      />
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-indicator">
        <el-skeleton :rows="2" animated />
      </div>
    </div>
    
    <div class="chat-input-area">
      <div class="input-wrapper">
        <el-input
          v-model="question"
          placeholder="请输入您的问题..."
          :disabled="loading"
          @keydown="handleKeyDown"
          type="textarea"
          :rows="3"
          class="message-input"
        />
        <el-button 
          type="primary" 
          @click="sendMessage" 
          :loading="loading"
          :disabled="!question.trim() || loading"
          size="small"
          class="embedded-send-button"
          circle
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
      <div class="input-tips">
        <small>提示：按 Enter 发送消息，Shift + Enter 换行，支持 Markdown 格式</small>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { ElMessage, ElMessageBox, ElEmpty, ElSkeleton } from 'element-plus';
import { Delete, Promotion } from '@element-plus/icons-vue';
import { useChatStore } from '../../store';
import ChatMessage from './ChatMessage.vue';

const chatStore = useChatStore();
const question = ref('');
const chatContainer = ref<HTMLElement | null>(null);

// 从store获取消息列表、加载状态和是否有消息的状态
const messages = computed(() => chatStore.currentMessages);
const loading = computed(() => chatStore.loading);
const hasMessages = computed(() => chatStore.currentMessages.length > 0);

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};

// 处理键盘事件
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    if (event.shiftKey) {
      // Shift + Enter: 换行，不做任何处理，让默认行为发生
      return;
    } else {
      // 单独的 Enter: 发送消息
      event.preventDefault();
      sendMessage();
    }
  }
};

// 发送消息
const sendMessage = async () => {
  const trimmedQuestion = question.value.trim();
  
  if (!trimmedQuestion) {
    ElMessage.warning('请输入问题内容');
    return;
  }
  
  if (loading.value) {
    return;
  }
  
  try {
    // 清空输入框
    question.value = '';
    
    // 发送问题
    await chatStore.sendMessage(trimmedQuestion);
    
    // 滚动到底部
    scrollToBottom();
  } catch (error) {
    console.error('发送消息失败:', error);
    ElMessage.error('发送消息失败，请重试');
  }
};

// 清空聊天记录
const clearChat = async () => {
  try {
    await ElMessageBox.confirm('确定要清空当前聊天记录吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    
    chatStore.clearMessages();
    ElMessage.success('聊天记录已清空');
  } catch {
    // 用户取消操作
  }
};



// 监听消息变化，自动滚动到底部
// const unwatchMessages = chatStore.$subscribe((mutation, state) => {
//   if (mutation.events.includes('messages')) {
//     scrollToBottom();
//   }
// });

// 组件挂载时滚动到底部
onMounted(() => {
  scrollToBottom();
});

// 组件卸载时取消监听
// onUnmounted(() => {
//   unwatchMessages();
// });
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  background-color: #fff;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #e6e6e6;
  background-color: #fafafa;
}

.chat-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #fafafa;
}

.welcome-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.loading-indicator {
  padding: 20px;
  display: flex;
  justify-content: center;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
  background-color: #fff;
}

.input-wrapper {
  position: relative;
}

.message-input {
  width: 100%;
}

.embedded-send-button {
  position: absolute;
  right: 8px;
  bottom: 8px;
  z-index: 10;
  width: 32px;
  height: 32px;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.embedded-send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.embedded-send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 调整textarea的样式，确保文本不会被按钮遮挡 */
.message-input :deep(.el-textarea__inner) {
  padding-right: 45px !important;
  padding-bottom: 45px !important;
  resize: none;
  border-radius: 8px;
}

.input-tips {
  margin-top: 10px;
  text-align: right;
}

.input-tips small {
  color: #999;
  font-size: 12px;
}

/* 自定义滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>