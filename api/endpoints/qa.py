from fastapi import APIRouter
from typing import Optional
from services.rag_service import RAGService
from pydantic import BaseModel
from utils.response import APIResponse, ErrorCode, RAGException
from utils.logger import get_logger

# 初始化日志器
logger = get_logger(name="qa")

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

@router.post("/query", response_model=APIResponse)
def ask_question(body: QuestionRequest):
    """基于文档内容提问
    
    Args:
        body: 包含问题和参数的请求体
    
    Returns:
        回答和相关源文档
    """
    if not body.question or not body.question.strip():
        logger.warning("问答请求失败: 问题内容为空")
        raise RAGException(
            code=ErrorCode.BAD_REQUEST,
            message="问题内容不能为空"
        )
    
    try:
        logger.info(f"收到问答请求: {body.question[:50]}{'...' if len(body.question) > 50 else ''}")
        logger.debug(f"问答参数: top_k={body.top_k}")
        
        result = rag_service.query(
            question=body.question,
            top_k=body.top_k
        )
        
        logger.info(f"问答请求处理完成，返回 {len(result.get('sources', []))} 个相关文档")
        return APIResponse.success(
            data=result,
            msg="问答请求处理完成"
        )
    except RAGException:
        # 重新抛出RAG异常
        raise
    except Exception as e:
        logger.error(f"处理问答请求失败: {body.question[:50]}{'...' if len(body.question) > 50 else ''}, 错误: {str(e)}")
        raise RAGException(
            code=ErrorCode.RAG_QUERY_FAILED,
            message=f"处理问题时出错: {str(e)}"
        )

@router.post("/search", response_model=APIResponse)
def search_documents(body: SearchRequest):
    """搜索相关文档
    
    Args:
        body: 包含查询和参数的请求体
    
    Returns:
        相关文档列表
    """
    if not body.query or not body.query.strip():
        logger.warning("文档搜索请求失败: 查询内容为空")
        raise RAGException(
            code=ErrorCode.BAD_REQUEST,
            message="查询内容不能为空"
        )
    
    try:
        logger.info(f"收到文档搜索请求: {body.query[:50]}{'...' if len(body.query) > 50 else ''}")
        logger.debug(f"搜索参数: top_k={body.top_k}")
        
        result = rag_service.search_documents(
            query=body.query,
            top_k=body.top_k
        )
        
        logger.info(f"文档搜索完成，返回 {result['total']} 个相关文档")
        return APIResponse.success(
            data=result,
            msg="文档搜索完成"
        )
    except RAGException:
        # 重新抛出RAG异常
        raise
    except Exception as e:
        logger.error(f"文档搜索失败: {body.query[:50]}{'...' if len(body.query) > 50 else ''}, 错误: {str(e)}")
        raise RAGException(
            code=ErrorCode.RAG_SEARCH_FAILED,
            message=f"搜索文档时出错: {str(e)}"
        )

@router.get("/stats", response_model=APIResponse)
def get_stats():
    """获取RAG系统统计信息
    
    Returns:
        统计信息
    """
    try:
        logger.info("收到统计信息请求")
        
        document_count = rag_service.get_document_count()
        stats = {
            "document_count": document_count
        }
        
        logger.info("统计信息获取完成")
        return APIResponse.success(
            data=stats,
            msg="统计信息获取完成"
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise RAGException(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message=f"获取统计信息时出错: {str(e)}"
        )