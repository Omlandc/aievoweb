#!/bin/bash
# project-health-check.sh - aigo.homes 项目健康巡检脚本

PROJECT_DIR="/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网"
LOG_FILE="$PROJECT_DIR/scripts/health-check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

ERRORS=0
WARNINGS=0

log() { echo "[$DATE] $1" >> "$LOG_FILE"; }

log "=== 开始巡检 ==="

# 1. 检查关键文件
cd "$PROJECT_DIR" || exit 1
for f in index.html tweets.html js/i18n-data.js js/i18n.js data/tweets.json css/style.css; do
  if [ ! -f "$f" ]; then
    log "❌ 缺失关键文件: $f"
    ERRORS=$((ERRORS + 1))
  fi
done

# 2. 检查 JS 语法
for f in js/i18n-data.js js/i18n.js js/mobile-nav.js; do
  if [ -f "$f" ]; then
    if ! node -c "$f" 2>/dev/null; then
      log "❌ JS 语法错误: $f"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

# 3. 检查 JSON 数据
for f in data/tweets.json data/index.json; do
  if [ -f "$f" ]; then
    if ! python3 -c "import json; json.load(open('$f'))" 2>/dev/null; then
      log "❌ JSON 格式错误: $f"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

# 4. 检查 Git 状态（是否有未推送的修复）
if [ -d .git ]; then
  UNPUSHED=$(git log origin/main..HEAD --oneline 2>/dev/null | wc -l)
  if [ "$UNPUSHED" -gt 0 ]; then
    log "⚠️ 有 $UNPUSHED 个提交未推送，自动推送..."
    git push origin main >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
      log "✅ 自动推送成功"
    else
      log "❌ 自动推送失败"
      ERRORS=$((ERRORS + 1))
    fi
  fi
  
  # 检查未提交的修改（排除运行时文件）
  UNSTAGED=$(git status --short | grep -v "raw-rss.json\|rss-bot.log\|\.tmp" | wc -l)
  if [ "$UNSTAGED" -gt 0 ]; then
    log "⚠️ 有 $UNSTAGED 个文件未提交"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# 5. 检查 RSS Bot 日志（最后运行时间）
if [ -f scripts/rss-bot.log ]; then
  LAST_LINE=$(tail -1 scripts/rss-bot.log 2>/dev/null)
  if echo "$LAST_LINE" | grep -q "失败\|error\|Error"; then
    log "❌ RSS Bot 最近运行失败: $LAST_LINE"
    ERRORS=$((ERRORS + 1))
  fi
fi

# 6. 检查推文数据量
if [ -f data/tweets.json ]; then
  TWEET_COUNT=$(python3 -c "import json; print(len(json.load(open('data/tweets.json'))))" 2>/dev/null)
  if [ "$TWEET_COUNT" -lt 10 ]; then
    log "⚠️ 推文数量过少: $TWEET_COUNT 条"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# 汇总
if [ $ERRORS -gt 0 ]; then
  log "❌ 巡检完成: 发现 $ERRORS 个错误, $WARNINGS 个警告"
  # 错误严重时可以通过微信通知（需要配置）
  echo "ERROR: $ERRORS errors found in aigo.homes"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  log "⚠️ 巡检完成: 0 个错误, $WARNINGS 个警告"
  exit 0
else
  log "✅ 巡检完成: 一切正常"
  exit 0
fi
