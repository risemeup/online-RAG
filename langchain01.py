from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv 
load_dotenv(override=True)

DeepSeek_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 初始化模型
model = ChatOpenAI(
    model="deepseek/deepseek-chat-v3.1:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=DeepSeek_API_KEY,
)

question = "你好，请你介绍一下你自己。"

result = model.invoke(question)
print(result.content)

