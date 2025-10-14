#!/bin/bash

# Ollama 容器内模型初始化脚本
echo "🚀 开始初始化 Ollama 模型..."

# 启动 Ollama 服务（后台运行）
ollama serve &
OLLAMA_PID=$!

# 等待 Ollama 服务启动
echo "⏳ 等待 Ollama 服务启动..."
sleep 10

# 检查服务是否可用
max_attempts=30
attempt=0
while ! ollama list > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ Ollama 服务启动超时"
        exit 1
    fi
    echo "⏳ 等待 Ollama 服务可用... (尝试 $attempt/$max_attempts)"
    sleep 2
done

echo "✅ Ollama 服务已启动"

# 检查模型是否已存在
if ollama list | grep -q "llama3.2:3b"; then
    echo "✅ llama3.2:3b 模型已存在，跳过下载"
else
    echo "📥 开始下载 llama3.2:3b 模型..."
    ollama pull llama3.2:3b
    
    if [ $? -eq 0 ]; then
        echo "✅ llama3.2:3b 模型下载完成！"
    else
        echo "❌ 模型下载失败"
        exit 1
    fi
fi

# 验证模型列表
echo "📋 当前可用模型："
ollama list

echo "🎉 模型初始化完成！"

# 保持 Ollama 服务运行
wait $OLLAMA_PID