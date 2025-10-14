# Smart Doc Assistant (RAG 智能文档助手)

一个基于检索增强生成（RAG）的本地文档问答系统。支持上传文档，自动向量化并构建知识库，随后对用户提问进行检索与回答。

---

## 核心调整概览

- 后端/前端容器化，但不再在 Docker 中运行 Ollama；统一改为调用宿主机的 Ollama 服务（利用 macOS Metal/MPS 加速，显著降低延时）。
- 提供两种启动方式：本地启动与镜像启动，均直连宿主机 Ollama。
- `start-all.sh` 增加交互式菜单；自动检查宿主机是否安装 Ollama，并在缺省时拉取默认模型。

---

## 目录结构

```
smart-doc-assistant/
├── README.md
├── DOCKER.md
├── docker-compose.yml
├── docker-build.sh
├── start-all.sh
├── data/                      # 示例数据
├── backend/                   # 后端（FastAPI + LangChain）
│   ├── app/main.py            # 应用入口
│   ├── api/endpoints/         # 文档与问答接口
│   ├── services/              # RAG、LLM、文档处理服务
│   ├── storage/               # 文档与向量存储
│   ├── config/settings.py     # 环境配置读取
│   ├── requirements.txt       # 依赖
│   └── start.sh               # 后端启动辅助脚本
└── front/                     # 前端（Vite + Vue）
    ├── src/
    ├── package.json
    └── vite.config.ts
```

---

## 系统架构

- 前端（Vue）通过浏览器访问后端 API。
- 后端（FastAPI）负责文档上传/检索/问答，向量化存储采用 ChromaDB。
- LLM 推理由宿主机运行的 Ollama 提供；容器中的后端通过 `OLLAMA_BASE_URL` 直连宿主机。

```
Browser (Frontend) → Backend (FastAPI) → Ollama (Host) → LLM
                          │
                          └→ ChromaDB (Vector Store)
```

---

## 环境准备

- Python 3.11+
- Node.js + pnpm
- Docker & Docker Compose（镜像模式使用）
- 宿主机安装并运行 Ollama
  - macOS 可用 `brew install ollama`
  - 启动服务：`ollama serve`

> 说明：Docker Desktop 中运行的 Linux 容器无法使用 macOS 的 Metal/MPS 加速；将后端直连宿主机 Ollama，可显著降低延时。

---

## 配置文件（.env）

在项目根目录创建并填写 `.env`：

```env
# LLM 提供商选择
LLM_PROVIDER=ollama

# 宿主机 Ollama 连接（本地模式）
OLLAMA_BASE_URL=http://localhost:11434

# 镜像模式下，容器连接宿主机 Ollama（适用于 macOS / Windows）
# OLLAMA_BASE_URL=http://host.docker.internal:11434

# 模型名（需与宿主机已拉取的模型一致）
OLLAMA_MODEL=llama3.1:8b

# 存储配置（与代码保持一致）
VECTOR_STORE_PATH=./backend/chroma_db
DOCUMENT_STORAGE_PATH=./backend/storage/documents

# 嵌入模型与分割参数
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 启动方式（交互菜单）

运行根目录脚本：

```bash
./start-all.sh
# 或显示菜单：
./start-all.sh menu
```

菜单项：
- 1 本地启动（后端 + 前端，直连宿主机 Ollama）
- 2 镜像启动（docker-compose 后端 + 前端，容器直连宿主机 Ollama）
- 3 停止本地服务
- 4 停止镜像服务
- 5 查看镜像日志
- 6 查看镜像状态
- 0 退出

> 脚本会自动检查宿主机是否安装 Ollama，并在缺少默认模型时执行拉取。

---

## 本地启动（不使用 Docker）

- 确保 `.env` 中 `OLLAMA_BASE_URL=http://localhost:11434`。
- 执行：

```bash
./start-all.sh
# 或者仅后端：
cd backend && bash start.sh run
```

- 访问：
  - 前端开发界面：`http://localhost:5173`
  - API 文档：`http://localhost:8000/docs`

---

## 镜像启动（Docker Compose）

- 确保 `.env` 中 `OLLAMA_BASE_URL=http://host.docker.internal:11434`（macOS/Windows）。
- 执行：

```bash
./start-all.sh docker
# 或手动：
docker-compose up -d backend frontend
```

- 访问：
  - 前端：`http://localhost`
  - 后端 API：`http://localhost:8000`

> 如遇 `8000` 端口占用：`lsof -nP -iTCP:8000 -sTCP:LISTEN` 查看并结束占用进程后重试。

---

## API 概览

- `POST /api/documents/upload` 上传文档
- `GET  /api/documents` 文档列表
- `DELETE /api/documents/{document_id}` 删除文档
- `POST /api/qa/query` 基于文档问答（请求体：`{"question": "...", "top_k": 3}`）
- `GET  /api/qa/stats` 文档统计信息
- `GET  /docs` Swagger UI，`/redoc` ReDoc

---

## RAG 流程

1. 上传文档 → 解析与分块
2. 计算嵌入 → 存入向量库（ChromaDB）
3. 用户提问 → 计算问题嵌入
4. 在向量库检索相关块 → 作为上下文
5. 调用 LLM 生成回答

---

## 性能与延时建议

- 使用宿主机 Ollama（macOS Metal/MPS 加速）而非容器内 Ollama，可显著降低延时。
- 预热模型后后续请求更快；保持 `KEEP_ALIVE` 类似行为由 Ollama 控制。
- 如需进一步降时延：
  - 选择更小/量化模型（需在宿主机拉取并在 `.env` 中配置）。
  - 控制查询上下文长度与 `top_k`，减少生成负担。

---

## 常见问题

- 端口占用：`8000` 被本地进程占用时，先停止占用后再启动镜像模式。
- `host.docker.internal`：macOS/Windows 可用；Linux 环境可考虑 `--network=host` 或设置固定桥接网关。
- 文档未命中：确保已上传文档，并检查分块参数与检索 `top_k`。

---

## 开发与测试

- 后端开发：`cd backend && bash start.sh run`
- 依赖安装：`pip install -r backend/requirements.txt`
- 前端开发：`cd front && pnpm install && pnpm dev`
- 运行测试：`cd backend && pytest`

---

## 说明

- 项目定位为本地单用户服务，所有上传文档共享同一知识库。
- 请根据实际环境与模型资源选择合适的参数与模型。