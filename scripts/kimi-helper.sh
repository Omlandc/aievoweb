#!/bin/bash
# Kimi 协同助手 - 带超时保护
# 用法: ./kimi-helper.sh "你的提示词" [超时秒数]

KIMI="/root/.local/share/uv/tools/kimi-cli/bin/kimi"
PROMPT="$1"
TIMEOUT="${2:-60}"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 '你的提示词' [超时秒数]"
    exit 1
fi

# 清理 Kimi 的输出（去掉推理过程）
function clean_output() {
    grep -v '^•' | grep -v '^To resume' | grep -v '^---' | grep -v '^The user' | grep -v '^This is' | sed '/^$/d'
}

echo "[Kimi] 正在处理..."
timeout $TIMEOUT $KIMI -p "$PROMPT" 2>/dev/null | clean_output
