from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 创建 LLM
llm = ChatOpenAI(
    model="glm-4.5-Flash",
    openai_api_key="cf8514726b17420589f1ee25113ad29d.SDHI8aT853EXYgHm",
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{domain}专家"),
    ("human", "请解释一下{topic}的概念和应用")
])

# 创建链
chain = prompt | llm

# 调用链
response = chain.invoke({
    "domain": "机器学习",
    "topic": "深度学习"
})

print(response.content)