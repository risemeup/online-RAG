from config.settings import settings
from langchain_openai import ChatOpenAI
from typing import Dict, Any, Optional

class LLMService:
    def __init__(self):
        # 初始化大语言模型
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            temperature=0  # 设置为0以获得更确定性的回答
        )
    
    def generate(self, prompt: str) -> str:
        """生成文本响应
        
        Args:
            prompt: 提示文本
        
        Returns:
            生成的文本响应
        """
        response = self.llm.predict(prompt)
        return response
    
    def generate_with_messages(self, messages: list) -> str:
        """使用消息列表生成响应
        
        Args:
            messages: 消息列表，格式为[{"role": "user", "content": "..."}, ...]
        
        Returns:
            生成的文本响应
        """
        response = self.llm.predict_messages(messages)
        return response.content
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新LLM配置
        
        Args:
            config: 包含更新配置的字典
        """
        # 根据提供的配置更新LLM实例
        for key, value in config.items():
            if hasattr(self.llm, key):
                setattr(self.llm, key, value)