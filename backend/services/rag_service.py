from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers import ContextualCompressionRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from storage.vector_store import VectorStore
from services.llm_service import LLMService
from typing import Dict, Any, Optional

class RAGService:
    def __init__(self):
        # 初始化依赖服务
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
        self.llm = self.llm_service.llm
        
        # 创建默认的RAG检索器
        self.retriever = self.vector_store.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        # 定义RAG提示模板
        self.rag_prompt_template = """
        你是一个智能助手，你需要基于提供的上下文信息来回答用户的问题。
        如果上下文信息中没有相关内容，请直接说明你没有足够的信息来回答这个问题，不要编造信息。
        请用简洁明了的方式回答问题。
        
        上下文信息:
        {context}
        
        用户问题:
        {question}
        
        回答:
        """
        self.prompt = PromptTemplate(
            template=self.rag_prompt_template,
            input_variables=["context", "question"]
        )
        
        # 创建RAG链
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
    
    def query(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """基于检索增强生成回答
        
        Args:
            question: 用户问题
            top_k: 检索的文档数量
        
        Returns:
            包含回答和源文档的字典
        """
        # 检索相关文档
        documents = self.vector_store.search(question, top_k=top_k)
        
        # 如果没有找到相关文档，直接返回没有足够信息的回答
        if not documents:
            return {
                "answer": "我没有足够的信息来回答这个问题。",
                "sources": [],
                "question": question
            }
        
        # 构建上下文
        context = "\n\n".join([doc.page_content for doc in documents])
        
        # 构建提示
        prompt = self.prompt.format(context=context, question=question)
        
        # 使用LLM生成回答
        answer = self.llm.invoke(prompt)
        
        # 确保answer是字符串格式
        if hasattr(answer, 'content'):
            answer = answer.content
        
        # 处理源文档信息
        sources = []
        for doc in documents:
            source_info = {
                "content": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question
        }
    
    def search_documents(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """搜索相关文档
        
        Args:
            query: 搜索查询
            top_k: 返回的文档数量
        
        Returns:
            包含搜索结果的字典
        """
        # 执行文档搜索
        documents = self.vector_store.search(query, top_k=top_k)
        
        # 处理搜索结果
        search_results = []
        for doc in documents:
            result_info = {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            search_results.append(result_info)
        
        return {
            "results": search_results,
            "total": len(search_results),
            "query": query
        }
    
    def set_compression_retriever(self, use_compression: bool = True) -> None:
        """设置是否使用压缩检索器
        
        Args:
            use_compression: 是否使用压缩检索器
        """
        if use_compression:
            # 创建压缩器
            compressor = LLMChainExtractor.from_llm(self.llm)
            # 创建压缩检索器
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=self.vector_store.vectorstore.as_retriever()
            )
        else:
            # 使用普通检索器
            self.retriever = self.vector_store.vectorstore.as_retriever()
        
        # 重新创建RAG链
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
    
    def update_rag_prompt(self, prompt_template: str) -> None:
        """更新RAG提示模板
        
        Args:
            prompt_template: 新的提示模板
        """
        self.rag_prompt_template = prompt_template
        self.prompt = PromptTemplate(
            template=self.rag_prompt_template,
            input_variables=["context", "question"]
        )
        
        # 重新创建RAG链
        self.rag_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )
    
    def get_document_count(self) -> int:
        """获取向量存储中的文档数量
        
        Returns:
            文档数量
        """
        return self.vector_store.get_document_count()