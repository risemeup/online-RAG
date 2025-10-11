from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import settings
from typing import List, Optional

class TextProcessor:
    def __init__(self):
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len
        )
    
    def split_text(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """将文本分割成合适大小的块
        
        Args:
            text: 要分割的文本
            metadata: 文档元数据
        
        Returns:
            分割后的文档列表
        """
        documents = self.text_splitter.create_documents([text], metadatas=[metadata] if metadata else None)
        return documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表
        
        Args:
            documents: 要分割的文档列表
        
        Returns:
            分割后的文档列表
        """
        split_docs = self.text_splitter.split_documents(documents)
        return split_docs
    
    def update_chunk_settings(self, chunk_size: int = None, chunk_overlap: int = None) -> None:
        """更新文本分割的块大小和重叠设置
        
        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
        """
        # 如果没有提供新值，则使用配置文件中的值
        chunk_size = chunk_size or settings.chunk_size
        chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # 创建新的文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )