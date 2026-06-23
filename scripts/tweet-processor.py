#!/usr/bin/env python3
"""
推文自动处理器+发布器
功能：
1. 读取 raw-rss.json 中的RSS数据
2. 筛选有价值的内容
3. 生成中文推文摘要
4. 发布到微博
5. 更新 tweets.json 和 tweets.html

由crontab每2小时运行一次
"""

import json
import os
import sys
import re
from datetime import datetime, timezone

# 项目目录（脚本在 scripts/ 下，需要到上级目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

def load_raw():
    """加载RSS原始数据"""
    filepath = os.path.join(PROJECT_DIR, "data", "raw-rss.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] 无法读取 raw-rss.json: {e}")
        return []

def load_tweets():
    """加载已有推文"""
    filepath = os.path.join(PROJECT_DIR, "data", "tweets.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def extract_keywords(title, summary):
    """提取关键词用于分类"""
    text = (title + " " + summary).lower()
    
    ai_keywords = ['ai', '人工智能', 'gpt', 'llm', '模型', 'chatgpt', 'claude', 'llama', 'openai', 'anthropic']
    dev_keywords = ['code', '编程', 'github', '开发者', 'api', 'framework', '开源', 'open source', 'git']
    product_keywords = ['产品', '发布', 'launch', 'new', '新品', 'startup', '融资']
    
    scores = {'AI': 0, '编程': 0, '产品': 0}
    
    for k in ai_keywords:
        if k in text:
            scores['AI'] += 1
    for k in dev_keywords:
        if k in text:
            scores['编程'] += 1
    for k in product_keywords:
        if k in text:
            scores['产品'] += 1
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else '科技'

def clean_text(text, max_len=200):
    """清理文本"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

def generate_summary(title, summary, source):
    """生成中文推文摘要"""
    clean_summary = clean_text(summary, 150)
    
    # 根据来源调整语气
    source_prefix = {
        'Hacker News': 'HN热帖',
        'TechCrunch': 'TC报道',
        'Product Hunt': 'PH今日新品',
        'OpenAI Blog': 'OpenAI官方',
        '36氪': '36kr',
        '少数派': 'sspai',
        '爱范儿': 'ifanr',
        '阮一峰': 'ruanyf',
    }.get(source, source)
    
    category = extract_keywords(title, summary)
    
    # 构建推文
    tweet = f"【{source_prefix} | {category}】{title}\n"
    if clean_summary:
        tweet += f"{clean_summary}\n"
    
    return tweet.strip()

def process_rss():
    """处理RSS数据，生成新推文"""
    raw_items = load_raw()
    existing_tweets = load_tweets()
    existing_ids = {t.get("id", "") for t in existing_tweets}
    
    print(f"[RSS] 原始数据: {len(raw_items)} 条")
    print(f"[RSS] 已有推文: {len(existing_tweets)} 条")
    
    # 筛选未处理的内容（最近7天的）
    new_items = []
    cutoff = datetime.now(timezone.utc).timestamp() - (7 * 24 * 3600)
    
    for item in raw_items:
        item_id = item.get("id", "")
        if item_id in existing_ids:
            continue
        
        # 检查时间
        fetched = item.get("fetched_at", "")
        if fetched:
            try:
                dt = datetime.fromisoformat(fetched.replace('Z', '+00:00'))
                if dt.timestamp() < cutoff:
                    continue
            except:
                pass
        
        new_items.append(item)
    
    print(f"[RSS] 待处理: {len(new_items)} 条")
    
    if not new_items:
        return []
    
    # 按来源去重，每来源最多2条
    by_source = {}
    for item in new_items:
        source = item.get("source", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)
    
    # 生成推文
    new_tweets = []
    for source, items in by_source.items():
        for item in items[:2]:  # 每来源最多2条
            tweet_text = generate_summary(
                item.get("title", ""),
                item.get("summary", ""),
                source
            )
            
            if not tweet_text or len(tweet_text) < 20:
                continue
            
            new_tweets.append({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "content": tweet_text,
                "link": item.get("link", ""),
                "source": source,
                "category": extract_keywords(item.get("title", ""), item.get("summary", "")),
                "lang": item.get("lang", "en"),
                "type": "short" if len(tweet_text) < 150 else "long",
                "date": item.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                "created": datetime.now(timezone.utc).isoformat(),
                "published": False  # 标记是否已发布
            })
    
    print(f"[Process] 生成 {len(new_tweets)} 条新推文")
    return new_tweets

def save_tweets(tweets):
    """保存推文到tweets.json"""
    filepath = os.path.join(PROJECT_DIR, "data", "tweets.json")
    
    existing = load_tweets()
    existing_ids = {t.get("id", "") for t in existing}
    
    # 合并
    for t in tweets:
        if t.get("id") not in existing_ids:
            existing.append(t)
    
    # 排序，最新的在前
    existing.sort(key=lambda x: x.get("created", ""), reverse=True)
    existing = existing[:100]  # 保留最近100条
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    print(f"[Save] 已保存 {len(existing)} 条推文")
    return existing

def generate_tweets_html(tweets):
    """生成 tweets.html 页面"""
    filepath = os.path.join(PROJECT_DIR, "tweets.html")
    
    # 生成推文卡片HTML
    tweet_cards = []
    for tweet in tweets[:20]:  # 最新20条
        content = tweet.get("content", "").replace("\n", "<br>")
        link = tweet.get("link", "")
        source = tweet.get("source", "")
        date = tweet.get("date", "")
        category = tweet.get("category", "科技")
        
        card = f'''<div class="tweet-card">
      <div class="tweet-meta">
        <span class="tweet-source">{source}</span>
        <span class="tweet-category">{category}</span>
        <span class="tweet-date">{date}</span>
      </div>
      <div class="tweet-content">{content}</div>
      {f'<a href="{link}" class="tweet-link" target="_blank">阅读原文 →</a>' if link else ''}
    </div>'''
        tweet_cards.append(card)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI推文流 | AI工具发现</title>
  <meta name="description" content="AI领域最新动态、产品发布、技术新闻聚合">
  <link rel="stylesheet" href="css/style.css">
  <style>
    .tweet-container {{ max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
    .tweet-card {{ background: var(--glass); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 1.5rem; margin-bottom: 1rem; transition: transform 0.2s; }}
    .tweet-card:hover {{ transform: translateY(-2px); }}
    .tweet-meta {{ display: flex; gap: 0.5rem; margin-bottom: 0.5rem; flex-wrap: wrap; }}
    .tweet-source {{ color: var(--accent); font-weight: 600; }}
    .tweet-category {{ background: var(--glass); padding: 0.1rem 0.5rem; border-radius: 20px; font-size: 0.75rem; }}
    .tweet-date {{ color: var(--text-secondary); font-size: 0.8rem; }}
    .tweet-content {{ line-height: 1.6; margin: 0.5rem 0; }}
    .tweet-link {{ color: var(--accent); text-decoration: none; }}
    .tweet-link:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <nav class="navbar"><div class="nav-inner">
    <a href="/" class="logo">🔍 AI工具发现</a>
    <div class="nav-links">
      <a href="index.html">发现</a>
      <a href="top10/code.html">🏆 排行榜</a>
      <a href="tweets.html" class="active">推文</a>
    </div>
  </div></nav>

  <div class="tweet-container">
    <h1>📰 AI推文流</h1>
    <p class="subtitle">来自全球科技媒体的最新AI动态</p>
    {chr(10).join(tweet_cards) if tweet_cards else '<p class="empty">暂无推文，请稍后查看...</p>'}
  </div>

  <footer class="footer"><p>AI进化网站，你进化想法。</p></footer>
</body>
</html>'''
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"[HTML] 已生成 tweets.html ({len(tweets)} 条推文)")

def publish_to_weibo(tweets):
    """发布未发布的推文到微博
    
    注意：此函数需要在OpenClaw环境中运行，使用weibo工具
    当前版本仅标记为已发布，实际发布需要手动调用或heartbeat触发
    """
    unpublished = [t for t in tweets if not t.get("published", False)]
    
    if not unpublished:
        print("[Weibo] 没有待发布的推文")
        return 0
    
    # 每次最多发布3条
    to_publish = unpublished[:3]
    
    print(f"[Weibo] 待发布: {len(to_publish)} 条推文")
    
    # 标记为已发布
    for t in to_publish:
        t["published"] = True
        t["published_at"] = datetime.now(timezone.utc).isoformat()
        print(f"[Weibo] 标记发布: {t.get('title', '')[:50]}...")
    
    return len(to_publish)

def git_push():
    """Git推送"""
    try:
        import subprocess
        os.chdir(PROJECT_DIR)
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # 检查是否有变化
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("[Git] 无变化，跳过推送")
            return True
        
        subprocess.run(
            ["git", "commit", "-m", f"auto: RSS推文更新 {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            check=True, capture_output=True
        )
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("[Git] ✅ 推送成功")
        return True
    except Exception as e:
        print(f"[Git] ❌ 推送失败: {e}")
        return False

def main():
    print(f"[TweetBot] 开始处理: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    # 1. 处理RSS → 生成推文
    new_tweets = process_rss()
    
    if not new_tweets:
        print("[TweetBot] 没有新内容，结束")
        return
    
    # 2. 保存推文
    all_tweets = save_tweets(new_tweets)
    
    # 3. 生成HTML页面
    generate_tweets_html(all_tweets)
    
    # 4. 标记发布（微博发布需要手动或heartbeat触发）
    published_count = publish_to_weibo(all_tweets)
    
    # 重新保存（更新published状态）
    save_tweets(all_tweets)
    
    # 5. Git推送
    git_push()
    
    print(f"[TweetBot] 完成: 新增 {len(new_tweets)} 条，本次标记发布 {published_count} 条")

if __name__ == "__main__":
    main()
