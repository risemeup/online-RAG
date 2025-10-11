import os
import warnings
from typing import List, Tuple, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from config.settings import settings

# 禁用 ChromaDB 遥测以避免错误
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_IMPL"] = "none"

# 抑制 HuggingFace 的弃用警告
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

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
        # 注意：Chroma 0.4.x+ 版本会自动持久化，无需手动调用persist()
        return ids
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """基于查询检索相关文档
        
        Args:
            query: 检索查询
            top_k: 返回的最大文档数量
        
        Returns:
            检索到的文档列表
        """
        # 使用ChromaDB的similarity_search方法
        results = self.vectorstore.similarity_search(query, k=top_k)
        return results
    
    def search_with_score(self, query: str, top_k: int = 3) -> List[Tuple[Document, float]]:
        """基于查询检索相关文档并返回相似度分数
        
        Args:
            query: 检索查询
            top_k: 返回的最大文档数量
        
        Returns:
            检索到的文档和相似度分数的列表
        """
        # 使用ChromaDB的similarity_search_with_score方法
        results = self.vectorstore.similarity_search_with_score(query, k=top_k)
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
                print(f"成功删除 {len(matching_docs['ids'])} 个向量文档")
            else:
                print("没有找到匹配的向量文档")
        except Exception as e:
            print(f"删除向量存储中的文档时出错: {str(e)}")
            # 尝试使用另一种方式删除文档（如果上述方法失败）
            try:
                # 使用 where 条件删除文档
                self.vectorstore.delete(where=metadata_filter)
                print(f"使用备选方法成功删除文档")
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