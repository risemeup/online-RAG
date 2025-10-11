import os
import uuid
import time
from config.settings import settings
from typing import Dict, Any, Optional

class DocumentMetadata:
    def __init__(self, filename: str, path: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None):
        self.filename = filename
        self.path = path
        self.doc_id = doc_id
        self.upload_time = time.time()  # 添加上传时间戳

class DocumentStore:
    def __init__(self):
        # 确保文档存储目录存在
        os.makedirs(settings.document_storage_path, exist_ok=True)
        
        # 存储文档元数据的字典
        self.document_metadata = {}
    
    def save_document(self, file_data: bytes, filename: str) -> str:
        """保存文档文件
        
        Args:
            file_data: 文档文件数据
            filename: 文件名
        
        Returns:
            文档ID
        """
        # 生成文档ID
        doc_id = str(uuid.uuid4())
        
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        
        # 构建文件路径
        file_path = os.path.join(settings.document_storage_path, f"{doc_id}{ext}")
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        # 存储文档元数据
        self.document_metadata[doc_id] = DocumentMetadata(
            filename=filename,
            path=file_path,
            doc_id=doc_id,
        )
        
        return self.document_metadata[doc_id]
    
    def get_document_path(self, doc_id: str) -> Optional[str]:
        """获取文档文件路径
        
        Args:
            doc_id: 文档ID
        
        Returns:
            文档文件路径，如果文档不存在则返回None
        """
        if doc_id in self.document_metadata:
            return self.document_metadata[doc_id].path
        return None
    
    def get_document_metadata(self, doc_id: str) -> Optional[DocumentMetadata]:
        """获取文档元数据
        
        Args:
            doc_id: 文档ID
        
        Returns:
            文档元数据，如果文档不存在则返回None
        """
        if doc_id in self.document_metadata:
            return self.document_metadata[doc_id]
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档
        
        Args:
            doc_id: 文档ID
        
        Returns:
            如果删除成功则返回True，否则返回False
        """
        if doc_id in self.document_metadata:
            # 获取文档的元数据
            doc_metadata = self.document_metadata[doc_id]
            
            # 获取文件路径
            file_path = doc_metadata.path
            
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 从元数据中删除
            del self.document_metadata[doc_id]
            return True
        return False
    
    def list_documents(self) -> Dict[str, DocumentMetadata]:
        """列出所有文档
        
        Returns:
            文档的元数据字典
        """
        return self.document_metadata