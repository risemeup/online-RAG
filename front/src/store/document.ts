import { defineStore } from 'pinia';
import type { Document, DocumentUploadResponse, DocumentStats } from '../types/document';
import service from '../utils/service';

// 用 defineStore 定义 Store，第一个参数是唯一 ID（必须，用于区分不同 Store）
export const useDocumentStore = defineStore('document', {
  // 状态：存储数据的地方（类似 Vuex 的 state）
  state: () => ({
    documents: [] as Document[],
    loading: false,
    uploadProgress: 0,
    stats: {
      totalDocuments: 0,
      totalSize: 0,
      lastUpdated: null
    } as DocumentStats
  }),

  // 计算属性：基于 state 派生的状态（类似 Vuex 的 getters）
  getters: {
    // 文档总数
    documentCount: (state) => state.documents.length,
    
    // 总文件大小
     totalSize: (state) => {
       return state.documents.reduce((sum, doc) => sum + (doc.size || 0), 0);
     },

     // 按上传时间排序的文档列表
     sortedDocuments: (state) => {
       return [...state.documents].sort((a, b) => {
         const timeA = a.upload_time ? new Date(a.upload_time).getTime() : 0;
         const timeB = b.upload_time ? new Date(b.upload_time).getTime() : 0;
         return timeB - timeA;
       });
     },

    // 是否有文档
    hasDocuments: (state) => state.documents.length > 0,

    // 最近的文档（前5个）
    recentDocuments(): Document[] {
      return this.sortedDocuments.slice(0, 5);
    },

    // 按类型分组的文档
    documentsByType: (state) => {
      const grouped: Record<string, Document[]> = {};
      state.documents.forEach(doc => {
        const type = doc.type || 'unknown';
        if (!grouped[type]) {
          grouped[type] = [];
        }
        grouped[type].push(doc);
      });
      return grouped;
    }
  },

  // 方法：处理业务逻辑（类似 Vuex 的 actions，可同步可异步）
  actions: {
    // ==================== API 请求方法 ====================
    
    // 获取文档列表
    async fetchDocumentListApi() {
      return await service.get('/documents/list') as Document[];
    },

    // 上传文档
    async uploadDocumentApi(file: File, onProgress?: (progress: number) => void) {
      const formData = new FormData();
      formData.append('file', file);

      return await service.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      }) as DocumentUploadResponse;
    },

    // 删除文档
    async deleteDocumentApi(documentId: string) {
      return await service.delete(`/documents/${documentId}`);
    },

    // 获取文档统计
    async getDocumentStatsApi() {
      return await service.get('/documents/stats') as DocumentStats;
    },

    // 搜索文档
    async searchDocumentsApi(query: string) {
      return await service.post('/documents/search', { query }) as Document[];
    },

    // ==================== 业务逻辑方法 ====================
    
    // 获取文档列表
    async fetchDocumentList() {
      this.loading = true;
      try {
        const response = await this.fetchDocumentListApi();
        this.documents = response;
        return response;
      } catch (error) {
        console.error('获取文档列表失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 上传文档
    async uploadDocument(file: File) {
      this.loading = true;
      this.uploadProgress = 0;
      
      try {
        const response = await this.uploadDocumentApi(file, (progress) => {
          this.uploadProgress = progress;
        });
        
        // 添加新文档到列表
         const newDocument: Document = {
           id: response.document_id,
           filename: response.filename,
           type: file.type,
           size: file.size,
           upload_time: new Date().toISOString()
         };
        
        this.documents.unshift(newDocument);
        
        return response;
      } catch (error) {
        console.error('上传文档失败:', error);
        throw error;
      } finally {
        this.loading = false;
        this.uploadProgress = 0;
      }
    },

    // 删除文档
    async deleteDocument(documentId: string) {
      try {
        await this.deleteDocumentApi(documentId);
        
        // 从列表中移除文档
        const index = this.documents.findIndex(doc => doc.id === documentId);
        if (index > -1) {
          this.documents.splice(index, 1);
        }
        
        return true;
      } catch (error) {
        console.error('删除文档失败:', error);
        throw error;
      }
    },

    // 获取文档统计
    async getDocumentStats() {
      try {
        const response = await this.getDocumentStatsApi();
        this.stats = response;
        return response;
      } catch (error) {
        console.error('获取文档统计失败:', error);
        throw error;
      }
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

    // 根据ID查找文档
    findDocumentById(documentId: string) {
      return this.documents.find(doc => doc.id === documentId);
    },

    // 更新文档信息
     updateDocument(documentId: string, updates: Partial<Document>) {
       const document = this.findDocumentById(documentId);
       if (document) {
         Object.assign(document, updates);
       }
     },

    // 清空文档列表
    clearDocuments() {
      this.documents = [];
    },

    // 刷新统计信息
    async refreshStats() {
      this.stats = {
        totalDocuments: this.documentCount,
        totalSize: this.totalSize,
        lastUpdated: new Date()
      };
    }
  }
});