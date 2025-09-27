import os
from typing import List, Tuple, Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config.settings import settings

class VectorStore:
    def __init__(self):
        # 初始化嵌入模型（开源免费）
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model_name)
        
        # 确保向量存储目录存在
        os.makedirs(settings.vector_store_path, exist_ok=True)
        
        # 初始化向量存储
        self.vectorstore = Chroma(
            persist_directory=settings.vector_store_path,
            embedding_function=self.embeddings
        )
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """添加文档到向量存储
        
        Args:
            documents: 要添加的文档列表
        
        Returns:
            添加的文档ID列表
        """
        ids = self.vectorstore.add_documents(documents)
        # 持久化存储
        self.vectorstore.persist()
        return ids
    
    def search(self, query: str, top_k: int = 3, session_id: Optional[str] = None) -> List[Document]:
        """基于查询检索相关文档
        
        Args:
            query: 检索查询
            top_k: 返回的最大文档数量
            session_id: 用户会话ID，如果提供则只返回该会话的文档
        
        Returns:
            检索到的文档列表
        """
        # 使用ChromaDB原生的元数据过滤功能，不再进行全数据库扫描
        filter_params = {"session_id": session_id} if session_id else None
        
        # 直接使用ChromaDB的similarity_search方法，传入过滤参数
        results = self.vectorstore.similarity_search(query, k=top_k, filter=filter_params)
        return results
    
    def search_with_score(self, query: str, top_k: int = 3, session_id: Optional[str] = None) -> List[Tuple[Document, float]]:
        """基于查询检索相关文档并返回相似度分数
        
        Args:
            query: 检索查询
            top_k: 返回的最大文档数量
            session_id: 用户会话ID，如果提供则只返回该会话的文档
        
        Returns:
            检索到的文档和相似度分数的列表
        """
        # 使用ChromaDB原生的元数据过滤功能，不再进行全数据库扫描
        filter_params = {"session_id": session_id} if session_id else None
        
        # 直接使用ChromaDB的similarity_search_with_score方法，传入过滤参数
        results = self.vectorstore.similarity_search_with_score(query, k=top_k, filter=filter_params)
        return results
    
    def delete_documents_by_metadata(self, metadata_filter: dict) -> None:
        """根据元数据过滤条件删除文档
        
        Args:
            metadata_filter: 元数据过滤条件，如 {"doc_id": "xxx"} 或 {"session_id": "xxx"}
        """
        try:
            # 首先通过过滤条件获取匹配的文档
            # 使用metadatas而不是ids，因为最新版本的ChromaDB API不支持include=['ids']
            matching_docs = self.vectorstore.get(include=['metadatas'], where=metadata_filter)
            
            # 检查是否有匹配的文档
            if matching_docs and len(matching_docs.get('ids', [])) > 0:
                # 如果有匹配的文档，删除它们
                self.vectorstore.delete(matching_docs['ids'])
                # 持久化存储
                self.vectorstore.persist()
        except Exception as e:
            print(f"删除向量存储中的文档时出错: {str(e)}")
            # 尝试使用另一种方式删除文档（如果上述方法失败）
            try:
                # 直接获取所有文档ID并删除（这是一个备选方案）
                all_docs = self.vectorstore.get()
                if all_docs and 'ids' in all_docs:
                    self.vectorstore.delete(all_docs['ids'])
                    self.vectorstore.persist()
            except Exception as inner_e:
                print(f"备选删除方法也失败: {str(inner_e)}")
                # 如果两种方法都失败，继续抛出异常以便上层处理
                raise
    
    def get_document_count(self) -> int:
        """获取向量存储中的文档数量
        
        Returns:
            文档数量
        """
        # 获取所有文档的ID并计算数量
        return len(self.vectorstore.get()['ids'])