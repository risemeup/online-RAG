import { defineStore } from 'pinia';
import type { Message, QuestionAnswerResponse } from '../types/chat';
import service from '../utils/service';

// 用 defineStore 定义 Store，第一个参数是唯一 ID（必须，用于区分不同 Store）
export const useChatStore = defineStore('chat', {
  // 状态：存储数据的地方（类似 Vuex 的 state）
  state: () => ({
    messages: [] as Message[],
    loading: false
  }),

  // 计算属性：基于 state 派生的状态（类似 Vuex 的 getters）
  getters: {
    // 当前消息列表
    currentMessages: (state) => state.messages,
    
    // 消息总数
    messageCount: (state) => state.messages.length,
    
    // 是否有消息
    hasMessages: (state) => state.messages.length > 0,
    
    // 最后一条消息
    lastMessage: (state) => {
      return state.messages.length > 0 ? state.messages[state.messages.length - 1] : null;
    }
  },

  // 方法：处理业务逻辑（类似 Vuex 的 actions，可同步可异步）
  actions: {
    // ==================== API 请求方法 ====================
    
    // 发送问题到后端
    async sendQuestionApi(question: string) {
      return await service.post('/qa/query', { question }) as QuestionAnswerResponse;
    },

    // 搜索文档
    async searchDocumentsApi(query: string) {
      return await service.post('/qa/search', { query }) as Array<{
        document_id: string;
        document_name: string;
        content: string;
        score: number;
      }>;
    },

    // 获取文档统计信息
    async getDocumentStatsApi() {
      return await service.get('/qa/stats') as {
        total_documents: number;
        total_chunks: number;
        avg_chunk_size: number;
      };
    },

    // ==================== 业务逻辑方法 ====================
    
    // 发送消息
    async sendMessage(content: string) {
      this.loading = true;
      
      try {
        // 创建用户消息
        const userMessage: Message = {
          id: Date.now().toString(),
          content,
          role: 'user',
          timestamp: new Date().toISOString()
        };

        // 添加用户消息
        this.messages.push(userMessage);

        // 调用 API 发送消息
        const response = await this.sendQuestionApi(content);

        // 创建 AI 回复消息
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: response.answer,
          role: 'assistant',
          timestamp: new Date().toISOString(),
          sources: response.sources, // 添加引用源信息
          originalQuestion: content // 保存原始问题
        };

        // 添加 AI 消息
        this.messages.push(aiMessage);

      } catch (error) {
        console.error('发送消息失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 清空消息
    clearMessages() {
      this.messages = [];
    },

    // 搜索文档
    async searchDocuments(query: string) {
      try {
        return await this.searchDocumentsApi(query);
      } catch (error) {
        console.error('搜索文档失败:', error);
        throw error;
      }
    },

    // 获取文档统计
    async getDocumentStats() {
      try {
        return await this.getDocumentStatsApi();
      } catch (error) {
        console.error('获取文档统计失败:', error);
        throw error;
      }
    },
    

  }
});