#!/bin/bash
# auto-pipeline.sh — 全自动内容更新流水线
# 每天自动执行：发现新工具 → 更新数据库 → 生成页面 → 推送
# 
# 使用方式:
#   bash scripts/auto-pipeline.sh
# 
# 建议定时：每天 06:00 / 14:00 / 21:00 各跑一次

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "========================================"
echo "🤖 AI工具发现站 — 自动更新流水线"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# ─── 步骤0: 运行竞品启发收集器 ───
echo ""
echo "🔍 步骤0: 运行竞品启发收集器（分析本地数据，发现优化机会）"
if [ -f "scripts/auto-insights.py" ]; then
    python3 scripts/auto-insights.py || echo "⚠️ Insight收集失败，继续"
else
    echo "⚠️ auto-insights.py 不存在，跳过"
fi

# ─── 步骤1: 检查Git状态 ───
echo ""
echo "📋 步骤1: 检查Git状态"
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  本地有未提交的更改，先提交..."
    git add -A
    git commit -m "auto: pre-pipeline checkpoint $(date +%Y%m%d-%H%M)"
fi

# ─── 步骤2: 运行RSS Bot发现新工具 ───
echo ""
echo "📡 步骤2: 运行RSS Bot发现新工具"
if [ -f "scripts/auto-discover-tools.py" ]; then
    python3 scripts/auto-discover-tools.py || echo "⚠️ RSS Bot运行失败，继续后续步骤"
else
    echo "⚠️ auto-discover-tools.py 不存在，跳过"
fi

# ─── 步骤3: 重新生成工具详情页 ───
echo ""
echo "📝 步骤3: 重新生成工具详情页（新工具会自动包含）"
if [ -f "scripts/generate-tool-pages.py" ]; then
    python3 scripts/generate-tool-pages.py || echo "⚠️ 工具页生成失败"
fi

# ─── 步骤4: 重新生成任务聚合页 ───
echo ""
echo "📦 步骤4: 重新生成任务聚合页"
if [ -f "scripts/generate-task-pages.py" ]; then
    python3 scripts/generate-task-pages.py || echo "⚠️ 任务页生成失败"
fi

# ─── 步骤5: 重新生成Top 10榜单页 ───
echo ""
echo "🏆 步骤5: 重新生成Top 10榜单页"
if [ -f "scripts/generate-top10.py" ]; then
    python3 scripts/generate-top10.py || echo "⚠️ Top10页生成失败"
fi

# ─── 步骤6: 重新生成首页 ───
echo ""
echo "🏠 步骤6: 重新生成首页"
if [ -f "scripts/generate-homepage.py" ]; then
    python3 scripts/generate-homepage.py || echo "⚠️ 首页生成失败"
fi

# ─── 步骤7: 更新Sitemap ───
echo ""
echo "🗺️  步骤7: 更新Sitemap"
if [ -f "scripts/generate-sitemap.py" ]; then
    python3 scripts/generate-sitemap.py || echo "⚠️ Sitemap生成失败"
fi

# ─── 步骤8: 检查变化并推送 ───
echo ""
echo "🚀 步骤8: 检查变化并推送到GitHub"

# 检查是否有变化
if git diff-index --quiet HEAD --; then
    echo "✅ 没有变化，无需推送"
else
    # 统计变化
    CHANGED_FILES=$(git diff --cached --name-only | wc -l)
    INSERTIONS=$(git diff --cached --stat | grep -o '[0-9]* insertions' | grep -o '[0-9]*' | awk '{s+=$1} END {print s}')
    DELETIONS=$(git diff --cached --stat | grep -o '[0-9]* deletions' | grep -o '[0-9]*' | awk '{s+=$1} END {print s}')
    
    echo "📊 变更统计:"
    echo "   文件数: $CHANGED_FILES"
    echo "   新增行: ${INSERTIONS:-0}"
    echo "   删除行: ${DELETIONS:-0}"
    
    # 生成提交信息
    NEW_TOOLS_COUNT=$(git diff --cached --name-only | grep -c "^tools/" || true)
    COMMIT_MSG="auto: daily update $(date +%Y-%m-%d)"
    
    if [ "$NEW_TOOLS_COUNT" -gt 0 ] 2>/dev/null; then
        COMMIT_MSG="auto: +$NEW_TOOLS_COUNT new tools + updates ($(date +%Y-%m-%d))"
    fi
    
    git add -A
    git commit -m "$COMMIT_MSG"
    
    # 推送
    if git push origin main; then
        echo "✅ 推送成功: $COMMIT_MSG"
    else
        echo "❌ 推送失败，请检查网络或权限"
        exit 1
    fi
fi

# ─── 完成 ───
echo ""
echo "========================================"
echo "✅ 流水线完成: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
