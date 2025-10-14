# Docker 部署指南

本文档介绍如何使用 Docker 部署 Smart Doc Assistant 项目。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

## 🚀 快速开始

### 1. 一键部署

```bash
# 使用构建脚本一键部署
./docker-build.sh deploy

# 或者使用交互模式
./docker-build.sh
```

### 2. 手动部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看状态
docker-compose ps
```

## 🏗️ 项目结构

```
smart-doc-assistant/
├── backend/
│   ├── Dockerfile              # 后端镜像构建文件
│   └── .dockerignore          # 后端忽略文件
├── front/
│   ├── Dockerfile              # 前端镜像构建文件
│   ├── nginx.conf             # Nginx 配置
│   └── .dockerignore          # 前端忽略文件
├── docker-compose.yml          # 服务编排文件
├── docker-build.sh            # 构建部署脚本
├── .dockerignore              # 项目忽略文件
└── DOCKER.md                  # 本文档
```

## 🐳 服务架构

### 服务组件

| 服务名 | 端口 | 描述 |
|--------|------|------|
| frontend | 80 | 前端 Web 界面 (Nginx + Vue3) |
| backend | 8000 | 后端 API 服务 (FastAPI) |
| redis | 6379 | 缓存服务 (可选) |

### 网络配置

- 所有服务运行在 `smart-doc-network` 网络中
- 前端通过 `/api/` 路径代理到后端服务
- 支持健康检查和自动重启

## 📁 数据持久化

### 数据卷

- `chroma_data`: 向量数据库数据
- `redis_data`: Redis 缓存数据

### 挂载目录

- `./storage`: 文档存储目录
- `./logs`: 日志文件目录
- `./data`: 数据文件目录

## ⚙️ 环境配置

### 必需的环境变量

在项目根目录创建 `.env` 文件：

```bash
# LLM 配置
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1

# 向量数据库配置
VECTOR_DB_PATH=./chroma_db

# 其他配置
LOG_LEVEL=INFO
```

### 可选配置

```bash
# Redis 配置
REDIS_URL=redis://redis:6379

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# 安全配置
SECRET_KEY=your_secret_key_here
```

## 🔧 常用命令

### 构建脚本命令

```bash
# 构建镜像
./docker-build.sh build

# 启动服务
./docker-build.sh start

# 停止服务
./docker-build.sh stop

# 重启服务
./docker-build.sh restart

# 查看日志
./docker-build.sh logs

# 查看状态
./docker-build.sh status

# 清理资源
./docker-build.sh clean
```

### Docker Compose 命令

```bash
# 启动服务（前台）
docker-compose up

# 启动服务（后台）
docker-compose up -d

# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up --build

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🔍 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   lsof -i :80
   lsof -i :8000
   
   # 修改 docker-compose.yml 中的端口映射
   ```

2. **内存不足**
   ```bash
   # 检查 Docker 内存限制
   docker system df
   docker system prune
   ```

3. **权限问题**
   ```bash
   # 确保目录权限正确
   sudo chown -R $USER:$USER ./storage ./logs
   ```

4. **网络问题**
   ```bash
   # 重建网络
   docker network rm smart-doc-network
   docker-compose up -d
   ```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f --tail=100
```

### 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查前端状态
curl http://localhost/

# 查看容器健康状态
docker-compose ps
```

## 🔒 安全建议

1. **生产环境配置**
   - 修改默认密钥和密码
   - 限制 CORS 允许的源
   - 使用 HTTPS
   - 配置防火墙规则

2. **数据备份**
   ```bash
   # 备份数据卷
   docker run --rm -v smart-doc-chroma-data:/data -v $(pwd):/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .
   
   # 恢复数据卷
   docker run --rm -v smart-doc-chroma-data:/data -v $(pwd):/backup alpine tar xzf /backup/chroma-backup.tar.gz -C /data
   ```

3. **监控和日志**
   - 配置日志轮转
   - 设置监控告警
   - 定期检查资源使用情况

## 📊 性能优化

1. **资源限制**
   ```yaml
   # 在 docker-compose.yml 中添加
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '1.0'
   ```

2. **缓存优化**
   - 启用 Redis 缓存
   - 配置 Nginx 静态文件缓存
   - 使用多阶段构建减小镜像大小

## 🆙 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建并部署
./docker-build.sh deploy

# 3. 或者手动更新
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📞 支持

如果遇到问题，请：

1. 查看日志文件
2. 检查环境配置
3. 参考故障排除部分
4. 提交 Issue 到项目仓库