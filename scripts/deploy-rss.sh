#!/bin/bash
set +e

PROJECT_DIR="/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网"
LOG_FILE="$PROJECT_DIR/scripts/rss-bot.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始 RSS 抓取..." >> "$LOG_FILE"

# 1. 运行 RSS Bot 生成推文
cd "$PROJECT_DIR" || exit 1
python3 scripts/rss-bot.py >> "$LOG_FILE" 2>&1
BOT_EXIT=$?

if [ $BOT_EXIT -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ RSS Bot 执行失败 (exit: $BOT_EXIT)" >> "$LOG_FILE"
    exit 1
fi

# 2. 检查是否有新内容
git diff --quiet data/tweets.json
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ 无新推文，跳过部署" >> "$LOG_FILE"
    exit 0
fi

# 3. 提交并推送（自动 push，pull 需手动）
git add data/tweets.json && \
git commit -m "rss: $(date +%Y-%m-%d) 自动推送" && \
git push origin main >> "$LOG_FILE" 2>&1

PUSH_EXIT=$?
if [ $PUSH_EXIT -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 推送成功，Cloudflare 将自动部署" >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 推送失败 (exit: $PUSH_EXIT)" >> "$LOG_FILE"
    exit 1
fi

# 4. 日志截断（保留最近500行）
LOG_LINES=$(wc -l < "$LOG_FILE" | awk '{print $1}')
if [ "$LOG_LINES" -gt 1000 ]; then
    tail -n 500 "$LOG_FILE" > /tmp/rss-bot.tmp && mv /tmp/rss-bot.tmp "$LOG_FILE"
fi
