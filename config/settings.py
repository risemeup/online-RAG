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
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # 支持 "openai" 或 "ollama"
    llm_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek/deepseek-chat-v3.1:free")
    
    # Ollama配置
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    
    # 文档存储配置
    document_storage_path: str = os.getenv("DOCUMENT_STORAGE_PATH", "./storage/documents")
    
    # 嵌入模型配置
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # 文本分割配置
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    
# 创建设置实例
settings = Settings()