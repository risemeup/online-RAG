from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import List, Dict, Any, Optional
from services.document_service import DocumentService
import json

router = APIRouter(
    prefix="",
    tags=["documents"],
    responses={404: {"description": "Not found"}}
)

document_service = DocumentService()

@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
):
    """上传并处理文档
    
    Args:
        request: FastAPI请求对象（用于获取请求头）
        file: 要上传的文件
        metadata: 文档元数据（JSON格式字符串）
    
    Returns:
        处理结果
    """
    try:
        # 从请求头中获取session_id
        session_id = request.headers.get("X-Session-ID")
        
        # 读取文件内容
        file_data = await file.read()
        
        # 处理文档
        result = document_service.upload_and_process_document(
            file_data=file_data,
            filename=file.filename,
            session_id=session_id
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理文档时出错: {str(e)}")

@router.get("/list", response_model=Dict[str, Dict[str, Any]])
def list_documents(request: Request):
    """列出文档
    
    Returns:
        文档列表
    """
    # 从请求头中获取session_id
    session_id = request.headers.get("X-Session-ID")
    return document_service.list_documents(session_id)

@router.get("/{doc_id}", response_model=Optional[Dict[str, Any]])
def get_document_info(doc_id: str):
    """获取文档信息
    
    Args:
        doc_id: 文档ID
    
    Returns:
        文档信息
    """
    document_info = document_service.get_document_info(doc_id)
    if not document_info:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document_info

@router.delete("/{doc_id}", response_model=Dict[str, bool])
def delete_document(doc_id: str):
    """删除文档
    
    Args:
        doc_id: 文档ID
    
    Returns:
        删除结果
    """
    result = document_service.delete_document(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"success": result}