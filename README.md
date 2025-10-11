# RAG智能文档网页服务
# RAG智能文档助手

## 项目概述

这是一个基于大语言模型和检索增强生成（RAG）技术的智能文档问答系统。用户可以上传文档，系统会自动处理并构建知识库，然后基于这些文档内容回答用户的提问。系统设计为本地单用户服务，提供简洁高效的文档问答体验。

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
4. 将文本块和向量存储到向量数据库中
5. 用户提问时，系统计算问题的嵌入向量
6. 在向量数据库中检索最相似的文本块
7. 将检索到的文本块作为上下文，发送给LLM生成回答

**系统特点**：作为本地单用户服务，系统会检索所有已上传的文档内容来回答问题，无需会话隔离。

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
  - **返回**: 回答和相关源文档

- `POST /api/qa/search` - 搜索相关文档
  - **请求体**: `{"query": "搜索内容", "top_k": 3}`
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

项目使用 `.env` 文件管理环境变量，支持两种LLM提供商：**OpenAI兼容API** 和 **本地Ollama**。

### 配置文件示例

复制 `.env.example` 文件为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### LLM提供商配置

#### 1. 使用OpenAI兼容API（默认）

```env
# LLM提供商选择
LLM_PROVIDER=openai

# OpenAI兼容API配置
DEEPSEEK_API_KEY=your_api_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=deepseek/deepseek-chat-v3.1:free
```

#### 2. 使用本地Ollama

```env
# LLM提供商选择
LLM_PROVIDER=ollama

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Ollama安装和使用

如果选择使用Ollama，需要先安装并启动Ollama服务：

1. **安装Ollama**：
   ```bash
   # macOS
   brew install ollama
   
   # 或从官网下载：https://ollama.ai
   ```

2. **启动Ollama服务**：
   ```bash
   ollama serve
   ```

3. **下载模型**：
   ```bash
   # 下载llama3.2模型（推荐）
   ollama pull llama3.2
   
   # 或下载其他模型，如：
   ollama pull qwen2.5
   ollama pull mistral
   ```

4. **配置环境变量**：
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2  # 使用已下载的模型名称
   ```

### 其他配置选项

```env
# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# 存储配置
VECTOR_STORE_PATH=./chroma_db
DOCUMENT_STORAGE_PATH=./storage/documents

# 嵌入模型配置
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# 文本分割配置
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

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
- 系统设计为本地单用户服务，所有文档共享同一个知识库
- 环境变量`TOKENIZERS_PARALLELISM`已设置为`false`以消除常见警告
- 项目会自动创建和管理虚拟环境，避免系统包冲突

## 常见问题解决

### 1. externally-managed-environment 错误

如果遇到 `externally-managed-environment` 错误，这是Python 3.11+的安全特性。解决方案：

**推荐方案**：使用项目提供的启动脚本
```bash
bash start.sh install  # 自动创建虚拟环境并安装依赖
```

**手动方案**：
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖（使用国内镜像源）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 网络超时问题

如果安装依赖时遇到网络超时，可以尝试：
- 使用清华大学镜像源：`-i https://pypi.tuna.tsinghua.edu.cn/simple/`
- 使用阿里云镜像源：`-i https://mirrors.aliyun.com/pypi/simple/`
- 增加超时时间：`--timeout 300`
