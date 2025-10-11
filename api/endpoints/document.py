from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from services.document_service import DocumentService
from utils.response import APIResponse, ErrorCode, DocumentException
from utils.logger import get_logger

router = APIRouter(
    prefix="",
    tags=["documents"],
    responses={404: {"description": "Not found"}}
)

document_service = DocumentService()
logger = get_logger(name="document")

@router.post("/upload", response_model=APIResponse)
async def upload_document(
    file: UploadFile = File(...),
):
    """上传并处理文档
    
    Args:
        file: 要上传的文件
    
    Returns:
        处理结果
    """
    logger.info(f"开始上传文档: {file.filename}")
    
    # 验证文件
    if not file.filename:
        logger.warning("文档上传失败: 文件名为空")
        raise DocumentException(
            code=ErrorCode.BAD_REQUEST,
            message="文件名不能为空"
        )
    
    # 检查文件类型
    allowed_extensions = {'.txt', '.pdf', '.docx', '.doc'}
    file_extension = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    if file_extension not in allowed_extensions:
        logger.warning(f"文档上传失败: 不支持的文件类型 {file_extension}")
        raise DocumentException(
            code=ErrorCode.UNSUPPORTED_FILE_TYPE,
            message=f"不支持的文件类型: {file_extension}。支持的类型: {', '.join(allowed_extensions)}"
        )
    
    # 检查文件大小 (限制为10MB)
    file_data = await file.read()
    max_size = 10 * 1024 * 1024  # 10MB
    
    if len(file_data) > max_size:
        logger.warning(f"文档上传失败: 文件大小超限 {len(file_data)} bytes")
        raise DocumentException(
            code=ErrorCode.FILE_TOO_LARGE,
            message=f"文件大小超过限制 ({max_size // (1024*1024)}MB)"
        )
    
    if len(file_data) == 0:
        logger.warning("文档上传失败: 文件内容为空")
        raise DocumentException(
            code=ErrorCode.BAD_REQUEST,
            message="文件内容为空"
        )
    
    logger.debug(f"文件验证通过: {file.filename}, 大小: {len(file_data)} bytes")
    
    try:
        # 处理文档
        doc_info = document_service.upload_and_process_document(
            file_data=file_data,
            filename=file.filename,
        )
        
        logger.info(f"文档上传成功: {file.filename}")
        return APIResponse.success(
            msg="文档上传并处理成功",
            data=doc_info
        )
        
    except DocumentException:
        # 重新抛出文档异常
        raise
    except Exception as e:
        logger.error(f"文档上传异常: {file.filename if file.filename else 'unknown'}, 错误: {str(e)}")
        # 包装其他异常为文档异常
        raise DocumentException(
            code=ErrorCode.DOCUMENT_UPLOAD_FAILED,
            message=f"文档处理失败: {str(e)}"
        )

@router.get("/list", response_model=APIResponse)
def list_documents():
    """列出文档
    
    Returns:
        文档列表
    """
    try:
        logger.debug("开始获取文档列表")
        documents = document_service.list_documents()
        logger.info(f"成功获取文档列表，共 {len(documents)} 个文档")
        return APIResponse.success(
            data=documents,
            msg="获取文档列表成功"
        )
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise DocumentException(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"获取文档列表失败: {str(e)}"
        )

@router.get("/{doc_id}", response_model=APIResponse)
def get_document_info(doc_id: str):
    """获取文档信息
    
    Args:
        doc_id: 文档ID
    
    Returns:
        文档信息
    """
    if not doc_id or not doc_id.strip():
        logger.warning("获取文档信息失败: 文档ID为空")
        raise DocumentException(
            code=ErrorCode.BAD_REQUEST,
            message="文档ID不能为空"
        )
    
    try:
        logger.debug(f"开始获取文档信息: {doc_id}")
        document_info = document_service.get_document_info(doc_id)
        if not document_info:
            logger.warning(f"文档不存在: {doc_id}")
            raise DocumentException(
                code=ErrorCode.DOCUMENT_NOT_FOUND,
                message=f"文档不存在: {doc_id}"
            )
        
        logger.info(f"成功获取文档信息: {doc_id}")
        return APIResponse.success(
            data=document_info,
            msg="获取文档信息成功"
        )
    except DocumentException:
        # 重新抛出文档异常
        raise
    except Exception as e:
        logger.error(f"获取文档信息异常: {doc_id}, 错误: {str(e)}")
        raise DocumentException(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"获取文档信息失败: {str(e)}"
        )

@router.delete("/{doc_id}", response_model=APIResponse)
def delete_document(doc_id: str):
    """删除文档
    
    Args:
        doc_id: 文档ID
    
    Returns:
        删除结果
    """
    if not doc_id or not doc_id.strip():
        logger.warning("删除文档失败: 文档ID为空")
        raise DocumentException(
            code=ErrorCode.BAD_REQUEST,
            message="文档ID不能为空"
        )
    
    try:
        logger.info(f"开始删除文档: {doc_id}")
        result = document_service.delete_document(doc_id)
        if not result:
            logger.warning(f"文档不存在或删除失败: {doc_id}")
            raise DocumentException(
                code=ErrorCode.DOCUMENT_NOT_FOUND,
                message=f"文档不存在或删除失败: {doc_id}"
            )
        
        logger.info(f"成功删除文档: {doc_id}")
        return APIResponse.success(
            data={"success": result},
            msg="文档删除成功"
        )
    except DocumentException:
        # 重新抛出文档异常
        raise
    except Exception as e:
        logger.error(f"删除文档异常: {doc_id}, 错误: {str(e)}")
        raise DocumentException(
            code=ErrorCode.DOCUMENT_DELETE_FAILED,
            message=f"删除文档失败: {str(e)}"
        )