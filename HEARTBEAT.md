# HEARTBEAT.md - 项目自动巡检

> 每 30 分钟检查一次 aigo.homes 项目健康状态

## 巡检项

1. **关键文件存在性** — index.html, tweets.html, js/i18n-data.js, data/tweets.json 等
2. **JS 语法检查** — i18n-data.js, i18n.js 等核心脚本
3. **JSON 数据有效性** — tweets.json, index.json
4. **Git 状态** — 是否有未提交的修复需要推送
5. **上次 RSS 推送时间** — 检查 deploy-rss.sh 是否正常运行

## 发现问题时

- 小问题（如未提交的修复）：自动 git push
- 中等问题（如 JS 语法错误）：尝试自动修复，否则报告用户
- 严重问题（如核心文件缺失）：立即报告用户

## 检查命令

```bash
cd ~/.openclaw/workspace/clawdocs/projects/玩转ai进化网

# 1. 检查关键文件
# 2. 检查 JS 语法: node -c js/*.js
# 3. 检查 JSON: python3 -c "import json; json.load(open('data/tweets.json'))"
# 4. 检查 Git 状态
# 5. 检查日志: tail -5 scripts/rss-bot.log
```
