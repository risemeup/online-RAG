import sys
sys.path.append('/app')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from config.settings import settings
from utils.exception_handler import register_exception_handlers
from utils.logger import get_logger

# 初始化FastAPI应用
app = FastAPI(
    title="RAG智能文档助手",
    description="基于检索增强生成的智能文档问答系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
register_exception_handlers(app)

# 注册API路由器
app.include_router(api_router, prefix="/api")

# 初始化日志器
logger = get_logger(name="app")

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "欢迎使用RAG智能文档助手API",
        "version": app.version,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "RAG智能文档助手",
        "version": app.version
    }

@app.on_event("startup")
async def startup_event():
    """应用启动时执行的操作"""
    # 这里可以添加一些初始化代码，例如加载模型、连接数据库等
    logger.info("RAG智能文档助手API已启动")
    logger.info(f"服务运行在: http://0.0.0.0:8000")
    logger.info(f"API文档地址: http://0.0.0.0:8000/docs")
    logger.info(f"当前环境配置: LLM提供商={settings.llm_provider}, 模型={settings.llm_model}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行的操作"""
    # 这里可以添加一些清理代码
    logger.info("RAG智能文档助手API已关闭")