# RAG智能文档网页服务
# RAG智能文档助手

## 项目概述

这是一个基于大语言模型和检索增强生成（RAG）技术的智能文档问答系统。用户可以上传文档，系统会自动处理并构建知识库，然后基于这些文档内容回答用户的提问。系统采用前后端分离架构，本README主要描述后端实现。

## 系统架构

### 整体架构

```
+----------------+      +----------------+      +----------------+
|                |      |                |      |                |
|  前端界面      +----->+  FastAPI后端   +----->+  LLM & RAG     |
|                |      |                |      |  服务          |
+----------------+      +----------------+      +----------------+
        ^                         |                       |
        |                         v                       v
        |                   +----------------+      +----------------+
        |                   |                |      |                |
        +-------------------+  API接口      |      |  向量数据库    |
                            |                |      |                |
                            +----------------+      +----------------+
```

### 后端架构

后端采用模块化设计，主要包含以下几个核心模块：

1. **API层**：使用FastAPI框架提供RESTful API接口，处理用户请求
2. **服务层**：包含RAG服务、文档处理服务、LLM服务等核心业务逻辑
3. **数据层**：负责文档存储、向量存储和数据持久化
4. **工具层**：提供各种辅助工具，如文本分割、嵌入计算等

## 工程结构

```
smart-doc-assistant/
├── api/                     # API接口层
│   ├── __init__.py
│   ├── endpoints/           # 路由端点
│   │   ├── __init__.py
│   │   ├── document.py      # 文档相关API
│   │   └── qa.py            # 问答相关API
│   └── models/              # 请求响应模型
│       ├── __init__.py
│       ├── document.py
│       └── qa.py
├── app/                     # 应用入口
│   ├── __init__.py
│   └── main.py
├── config/                  # 配置文件
│   ├── __init__.py
│   └── settings.py
├── core/                    # 核心功能模块
│   └── __init__.py
├── services/                # 业务服务层
│   ├── __init__.py
│   ├── document_service.py  # 文档处理服务
│   ├── llm_service.py       # LLM服务
│   └── rag_service.py       # RAG检索问答服务
├── storage/                 # 存储层
│   ├── __init__.py
│   ├── document_store.py    # 文档存储
│   ├── vector_store.py      # 向量存储
│   └── documents/           # 文档文件存储目录
├── utils/                   # 工具函数
│   ├── __init__.py
│   └── text_processor.py    # 文本处理工具
├── tests/                   # 测试代码
│   ├── __init__.py
│   ├── test_document.py
│   └── test_rag_service.py
├── .env                     # 环境变量配置
├── requirements.txt         # 项目依赖
├── start.sh                 # 启动脚本
├── chroma_db/               # 向量数据库存储目录
├── data/                    # 示例数据
└── README.md                # 项目文档
```

## 技术栈

### 后端技术
- **框架**：FastAPI 0.110.0
- **异步支持**：Python asyncio
- **RAG实现**：LangChain 0.1.13
- **向量数据库**：ChromaDB 0.4.24
- **嵌入模型**：sentence-transformers 2.5.1
- **LLM接口**：支持OpenAI API兼容接口（langchain-openai 0.0.7）

### 文档处理
- **文档解析**：Unstructured 0.10.30
- **文本分割**：LangChain Text Splitters
- **嵌入计算**：sentence-transformers 2.5.1
- **文档格式支持**：PDF、Word、文本等

### 其他组件
- **API文档**：Swagger UI (/docs) 和 ReDoc (/redoc)
- **环境配置**：pydantic-settings 2.2.1 和 python-dotenv 1.0.1
- **HTTP客户端**：requests 2.31.0
- **进度显示**：tqdm 4.66.2

## 核心功能实现

### 1. RAG检索问答

RAG (Retrieval-Augmented Generation) 是本系统的核心功能，实现流程如下：

1. 用户上传文档
2. 系统解析文档并分割成合适大小的文本块
3. 为每个文本块计算嵌入向量
4. 将文本块和向量存储到向量数据库中，附带元数据（包括session_id）
5. 用户提问时，系统计算问题的嵌入向量
6. 在向量数据库中检索最相似的文本块（按session_id过滤）
7. 将检索到的文本块作为上下文，发送给LLM生成回答

**重要说明**：当前版本中，所有RAG查询都需要提供`X-Session-ID`请求头，系统会根据该ID过滤相关文档。

### 2. 文档处理

