#!/bin/bash

# 前后端一键启动脚本

echo "🚀 Smart Doc Assistant 启动脚本"
echo "================================"

# 启动后端
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend
    
    # 启动后端服务（后台运行）
    echo "🚀 启动后端API服务..."
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

# 显示访问信息
show_info() {
    echo ""
    echo "🎉 服务启动完成！"
    echo "================================"
    echo "📱 前端界面: http://localhost:5173"
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

# 主流程
main() {
    start_backend
    sleep 3  # 等待后端启动
    start_frontend
    show_info
    
    # 保持脚本运行
    wait
}

# 执行主流程
main