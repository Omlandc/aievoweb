#!/bin/bash
# trigger-auto-search.sh — 触发AI新工具自动搜索
# 由crontab每3天调用一次

TRIGGER_FILE="/tmp/.trigger-auto-search-ai-tools"
TRIGGER_LOG="/tmp/auto-search-trigger.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发AI新工具自动搜索" >> "$TRIGGER_LOG"

# 创建触发文件，包含时间戳和请求信息
cat > "$TRIGGER_FILE" << EOF
TRIGGER_TIME=$(date +%s)
TRIGGER_DATE=$(date '+%Y-%m-%d %H:%M:%S')
REQUEST=search_new_ai_tools_2026
STATUS=pending
EOF

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 触发文件已创建: $TRIGGER_FILE" >> "$TRIGGER_LOG"
