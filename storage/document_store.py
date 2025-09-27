import os
import uuid
from config.settings import settings
from typing import Dict, Any, Optional

class DocumentStore:
    def __init__(self):
        # 确保文档存储目录存在
        os.makedirs(settings.document_storage_path, exist_ok=True)
        
        # 存储文档元数据的字典，按session_id组织
        self.document_metadata = {}
        # 存储session_id到文档ID的映射
        self.session_to_docs = {}
    
    def save_document(self, file_data: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> str:
        """保存文档文件
        
        Args:
            file_data: 文档文件数据
            filename: 文件名
            metadata: 文档元数据
            session_id: 用户会话ID
        
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
        self.document_metadata[doc_id] = {
            "filename": filename,
            "path": file_path,
            "doc_id": doc_id,
            "metadata": metadata
        }
        
        # 更新session_id到文档ID的映射
        if session_id:
            if session_id not in self.session_to_docs:
                self.session_to_docs[session_id] = []
            self.session_to_docs[session_id].append(doc_id)
        print(self.session_to_docs, self.document_metadata)
        return doc_id
    
    def get_document_path(self, doc_id: str) -> Optional[str]:
        """获取文档文件路径
        
        Args:
            doc_id: 文档ID
        
        Returns:
            文档文件路径，如果文档不存在则返回None
        """
        if doc_id in self.document_metadata:
            return self.document_metadata[doc_id]["path"]
        return None
    
    def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
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
            file_path = doc_metadata["path"]
            
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 从session_to_docs映射中删除
            for session_id, doc_ids in self.session_to_docs.items():
                if doc_id in doc_ids:
                    doc_ids.remove(doc_id)
                    # 如果会话没有文档了，删除会话条目
                    if not doc_ids:
                        del self.session_to_docs[session_id]
                    break
            
            # 从元数据中删除
            del self.document_metadata[doc_id]
            return True
        return False
    
    def list_documents(self, session_id: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """列出文档
        
        Args:
            session_id: 用户会话ID，如果提供则只返回该会话的文档
        
        Returns:
            文档的元数据字典
        """
        print('here', self.session_to_docs)
        if session_id:
            # 如果提供了session_id，只返回该会话的文档
            if session_id in self.session_to_docs:
                return {doc_id: self.document_metadata[doc_id] for doc_id in self.session_to_docs[session_id] if doc_id in self.document_metadata}
            return {}
        else:
            # 否则返回所有文档
            return self.document_metadata