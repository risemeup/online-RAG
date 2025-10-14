#!/bin/bash

# Docker 构建和部署脚本

set -e  # 遇到错误时退出

echo "🐳 Smart Doc Assistant Docker 构建脚本"
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印彩色消息
print_message() {
    echo -e "${2}${1}${NC}"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_message "❌ Docker 未安装，请先安装 Docker" $RED
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_message "❌ Docker Compose 未安装，请先安装 Docker Compose" $RED
        exit 1
    fi
    
    print_message "✅ Docker 环境检查通过" $GREEN
}

# 检查环境文件
check_env() {
    if [ ! -f ".env" ]; then
        print_message "⚠️  .env 文件不存在，创建示例文件..." $YELLOW
        exit 1
    else
        print_message "✅ .env 文件存在" $GREEN
    fi
}

# 构建镜像（完整构建，不使用缓存）
build_images() {
    print_message "🔨 开始构建 Docker 镜像（完整构建）..." $BLUE
    
    # 使用 docker-compose 构建所有镜像，不使用缓存
    print_message "📦 使用 docker-compose 构建镜像（无缓存）..." $BLUE
    docker-compose build --no-cache
    
    print_message "✅ 镜像构建完成" $GREEN
}

# 快速构建镜像（使用缓存）
build_images_fast() {
    print_message "🔨 开始快速构建 Docker 镜像..." $BLUE
    
    # 使用 docker-compose 构建所有镜像，使用缓存
    print_message "📦 使用 docker-compose 快速构建镜像..." $BLUE
    docker-compose build
    
    print_message "✅ 镜像构建完成" $GREEN
}

# 启动服务
start_services() {
    print_message "🚀 启动服务..." $BLUE
    docker-compose up -d
    
    print_message "⏳ 等待服务启动..." $YELLOW
    sleep 10
    
    # 检查服务状态
    print_message "📊 检查服务状态..." $BLUE
    docker-compose ps
    
    print_message "🎉 服务启动完成！" $GREEN
    print_message "📱 前端地址: http://localhost" $BLUE
    print_message "📚 API文档: http://localhost:8000/docs" $BLUE
    print_message "🔧 后端API: http://localhost:8000" $BLUE
}

# 停止服务
stop_services() {
    print_message "🛑 停止服务..." $YELLOW
    docker-compose down
    print_message "✅ 服务已停止" $GREEN
}

# 清理资源
cleanup() {
    print_message "🧹 清理 Docker 资源..." $YELLOW
    docker-compose down -v --rmi all
    print_message "✅ 清理完成" $GREEN
}

# 查看日志
show_logs() {
    print_message "📋 显示服务日志..." $BLUE
    docker-compose logs -f
}

# 主菜单
show_menu() {
    echo ""
    print_message "请选择操作:" $BLUE
    echo "1) 构建镜像（完整构建，无缓存）"
    echo "2) 快速构建镜像（使用缓存）"
    echo "3) 启动服务"
    echo "4) 停止服务"
    echo "5) 重启服务"
    echo "6) 查看日志"
    echo "7) 查看状态"
    echo "8) 清理资源"
    echo "9) 完整部署（构建+启动）"
    echo "0) 退出"
    echo ""
}

# 主逻辑
main() {
    check_docker
    check_env
    
    if [ $# -eq 0 ]; then
        # 交互模式
        while true; do
            show_menu
            read -p "请输入选项 (0-9): " choice
            
            case $choice in
                1)
                    build_images
                    ;;
                2)
                    build_images_fast
                    ;;
                3)
                    start_services
                    ;;
                4)
                    stop_services
                    ;;
                5)
                    stop_services
                    start_services
                    ;;
                6)
                    show_logs
                    ;;
                7)
                    docker-compose ps
                    ;;
                8)
                    cleanup
                    ;;
                9)
                    build_images
                    start_services
                    ;;
                0)
                    print_message "👋 再见！" $GREEN
                    exit 0
                    ;;
                *)
                    print_message "❌ 无效选项，请重新选择" $RED
                    ;;
            esac
            
            echo ""
            read -p "按回车键继续..."
        done
    else
        # 命令行模式
        case $1 in
            build)
                build_images
                ;;
            build-fast)
                build_images_fast
                ;;
            start)
                start_services
                ;;
            stop)
                stop_services
                ;;
            restart)
                stop_services
                start_services
                ;;
            logs)
                show_logs
                ;;
            status)
                docker-compose ps
                ;;
            clean)
                cleanup
                ;;
            deploy)
                build_images
                start_services
                ;;
            *)
                echo "用法: $0 [build|build-fast|start|stop|restart|logs|status|clean|deploy]"
                echo "或者直接运行 $0 进入交互模式"
                echo ""
                echo "参数说明:"
                echo "  build      - 完整构建镜像（无缓存）"
                echo "  build-fast - 快速构建镜像（使用缓存）"
                echo "  start      - 启动服务"
                echo "  stop       - 停止服务"
                echo "  restart    - 重启服务"
                echo "  logs       - 查看日志"
                echo "  status     - 查看状态"
                echo "  clean      - 清理资源"
                echo "  deploy     - 完整部署（构建+启动）"
                exit 1
                ;;
        esac
    fi
}

# 执行主函数
main "$@"