文档处理服务负责接收用户上传的文档，进行解析、分割和向量化：

- 支持多种文档格式（PDF、Word、文本等）
- 智能文本分割，保持语义完整性
- 批量处理和进度跟踪
- 文档元数据管理

### 3. LLM服务

LLM服务封装了与大语言模型的交互逻辑：

- 支持多种LLM提供商（OpenAI、DeepSeek等）
- 统一的接口设计，便于切换模型
- 模型参数配置管理
- 会话管理和上下文维护

## API接口设计

### 文档管理接口

- `POST /api/documents/` - 上传新文档
- `GET /api/documents/` - 获取所有文档列表
- `GET /api/documents/{document_id}` - 获取文档详情
- `DELETE /api/documents/{document_id}` - 删除文档

### 问答接口

- `POST /api/qa/query` - 基于文档内容提问
  - **请求体**: `{"question": "问题内容", "top_k": 3}`
  - **请求头**: 必须包含 `X-Session-ID`
  - **返回**: 回答和相关源文档

- `POST /api/qa/search` - 搜索相关文档
  - **请求体**: `{"query": "搜索内容", "top_k": 3}`
  - **请求头**: 可选包含 `X-Session-ID` 进行过滤
  - **返回**: 搜索结果列表

- `GET /api/qa/stats` - 获取文档统计信息
  - **返回**: 包含文档数量的统计信息

### 根路径

- `GET /` - 返回API基本信息

### API文档

- `GET /docs` - Swagger UI文档
- `GET /redoc` - ReDoc文档
- `GET /openapi.json` - OpenAPI规范

## 环境变量配置

项目使用 `.env` 文件管理环境变量，主要配置LLM服务的API密钥：

```env
# LLM API密钥配置
DEEPSEEK_API_KEY=your_api_key_here

# 可选配置（如未指定，使用默认值）
# SERVER_HOST=0.0.0.0
# SERVER_PORT=8000
# VECTOR_STORE_PATH=./chroma_db
# DOCUMENT_STORAGE_PATH=./storage/documents
```

当前项目使用DeepSeek API作为LLM服务提供商，您需要在.env文件中配置有效的API密钥。

## 快速开始

### 使用启动脚本

项目提供了`start.sh`脚本以简化依赖安装、服务器启动和测试运行等操作：

```bash
# 安装依赖
bash start.sh install

# 启动开发服务器（会自动清空向量数据库和本地文本缓存）
bash start.sh run

# 运行测试
bash start.sh test

# 安装依赖并启动服务器
bash start.sh all

# 显示帮助信息
bash start.sh help
```

### 手动启动

1. 克隆项目代码
2. 安装依赖：`pip install -r requirements.txt`
3. 配置环境变量：在`.env`文件中设置`DEEPSEEK_API_KEY`
4. 启动服务：`uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### 访问API文档

服务启动后，可以通过以下URL访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 注意事项

- 启动开发服务器时，系统会自动清空向量数据库和本地文本缓存
- 所有RAG查询请求必须包含`X-Session-ID`请求头
- 环境变量`TOKENIZERS_PARALLELISM`已设置为`false`以消除常见警告

## 扩展建议

1. **支持更多文档格式**：添加对PPT、Excel、图片OCR等格式的支持
2. **多语言支持**：增强对中文等非英语文档的处理能力
3. **用户管理系统**：添加用户认证、授权和个性化设置
4. **文档分类和标签**：实现文档分类和标签系统，提高检索精度
5. **批量处理优化**：优化大量文档的批量处理性能
6. **模型微调**：基于特定领域文档对模型进行微调

## 总结

本项目提供了一个完整的RAG智能文档问答系统的后端实现方案。采用FastAPI和LangChain构建，具有良好的可扩展性和可维护性。系统支持文档上传、处理和基于内容的智能问答，适用于需要处理大量文档并提供智能查询服务的场景。

当前版本的主要特点：
- 基于LangChain和ChromaDB实现高效的检索增强生成
- 使用DeepSeek API作为大语言模型服务
- 提供完整的RESTful API接口，包含文档管理和问答功能
- 支持session_id机制，可隔离不同会话的文档和查询
- 自动处理多种文档格式，包括PDF、Word和文本文件
- 提供便捷的启动脚本，简化开发和部署流程
- 内置详细的API文档（Swagger UI和ReDoc）

项目易于扩展，可以根据需求添加更多功能，如支持更多文档格式、多语言支持、用户管理系统等。