/**
 * 应用配置项
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 请求超时时间（毫秒）
export const REQUEST_TIMEOUT = 60000;

// 上传文件大小限制（字节）
export const FILE_SIZE_LIMIT = 50 * 1024 * 1024; // 50MB

// 支持的文件类型
export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain'
];

// 默认的top_k值
export const DEFAULT_TOP_K = 3;