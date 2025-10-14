import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    # 服务器配置
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 向量数据库配置
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./chroma_db")
    
    # LLM配置
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")  # 支持 "openai" 或 "ollama"
    llm_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    @property
    def llm_base_url(self) -> str:
        """根据LLM提供商返回相应的base_url"""
        if self.llm_provider.lower() == "openai":
            return os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        else:
            return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    @property
    def llm_model(self) -> str:
        """根据LLM提供商返回相应的模型名称"""
        if self.llm_provider.lower() == "openai":
            return os.getenv("LLM_MODEL", "deepseek/deepseek-chat-v3.1:free")
        else:
            return os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    
    # 文档存储配置
    document_storage_path: str = os.getenv("DOCUMENT_STORAGE_PATH", "./storage/documents")
    
    # 嵌入模型配置
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # 文本分割配置
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
# 创建设置实例
settings = Settings()