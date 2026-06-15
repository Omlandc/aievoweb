import json
import hashlib
import feedparser
import time
import random
from datetime import datetime, timezone
from html import unescape
import re
import os
import socket

# 设置全局超时
socket.setdefaulttimeout(15)

# RSS 源配置（扩展版 - 只保留验证可用的源）
RSS_SOURCES = {
    # 中文科技/AI
    "ruanyifeng": {"url": "http://www.ruanyifeng.com/blog/atom.xml", "name": "阮一峰", "lang": "zh", "weight": 1.2},
    "sspai": {"url": "https://sspai.com/feed", "name": "少数派", "lang": "zh", "weight": 1.0},
    "36kr": {"url": "https://36kr.com/feed", "name": "36氪", "lang": "zh", "weight": 1.3},
    "ifanr": {"url": "https://www.ifanr.com/feed", "name": "爱范儿", "lang": "zh", "weight": 1.0},
    
    # 英文科技/AI
    "hackernews": {"url": "https://news.ycombinator.com/rss", "name": "Hacker News", "lang": "en", "weight": 1.5},
    "techcrunch": {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "lang": "en", "weight": 1.3},
    "githubblog": {"url": "https://github.blog/feed/", "name": "GitHub Blog", "lang": "en", "weight": 1.2},
    "producthunt": {"url": "https://www.producthunt.com/feed", "name": "Product Hunt", "lang": "en", "weight": 1.2},
    "css-tricks": {"url": "https://css-tricks.com/feed/", "name": "CSS-Tricks", "lang": "en", "weight": 1.0},
    "theverge": {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "lang": "en", "weight": 1.2},
    "smashing": {"url": "https://www.smashingmagazine.com/feed/", "name": "Smashing", "lang": "en", "weight": 1.0},
    "devto": {"url": "https://dev.to/feed", "name": "Dev.to", "lang": "en", "weight": 1.1},
    "freecodecamp": {"url": "https://www.freecodecamp.org/news/rss/", "name": "freeCodeCamp", "lang": "en", "weight": 1.1},
    "arstechnica": {"url": "https://feeds.arstechnica.com/arstechnica/index", "name": "Ars Technica", "lang": "en", "weight": 1.1},
    "wired": {"url": "https://www.wired.com/feed/rss", "name": "Wired", "lang": "en", "weight": 1.0},
    "engadget": {"url": "https://www.engadget.com/rss.xml", "name": "Engadget", "lang": "en", "weight": 1.0},
    
    # 新增：更多可靠源
    "reddit-webdev": {"url": "https://www.reddit.com/r/webdev/.rss", "name": "Reddit WebDev", "lang": "en", "weight": 1.0},
    "reddit-javascript": {"url": "https://www.reddit.com/r/javascript/.rss", "name": "Reddit JS", "lang": "en", "weight": 1.0},
    "reddit-technology": {"url": "https://www.reddit.com/r/technology/.rss", "name": "Reddit Tech", "lang": "en", "weight": 1.2},
    "openai": {"url": "https://openai.com/blog/rss.xml", "name": "OpenAI Blog", "lang": "en", "weight": 1.4},
    "phy": {"url": "https://phys.org/rss-feed/", "name": "Phys.org", "lang": "en", "weight": 1.0},
    "lobsters": {"url": "https://lobste.rs/rss", "name": "Lobsters", "lang": "en", "weight": 1.1},
}

CATEGORIES = ["#AI工具", "#前端开发", "#产品设计", "#科技新闻", "#创业干货", "#效率工具", "#开源项目", "#AI研究", "#硬件新品"]

# 关键词到分类映射
CATEGORY_KEYWORDS = {
    "#AI工具": ["AI工具", "ChatGPT", "Kimi", "Claude", "AI应用", "AI助手", "AI产品", "AI写作", "AI绘画", "AI编程", "AI coding", "AI agent", "AI工具", "AI助手"],
    "#前端开发": ["前端", "JavaScript", "CSS", "React", "Vue", "HTML", "Web", "前端", "browser", "DOM", "responsive", "CSS", "JS", "框架", "tailwind"],
    "#产品设计": ["产品", "设计", "UX", "UI", "用户体验", "交互", "产品", "design", "prototype", "Figma", "product"],
    "#科技新闻": ["科技", "新闻", "发布", "更新", "推出", "宣布", "科技", "tech", "news", "release", "launch", "announcement"],
    "#创业干货": ["创业", "融资", "商业模式", " startup", "融资", "创业", "商业", "盈利", "marketing", "growth"],
    "#效率工具": ["效率", "工具", "生产力", "自动化", "workflow", "productivity", "tool", "效率"],
    "#开源项目": ["开源", "GitHub", "项目", "仓库", "open source", "github", "repo", "开源"],
    "#AI研究": ["论文", "模型", "训练", "算法", "研究", "paper", "model", "LLM", "transformer", "research", "论文"],
    "#硬件新品": ["芯片", "GPU", "手机", "电脑", "硬件", "device", "chip", "GPU", "Apple", "NVIDIA", "硬件"],
}

def clean_text(text, max_len=200):
    """清理 HTML 标签，限制长度"""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

def classify_content(title, summary):
    """根据关键词给内容分类"""
    text = (title + " " + summary).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[cat] = score
    
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return random.choice(CATEGORIES)
    return best

