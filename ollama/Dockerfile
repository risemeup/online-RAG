FROM ollama/ollama:latest

# 复制初始化脚本
COPY ollama-init.sh /usr/local/bin/ollama-init.sh
RUN chmod +x /usr/local/bin/ollama-init.sh

# 设置入口点
ENTRYPOINT ["/usr/local/bin/ollama-init.sh"]