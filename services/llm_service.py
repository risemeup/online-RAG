from config.settings import settings
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

class LLMService:
    def __init__(self):
        # 根据配置选择LLM提供商
        if settings.llm_provider.lower() == "ollama":
            # 初始化Ollama模型
            self.llm = ChatOllama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
                temperature=0  # 设置为0以获得更确定性的回答
            )
        else:
            # 默认使用OpenAI兼容的模型
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                base_url=settings.llm_base_url,
                api_key=settings.llm_api_key,
                temperature=0  # 设置为0以获得更确定性的回答
            )