from storage.document_store import DocumentStore, DocumentMetadata
from storage.vector_store import VectorStore
from utils.text_processor import TextProcessor
from utils.logger import get_logger
from typing import List, Dict, Any, Optional

# 初始化日志器
logger = get_logger(name="document_service")

class DocumentService:
    def __init__(self):
        # 初始化依赖服务
        self.document_store = DocumentStore()
        self.vector_store = VectorStore()
        self.text_processor = TextProcessor()
    
    def process_document(self, doc_metadata: DocumentMetadata) -> Dict[str, Any]:
        """处理文档文件
        
        Args:
            doc_metadata: 文档元数据
        
        Returns:
            包含处理结果的字典
        """
        # 加载文档
        file_path = doc_metadata.path
        if file_path.lower().endswith('.docx'):
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
        elif file_path.lower().endswith('.txt'):
            # 对于txt文件，使用简单的文本读取方式
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            from langchain_core.documents import Document
            documents = [Document(page_content=content, metadata={'source': file_path})]
        else:
            # 对于其他类型的文件，使用默认的UnstructuredFileLoader
            from langchain_community.document_loaders import UnstructuredFileLoader
            loader = UnstructuredFileLoader(file_path)
            documents = loader.load()
        
        # 分割文档
        split_docs = self.text_processor.split_documents(documents)
        
        # 添加元数据
        for i, doc in enumerate(split_docs):
            doc.metadata["filename"] = doc_metadata.filename
            doc.metadata["doc_id"] = doc_metadata.doc_id
            # 添加chunk_id
            doc.metadata["chunk_id"] = f"chunk_{i:03d}"
            # 添加content字段，存储原始文本
            doc.metadata["content"] = doc.page_content
        
        # 将文档添加到向量存储
        self.vector_store.add_documents(split_docs)
    
    def upload_and_process_document(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """上传并处理文档
        
        Args:
            file_data: 文档文件数据
            filename: 文件名
        
        Returns:
            包含处理结果的字典
        """
        # 保存文档到文档存储
        doc_metadata = self.document_store.save_document(file_data, filename)
          
        # 处理文档
        self.process_document(doc_metadata)
        
        # 返回文档信息
        return {
            "id": doc_metadata.doc_id,
            "filename": doc_metadata.filename,
            "path": doc_metadata.path,
            "upload_time": doc_metadata.upload_time,
            "status": "processed"
        }
    
    
    def get_document_info(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取文档信息
        
        Args:
            doc_id: 文档ID
        
        Returns:
            文档信息，如果文档不存在则返回None
        """
        doc_metadata = self.document_store.get_document_metadata(doc_id)
        if doc_metadata is None:
            return None
        
        # 将DocumentMetadata对象转换为字典以便JSON序列化
        return {
            "id": doc_metadata.doc_id,
            "filename": doc_metadata.filename,
            "path": doc_metadata.path,
            "upload_time": doc_metadata.upload_time
        }
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """列出文档
        
        Returns:
            文档的信息列表
        """
        doc_list = []
        for item in self.document_store.list_documents().values():
            doc_list.append({
                "id": item.doc_id,
                "filename": item.filename,
            })
        return doc_list
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            如果删除成功则返回True，否则返回False
        """
        # 获取文档信息以获取关联的文档块
        doc_info = self.document_store.get_document_metadata(doc_id)
        if not doc_info:
            return False
        
        # 从向量存储中删除关联的文档块
        # 使用新的delete_documents_by_metadata方法，基于doc_id元数据进行过滤删除
        # 这样可以避免全库扫描，显著提高删除效率
        self.vector_store.delete_documents_by_metadata({"doc_id": doc_id})
        
        # 从文档存储中删除文档
        return self.document_store.delete_document(doc_id)