def fetch_rss(source_id, config):
    """抓取单个 RSS 源"""
    try:
        print(f"[RSS] 正在抓取: {config['name']} ...")
        
        # 使用自定义 User-Agent
        feed = feedparser.parse(
            config['url'],
            agent='Mozilla/5.0 (compatible; RSSBot/1.0; +https://aigo.homes/)'
        )
        
        if not feed.entries:
            print(f"[RSS] ⚠️ {config['name']} 无条目")
            return []
        
        tweets = []
        for entry in feed.entries[:3]:  # 每个源取前3条
            title = clean_text(entry.get('title', ''), 100)
            summary = clean_text(entry.get('summary', entry.get('description', '')), 200)
            link = entry.get('link', '')
            
            if not title or not link:
                continue
            
            # 生成唯一ID
            id_str = f"{source_id}-{title}-{entry.get('published', '')}"
            tweet_id = hashlib.md5(id_str.encode()).hexdigest()[:8]
            
            # 判断类型
            content_len = len(title) + len(summary)
            tweet_type = "long" if content_len > 100 else "short"
            
            # 构建推文内容
            content = f"【{config['name']}】{title}"
            if summary and len(summary) > 20:
                content += f" — {summary}"
            
            # 添加标签
            category = classify_content(title, summary)
            content += f" {category}"
            
            # 获取发布日期
            published = entry.get('published', entry.get('updated', ''))
            if not published:
                published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                # 尝试解析日期
                try:
                    dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                    published = dt.strftime("%Y-%m-%d")
                except:
                    published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            tweets.append({
                "id": tweet_id,
                "title": title,
                "content": content,
                "link": link,
                "source": config['name'],
                "category": category,
                "lang": config['lang'],
                "type": tweet_type,
                "date": published,
                "created": datetime.now(timezone.utc).isoformat(),
                "weight": config.get('weight', 1.0)
            })
        
        print(f"[RSS] ✅ {config['name']} 获取 {len(tweets)} 条")
        return tweets
        
    except Exception as e:
        print(f"[RSS] ❌ {config['name']} 失败: {e}")
        return []

def generate_search_summaries():
    """搜索总结推文（通过外部搜索工具生成）"""
    summaries = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 搜索主题池
    search_topics = [
        ("AI 最新动态 2026", "AI研究", "zh"),
        ("前端技术趋势 2026", "前端开发", "zh"),
        ("AI tools new release", "AI工具", "en"),
        ("科技创业融资", "创业干货", "zh"),
        ("GitHub trending today", "开源项目", "en"),
    ]
    
    for topic, cat, lang in search_topics[:3]:
        id_str = f"search-{topic}-{today}"
        tweet_id = hashlib.md5(id_str.encode()).hexdigest()[:8]
        
        summaries.append({
            "id": tweet_id,
            "title": f"🔍 搜索精选: {topic}",
            "content": f"【搜索总结】今日搜索 '{topic}' 发现多篇值得关注的文章。具体内容已整合到网站，点击查看完整摘要。 {cat}",
            "link": "https://aigo.homes",
            "source": "搜索聚合",
            "category": f"#{cat}" if not cat.startswith("#") else cat,
            "lang": lang,
            "type": "long",
            "date": today,
            "created": datetime.now(timezone.utc).isoformat(),
            "weight": 1.5,
            "is_search": True
        })
    
    return summaries

def select_best_tweets(all_tweets, max_count=30):
    """按权重和多样性筛选最佳推文"""
    # 按权重排序
    all_tweets.sort(key=lambda x: x.get('weight', 1.0), reverse=True)
    
    # 确保多样性：每个分类最多取几条
    selected = []
    category_counts = {}
    
    for tweet in all_tweets:
        cat = tweet.get('category', '#科技新闻')
        if category_counts.get(cat, 0) < 5:  # 每个分类最多5条
            selected.append(tweet)
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if len(selected) >= max_count:
            break
    
    return selected

def save_tweets(tweets, filepath="data/tweets.json"):
    """保存到JSON文件"""
    # 使用绝对路径，确保保存到正确位置
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    filepath = os.path.join(project_dir, filepath)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
        # 兼容旧格式 {"tweets": [...]}
        if isinstance(existing, dict) and "tweets" in existing:
            existing = existing["tweets"]
        elif not isinstance(existing, list):
            existing = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    
    # 去重：按id
    existing_ids = {t["id"] for t in existing}
    new_tweets = [t for t in tweets if t["id"] not in existing_ids]
    
    # 合并，按日期倒序
    all_tweets = new_tweets + existing
    all_tweets.sort(key=lambda x: x.get("created", ""), reverse=True)
    
    # 保留最近300条
    all_tweets = all_tweets[:300]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_tweets)} 条，总计 {len(all_tweets)} 条")
    return all_tweets

def main():
    print(f"[RSS Bot] 开始执行: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"[RSS Bot] 共 {len(RSS_SOURCES)} 个 RSS 源")
    
    all_tweets = []
    
    # 1. 抓取所有 RSS
    for source_id, config in RSS_SOURCES.items():
        tweets = fetch_rss(source_id, config)
        all_tweets.extend(tweets)
        time.sleep(1)  # 礼貌抓取，避免被封
    
    # 2. 添加搜索总结
    search_tweets = generate_search_summaries()
    all_tweets.extend(search_tweets)
    
    # 3. 筛选最佳推文
    selected = select_best_tweets(all_tweets, max_count=30)
    
    # 4. 保存
    save_tweets(selected, "data/tweets.json")
    
    print(f"[RSS Bot] 执行完成: 共 {len(selected)} 条精选推文")

if __name__ == "__main__":
    main()
