#!/bin/bash

# 前后端一键启动脚本

echo "🚀 Smart Doc Assistant 启动脚本"
echo "================================"

# 检查并准备宿主机 Ollama 与默认模型
ensure_ollama() {
    echo "🔎 检查宿主机 Ollama 环境..."
    if ! command -v ollama >/dev/null 2>&1; then
        echo "❌ 未检测到 Ollama，请先在宿主机安装：https://ollama.com/download"
        echo "提示：macOS 可使用 'brew install ollama' 安装。"
        exit 1
    fi

    echo "🔎 检查默认模型是否可用..."
    if ! ollama list | grep -q "llama3.1:8b"; then
        echo "📥 正在拉取默认模型（llama3.1:8b）..."
        ollama pull llama3.1:8b || { echo "❌ 模型拉取失败，请检查网络后重试"; exit 1; }
    fi
    echo "✅ 宿主机 Ollama 已就绪，默认模型可用"
}

# 启动后端
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend
    
    # 启动后端服务（后台运行）
    echo "🚀 启动后端API服务（本地模式）..."
    # 本地模式下直连宿主机 Ollama
    export OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}
    bash start.sh run &
    BACKEND_PID=$!
    
    cd ..
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
}

# 启动前端
start_frontend() {
    echo "🎨 启动前端服务..."
    cd front
    
    # 检查是否已安装依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装前端依赖..."
        pnpm install
    fi
    
    # 启动前端服务
    echo "🚀 启动前端开发服务器..."
    pnpm dev &
    FRONTEND_PID=$!
    
    cd ..
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
}

# 使用镜像（Docker Compose）启动前后端（直连宿主机 Ollama）
start_docker() {
    echo "🔧 使用镜像启动后端与前端（直连宿主机 Ollama）..."
    # 后端容器将通过 .env 中的 OLLAMA_BASE_URL=host.docker.internal:11434 访问宿主机 Ollama
    docker-compose up -d backend frontend
    echo "✅ 镜像启动完成"
    echo "📚 API: http://localhost:8000"
    echo "🖥️ 前端: http://localhost"
}

# 停止本地（后台）服务
stop_local() {
    echo "🛑 停止本地服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null && echo "✅ 后端服务已停止"
        BACKEND_PID=""
    else
        echo "ℹ️ 未检测到本地后端正在运行"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null && echo "✅ 前端服务已停止"
        FRONTEND_PID=""
    else
        echo "ℹ️ 未检测到本地前端正在运行"
    fi
}

# 显示访问信息
show_info() {
    echo ""
    echo "🎉 服务启动完成！"
    echo "================================"
    echo "📱 前端界面（本地开发）: http://localhost:5173"
    echo "📚 API文档: http://localhost:8000/docs"
    echo "🔧 API接口: http://localhost:8000"
    echo ""
    echo "💡 提示："
    echo "  - 按 Ctrl+C 停止所有服务"
    echo "  - 确保已在根目录配置 .env 文件"
    echo ""
}

# 清理函数
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ 后端服务已停止"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ 前端服务已停止"
    fi
    echo "👋 再见！"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 菜单
show_menu() {
    echo ""
    echo "请选择操作:"
    echo "1) 本地启动（后端+前端，直连宿主机 Ollama）"
    echo "2) 镜像启动（docker-compose 后端+前端）"
    echo "3) 停止本地服务"
    echo "4) 停止镜像服务"
    echo "5) 查看镜像日志"
    echo "6) 查看镜像状态"
    echo "0) 退出"
    echo ""
}

# 主流程
main() {
    if [ $# -eq 0 ] || [ "$1" = "menu" ]; then
        while true; do
            show_menu
            read -p "请输入选项 (0-6): " choice
            case $choice in
                1)
                    ensure_ollama
                    start_backend
                    sleep 3
                    start_frontend
                    show_info
                    ;;
                2)
                    ensure_ollama
                    start_docker
                    ;;
                3)
                    stop_local
                    ;;
                4)
                    echo "🛑 停止镜像服务..."
                    docker-compose down && echo "✅ 镜像服务已停止"
                    ;;
                5)
                    echo "📋 显示镜像日志 (按 Ctrl+C 退出)"
                    docker-compose logs -f
                    ;;
                6)
                    echo "📊 查看镜像服务状态"
                    docker-compose ps
                    ;;
                0)
                    echo "👋 再见！"
                    exit 0
                    ;;
                *)
                    echo "❌ 无效选项，请重新选择"
                    ;;
            esac
            echo ""
        done
    else
        MODE=${1:-local}
        if [ "$MODE" = "docker" ]; then
            ensure_ollama
            start_docker
            echo "💡 使用 'docker-compose logs -f backend' 查看后端日志，'docker-compose down' 停止服务"
        else
            ensure_ollama
            start_backend
            sleep 3  # 等待后端启动
            start_frontend
            show_info
            # 保持脚本运行（仅本地模式）
            wait
        fi
    fi
}

# 执行主流程
main "$@"