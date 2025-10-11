"""
该文件用于定义统一的API响应格式和自定义异常
继承HTTPException，统一错误码，避免重复，方便前端处理

定义错误码时遵循HTTP/1.1规范：
https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Status
"""

from typing import Any, Optional
from pydantic import BaseModel
from fastapi import HTTPException


class ErrorCode:
    """错误码定义"""
    # 成功
    SUCCESS = 0
    
    # 客户端错误 (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    
    # 服务器错误 (5xx)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    
    # 业务错误码 (自定义)
    DOCUMENT_UPLOAD_FAILED = 1001
    DOCUMENT_PROCESS_FAILED = 1002
    DOCUMENT_NOT_FOUND = 1003
    DOCUMENT_DELETE_FAILED = 1004
    UNSUPPORTED_FILE_TYPE = 1005
    FILE_TOO_LARGE = 1006
    
    RAG_QUERY_FAILED = 2001
    RAG_SEARCH_FAILED = 2002
    LLM_SERVICE_ERROR = 2003


class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int = ErrorCode.SUCCESS
    msg: str = "OK"
    data: Optional[Any] = None

    @staticmethod
    def success(data: Any = None, msg: str = "操作成功"):
        """成功响应"""
        return APIResponse(code=ErrorCode.SUCCESS, msg=msg, data=data)

    @staticmethod
    def error(code: int, msg: str = "操作失败", data: Any = None):
        """错误响应"""
        return APIResponse(code=code, msg=msg, data=data)
    
    @staticmethod
    def bad_request(msg: str = "请求参数错误", data: Any = None):
        """400 错误请求"""
        return APIResponse(code=ErrorCode.BAD_REQUEST, msg=msg, data=data)
    
    @staticmethod
    def not_found(msg: str = "资源不存在", data: Any = None):
        """404 资源不存在"""
        return APIResponse(code=ErrorCode.NOT_FOUND, msg=msg, data=data)
    
    @staticmethod
    def internal_error(msg: str = "服务器内部错误", data: Any = None):
        """500 服务器内部错误"""
        return APIResponse(code=ErrorCode.INTERNAL_SERVER_ERROR, msg=msg, data=data)
    
    @staticmethod
    def document_upload_failed(msg: str = "文档上传失败", data: Any = None):
        """文档上传失败"""
        return APIResponse(code=ErrorCode.DOCUMENT_UPLOAD_FAILED, msg=msg, data=data)
    
    @staticmethod
    def document_not_found(msg: str = "文档不存在", data: Any = None):
        """文档不存在"""
        return APIResponse(code=ErrorCode.DOCUMENT_NOT_FOUND, msg=msg, data=data)
    
    @staticmethod
    def unsupported_file_type(msg: str = "不支持的文件类型", data: Any = None):
        """不支持的文件类型"""
        return APIResponse(code=ErrorCode.UNSUPPORTED_FILE_TYPE, msg=msg, data=data)


class BusinessException(Exception):
    """业务异常基类"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class DocumentException(BusinessException):
    """文档相关异常"""
    pass


class RAGException(BusinessException):
    """RAG相关异常"""
    pass
