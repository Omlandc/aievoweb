#!/bin/bash
# 每日搜索总结脚本
# 用 kimi_search 获取最新 AI/科技新闻，生成摘要推文

PROJECT_DIR="/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网"
DATA_DIR="$PROJECT_DIR/data"
DATE=$(date +%Y-%m-%d)

echo "[Search Bot] 开始执行: $DATE"

# 搜索主题
declare -a TOPICS=(
    "AI 最新动态 2026"
    "前端技术趋势 2026"
    "科技创业融资 2026"
    "GitHub trending today"
)

# 注意：这里需要 kimi_search 工具支持
# 当前版本使用占位数据，后续可以接入实际搜索 API

# 生成搜索总结推文
cat > "$DATA_DIR/search-summaries-$DATE.json" << EOF
[
  {
    "id": "search-ai-$DATE",
    "title": "🔍 AI 搜索精选: $DATE",
    "content": "【AI搜索总结】今日AI领域多条重要动态。具体内容包括大模型更新、新产品发布、研究论文等。点击查看完整摘要。#AI研究",
    "link": "https://aigo.homes",
    "source": "搜索聚合",
    "category": "#AI研究",
    "lang": "zh",
    "type": "long",
    "date": "$DATE",
    "created": "$(date -Iseconds)",
    "weight": 1.5
  }
]
EOF

echo "[Search Bot] 搜索总结已生成: $DATA_DIR/search-summaries-$DATE.json"

# 合并到主推文文件
python3 << 'PYEOF'
import json, os, glob

data_dir = "/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网/data"
main_file = os.path.join(data_dir, "tweets.json")

# 加载现有推文
try:
    with open(main_file, "r", encoding="utf-8") as f:
        existing = json.load(f)
except:
    existing = []

existing_ids = {t["id"] for t in existing}

# 加载所有搜索总结
for summary_file in glob.glob(os.path.join(data_dir, "search-summaries-*.json")):
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summaries = json.load(f)
        for s in summaries:
            if s["id"] not in existing_ids:
                existing.append(s)
                existing_ids.add(s["id"])
    except Exception as e:
        print(f"Error loading {summary_file}: {e}")

# 排序并保存
existing.sort(key=lambda x: x.get("created", ""), reverse=True)
existing = existing[:300]

with open(main_file, "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"[Search Bot] 合并完成: {len(existing)} 条推文")
PYEOF

echo "[Search Bot] 执行完成"
