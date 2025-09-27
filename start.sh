#!/bin/bash

# 启动脚本 - 用于简化项目的依赖安装、开发服务器启动、测试运行等操作

# 设置环境变量以消除常见警告
export TOKENIZERS_PARALLELISM=false  # 禁止HuggingFace tokenizers并行处理警告
export PYTHONWARNINGS="ignore::DeprecationWarning,ignore::UserWarning:langchain"

# 加载用户环境变量
source .env 2>/dev/null || echo "未找到.env文件，使用默认配置"

# 确保脚本在出错时退出
set -e

# 清空向量数据库和本地文本缓存
clear_data() {
    echo "正在清空向量数据库和本地文本缓存..."
    
    # 获取向量数据库路径（默认为./chroma_db）
    VECTOR_STORE_PATH="${VECTOR_STORE_PATH:-./chroma_db}"
    DOCUMENT_STORAGE_PATH="${DOCUMENT_STORAGE_PATH:-./storage/documents}"
    
    # 清空向量数据库
    if [ -d "$VECTOR_STORE_PATH" ]; then
        echo "正在清空向量数据库：$VECTOR_STORE_PATH"
        rm -rf "$VECTOR_STORE_PATH"/*
    fi
    
    # 清空本地文本缓存
    if [ -d "$DOCUMENT_STORAGE_PATH" ]; then
        echo "正在清空本地文本缓存：$DOCUMENT_STORAGE_PATH"
        rm -rf "$DOCUMENT_STORAGE_PATH"/*
    fi
    
    echo "数据清空完成"
}

# 安装依赖
install_deps() {
    echo "正在安装依赖..."
    pip install -r requirements.txt
}

# 启动开发服务器
start_dev_server() {
    # 清空数据
    clear_data
    echo "正在启动开发服务器..."
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# 运行测试
run_tests() {
    echo "正在运行测试..."
    python -m unittest discover tests
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo "选项:" 
    echo "  install    安装依赖"
    echo "  run        启动开发服务器"
    echo "  test       运行测试"
    echo "  all        安装依赖并启动服务器"
    echo "  help       显示帮助信息"
}

# 根据参数执行相应的操作
case "$1" in
    install)
        install_deps
        ;;
    run)
        start_dev_server
        ;;
    test)
        run_tests
        ;;
    all)
        install_deps
        start_dev_server
        ;;
    help)
        show_help
        ;;
    *)
        echo "未提供有效的选项，请使用以下选项之一："
        show_help
        exit 1
        ;;
esac