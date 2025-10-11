/**
 * 文档信息类型定义
 */
export interface Document {
  id: string;
  filename: string;
  size?: number;
  type?: string;
  upload_time?: string;
  content?: string;
}

/**
 * 上传文档请求参数类型
 */
export interface UploadDocumentRequest {
  file: File;
}

/**
 * 删除文档请求参数类型
 */
export interface DeleteDocumentRequest {
  documentId: string;
}

/**
 * 文档上传响应类型
 */
export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  message: string;
}

/**
 * 文档统计信息类型
 */
export interface DocumentStats {
  totalDocuments: number;
  totalSize: number;
  lastUpdated: Date | null;
}