from fastapi import APIRouter, HTTPException, Query, Request
from typing import Dict, Any, Optional
from services.rag_service import RAGService
from pydantic import BaseModel

router = APIRouter(
    prefix="",
    tags=["qa"],
    responses={404: {"description": "Not found"}}
)

rag_service = RAGService()

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

@router.post("/query", response_model=Dict[str, Any])
def ask_question(request: Request, body: QuestionRequest):
    """基于文档内容提问
    
    Args:
        request: FastAPI请求对象（用于获取请求头）
        body: 包含问题和参数的请求体
    
    Returns:
        回答和相关源文档
    """
    try:
        # 从请求头中获取session_id
        session_id = request.headers.get("X-Session-ID")
        
        # 验证session_id必须存在
        if not session_id:
            raise HTTPException(status_code=400, detail="请求头中必须包含X-Session-ID")
        
        result = rag_service.query(
            question=body.question,
            top_k=body.top_k,
            session_id=session_id
        )
        return result
    except HTTPException:
        raise  # 重新抛出HTTPException以保持原始状态码和消息
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理问题时出错: {str(e)}")

@router.post("/search", response_model=Dict[str, Any])
def search_documents(request: Request, body: SearchRequest):
    """搜索相关文档
    
    Args:
        request: FastAPI请求对象（用于获取请求头）
        body: 包含搜索查询和参数的请求体
    
    Returns:
        搜索结果
    """
    try:
        # 从请求头中获取session_id
        session_id = request.headers.get("X-Session-ID")
        
        result = rag_service.search_documents(
            query=body.query,
            top_k=body.top_k,
            session_id=session_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索文档时出错: {str(e)}")

@router.get("/stats", response_model=Dict[str, int])
def get_document_stats():
    """获取文档统计信息
    
    Returns:
        文档数量统计
    """
    try:
        count = rag_service.get_document_count()
        return {"document_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息时出错: {str(e)}")