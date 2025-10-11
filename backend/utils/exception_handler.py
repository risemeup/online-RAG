"""
全局异常处理器
统一处理各种异常，返回标准的APIResponse格式
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .response import APIResponse, ErrorCode, BusinessException, DocumentException, RAGException

# 配置日志
logger = logging.getLogger(__name__)


async def business_exception_handler(request: Request, exc: BusinessException) -> JSONResponse:
    """处理业务异常"""
    logger.warning(f"Business exception: {exc.message}")
    response = APIResponse.error(code=exc.code, msg=exc.message, data=exc.data)
    return JSONResponse(
        status_code=200,  # 业务异常返回200，通过code区分
        content=response.model_dump()
    )


async def document_exception_handler(request: Request, exc: DocumentException) -> JSONResponse:
    """处理文档相关异常"""
    logger.warning(f"Document exception: {exc.message}")
    
    # 根据错误码确定HTTP状态码
    http_status_code = 200
    if exc.code == ErrorCode.DOCUMENT_NOT_FOUND:
        http_status_code = 404
    elif exc.code == ErrorCode.BAD_REQUEST:
        http_status_code = 400
    elif exc.code == ErrorCode.FILE_TOO_LARGE:
        http_status_code = 413
    elif exc.code == ErrorCode.UNSUPPORTED_FILE_TYPE:
        http_status_code = 415
    elif exc.code == ErrorCode.INTERNAL_SERVER_ERROR:
        http_status_code = 500
    
    response = APIResponse.error(code=exc.code, msg=exc.message, data=exc.data)
    return JSONResponse(
        status_code=http_status_code,
        content=response.model_dump()
    )


async def rag_exception_handler(request: Request, exc: RAGException) -> JSONResponse:
    """处理RAG相关异常"""
    logger.warning(f"RAG exception: {exc.message}")
    response = APIResponse.error(code=exc.code, msg=exc.message, data=exc.data)
    return JSONResponse(
        status_code=200,
        content=response.model_dump()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    logger.warning(f"HTTP exception: {exc.detail}")
    
    # 根据HTTP状态码映射到错误码
    error_code_map = {
        400: ErrorCode.BAD_REQUEST,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        405: ErrorCode.METHOD_NOT_ALLOWED,
        409: ErrorCode.CONFLICT,
        422: ErrorCode.UNPROCESSABLE_ENTITY,
        500: ErrorCode.INTERNAL_SERVER_ERROR,
        501: ErrorCode.NOT_IMPLEMENTED,
        502: ErrorCode.BAD_GATEWAY,
        503: ErrorCode.SERVICE_UNAVAILABLE,
    }
    
    code = error_code_map.get(exc.status_code, exc.status_code)
    response = APIResponse.error(code=code, msg=str(exc.detail))
    
    return JSONResponse(
        status_code=200,  # 统一返回200，通过code区分错误
        content=response.model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    logger.warning(f"Validation exception: {exc.errors()}")
    
    # 提取验证错误信息
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_details.append(f"{field}: {message}")
    
    error_msg = "请求参数验证失败: " + "; ".join(error_details)
    response = APIResponse.bad_request(msg=error_msg, data=exc.errors())
    
    return JSONResponse(
        status_code=200,
        content=response.model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    response = APIResponse.internal_error(
        msg="服务器内部错误，请稍后重试",
        data={"error": str(exc)} if logger.isEnabledFor(logging.DEBUG) else None
    )
    
    return JSONResponse(
        status_code=200,
        content=response.model_dump()
    )


def register_exception_handlers(app):
    """注册异常处理器到FastAPI应用"""
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(DocumentException, document_exception_handler)
    app.add_exception_handler(RAGException, rag_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)