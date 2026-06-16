# Heartbeat Tasks

## RSS 自动翻译
- 检查文件: `data/raw-rss.json`
- 对比: `data/tweets.json` 中已有 ID
- 如果有新内容: 自动翻译标题 → 生成双语推文 → git push
- 如果无新内容: 跳过

## 检查频率
- 每次 Heartbeat 都检查
- 通常每 30-60 分钟一次
- 差值: 最多延迟 1 小时处理 RSS 更新
