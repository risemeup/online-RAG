# API模块初始化文件
from fastapi import APIRouter

# 创建主API路由器
router = APIRouter()

# 导入并注册所有端点
from .endpoints import document, qa

router.include_router(document.router, prefix="/documents", tags=["documents"])
router.include_router(qa.router, prefix="/qa", tags=["qa"])