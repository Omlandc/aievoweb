# aigo.homes 全自动产品优化方案

> 原则：所有流程自动化，零手动维护。Kimi Claw 全自动执行。

## 核心策略转变

从"AI资讯搬运" → **"AI工具发现引擎"**
- 自动抓取全网AI工具发布动态
- 自动生成功能点评和标签
- 自动构建可搜索的工具数据库
- 自动更新首页和SEO页面

## 全自动架构

```
数据源
├── RSS源（已有17个）—— 发现新工具发布
├── ProductHunt RSS —— 新工具首发
├── GitHub Trending —— 开源AI项目
└── 搜索API —— 补充工具信息

自动化流水线（Kimi Claw 定时执行）
1. 抓取 → 提取工具名称/链接/描述
2. AI点评 → 生成功能一句话点评 + 中文标签 + 分类
3. 入库 → 更新 tools-database.json
4. 生成页面 → 自动创建工具详情页（SEO）
5. 更新首页 → 重新生成首页（排行榜/分类）
6. 推送 → git commit + push

用户交互
├── 邮件订阅 → 表单提交到JSON文件（自动收集）
├── 工具收藏 → localStorage（纯前端）
├── 搜索 → 前端搜索tools-database.json
└── 分类筛选 → 前端过滤
```

## 全自动内容生成策略

### 工具发现（从RSS自动提取）
- 监控 RSS 标题/摘要中的工具名（ChatGPT、Claude、Midjourney等）
- 用正则/NER自动识别新工具
- 自动访问工具官网，提取：功能描述、价格、截图
- 用AI生成：中文一句话点评 + 功能标签 + 适用场景

### 数据存储
```json
{
  "tools": [
    {
      "id": "notion-ai",
      "name": "Notion AI",
      "nameZh": "Notion AI",
      "url": "https://notion.so/product/ai",
      "icon": "📝",
      "category": "productivity",
      "categoryZh": "生产力",
      "tags": ["写作", "笔记", "AI助手"],
      "description": "AI-powered writing assistant inside Notion",
      "descriptionZh": "内置于Notion的AI写作助手，一键生成内容、续写、翻译",
      "pricing": "freemium",
      "pricingZh": "免费增值",
      "featured": true,
      "dateAdded": "2026-06-15",
      "source": "阮一峰科技周刊",
      "mentions": 5
    }
  ]
}
```

## 全自动页面生成

### 首页（自动生成）
- Hero：搜索框 + 分类快捷入口
- 本周热门：按 mentions 排序 Top 10
- 新品速递：dateAdded 最近7天
- 分类浏览：Productivity/Design/Code/Video/Audio
- 底部：5条最新推文 + 邮件订阅

### 工具详情页（自动生成）
- 每个工具一个独立HTML页面
- SEO优化：标题、描述、结构化数据
- 内容：名称、图标、点评、标签、价格、官网链接、相关工具

### 分类页（自动生成）
- /productivity.html — 生产力工具
- /design.html — 设计工具
- /code.html — 编程工具

## 变现策略（非affiliate，全自动）

1. **广告位出租**（自动化）
   - 工具卡片底部预留"赞助商推荐"位
   - 按月出租，自动轮换
   - 通过邮件自动联系厂商（模板化）

2. **数据产品**（自动化）
   - 每月自动生成"AI工具趋势报告"
   - 发布为PDF/网页，付费下载
   - 基于 mentions 和 trending 数据

3. **邮件广告**（自动化）
   - 每周邮件底部加"本周赞助商"
   - 自动插入赞助商信息

## 实施路线图（全自动）

### Phase 1: 工具数据库（1-2天）
- [ ] 创建 tools-database.json（从现有数据自动提取）
- [ ] 写 auto-tools-bot.py：从RSS提取工具名，AI生成点评
- [ ] 定时任务：每天6/14/21点运行

### Phase 2: 首页重构（2-3天）
- [ ] 自动生成新首页（工具搜索+排行榜+分类）
- [ ] 保留推文区作为次要内容
- [ ] 前端搜索功能（搜索tools-database.json）

### Phase 3: SEO页面（3-5天）
- [ ] 自动生成工具详情页（100个工具）
- [ ] 自动生成分类页
- [ ] 结构化数据标记
- [ ] 自动sitemap.xml

### Phase 4: 邮件订阅（1天）
- [ ] 订阅表单提交到JSON文件
- [ ] 自动收集邮箱
- [ ] 每周自动生成邮件内容（Top 5工具）

### Phase 5: 自动化运维（持续）
- [ ] 定时任务：每天更新工具数据库
- [ ] 定时任务：每周生成邮件
- [ ] 定时任务：每月生成趋势报告
- [ ] 健康检查：自动检测所有页面

## 数据源清单

| 数据源 | 用途 | 获取方式 |
|--------|------|----------|
| 现有RSS（17个） | 工具发现 | 已有 |
| ProductHunt RSS | 新工具首发 | https://www.producthunt.com/feed |
| GitHub Trending | 开源AI项目 | https://github.com/trending |
| 工具官网 | 功能/价格 | 自动访问 |
| 搜索API | 补充信息 | 搜索API |

## 自动化脚本清单

1. **auto-tools-bot.py** — 从RSS提取工具，AI生成点评，更新数据库
2. **generate-homepage.py** — 根据数据库生成新首页
3. **generate-tool-pages.py** — 生成每个工具的详情页
4. **generate-category-pages.py** — 生成分类页面
5. **generate-sitemap.py** — 生成sitemap.xml
6. **generate-newsletter.py** — 生成每周邮件内容
7. **deploy-all.sh** — 一键部署所有变更

## 关键设计决策

1. **不要手动** → 所有工具信息从RSS/网络自动提取，AI自动生成点评
2. **不要affiliate** → 变现靠广告位出租+数据产品+邮件赞助
3. **全自动化** → Kimi Claw 定时执行所有脚本，自动commit+push

## 成功指标

| 指标 | 当前 | 1个月 | 3个月 |
|------|------|-------|-------|
| 工具数据库 | 0 | 100 | 500 |
| 日UV | ? | 100 | 1000 |
| 邮件订阅 | 0 | 50 | 500 |
| 页面数 | 11 | 111 | 511 |
| 搜索流量 | 0 | 30% | 50% |
