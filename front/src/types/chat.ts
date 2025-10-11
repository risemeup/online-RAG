/**
 * 聊天消息类型定义
 */
export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'system';
  timestamp: string;
  sources?: Array<{
    document_id: string;
    document_name: string;
    content: string;
    relevance_score: number;
  }>;
}

/**
 * 新的消息类型定义
 */
export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  sources?: SourceDocument[];
  // 保留原始问题（仅对assistant消息有效）
  originalQuestion?: string;
}



/**
 * 发送消息请求参数类型
 */
export interface SendMessageRequest {
  question: string;
  top_k?: number;
}

/**
 * API响应中的来源文档类型
 */
export interface SourceDocument {
  content: string;
  metadata: {
    chunk_id: string;
    content: string;
    doc_id: string;
    filename: string;
    source: string;
  };
}

/**
 * 问答API响应类型
 */
export interface QuestionAnswerResponse {
  answer: string;
  sources: SourceDocument[];
  question: string;
}

/**
 * 搜索文档请求参数类型
 */
export interface SearchDocumentsRequest {
  query: string;
  top_k?: number;
}

/**
 * 搜索结果类型定义
 */
export interface SearchResult {
  document_id: string;
  document_name: string;
  content: string;
  relevance_score: number;
}