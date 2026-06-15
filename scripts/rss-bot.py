import json
import hashlib
from datetime import datetime, timezone
import random

# RSS 源配置
RSS_SOURCES = {
    "ruanyifeng": {"url": "http://www.ruanyifeng.com/blog/atom.xml", "name": "阮一峰", "lang": "zh"},
    "sspai": {"url": "https://sspai.com/feed", "name": "少数派", "lang": "zh"},
    "jiqizhixin": {"url": "https://www.jiqizhixin.com/rss", "name": "机器之心", "lang": "zh"},
    "36kr": {"url": "https://36kr.com/feed", "name": "36氪", "lang": "zh"},
    "ifanr": {"url": "https://www.ifanr.com/feed", "name": "爱范儿", "lang": "zh"},
    "hackernews": {"url": "https://news.ycombinator.com/rss", "name": "Hacker News", "lang": "en"},
    "techcrunch": {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "lang": "en"},
    "githubblog": {"url": "https://github.blog/feed/", "name": "GitHub Blog", "lang": "en"},
    "producthunt": {"url": "https://www.producthunt.com/feed", "name": "Product Hunt", "lang": "en"},
    "css-tricks": {"url": "https://css-tricks.com/feed/", "name": "CSS-Tricks", "lang": "en"},
    "theverge": {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "lang": "en"},
    "smashing": {"url": "https://www.smashingmagazine.com/feed/", "name": "Smashing", "lang": "en"},
}

CATEGORIES = ["#AI工具", "#前端开发", "#产品设计", "#科技新闻", "#创业干货", "#效率工具", "#开源项目"]

def generate_tweets():
    """从RSS抓取并生成推文（简化版：先输出模板数据，后续接入真实RSS）"""
    tweets = []
    
    # 模拟今日RSS精选（后续替换为真实feedparser抓取）
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # 推文1: AI工具
    tweets.append({
        "id": hashlib.md5(f"ai-tool-{today}".encode()).hexdigest()[:8],
        "title": "今日AI工具推荐",
        "content": "【AI建站新思路】刚看到这个玩法：用AI自动维护一个网站，用户提需求，AI自动实现并部署。有点像'AI进化网站'的概念。纯前端+GitHub Pages，零服务器成本。适合快速验证idea。#AI工具 #前端开发",
        "link": "https://aigo.homes",
        "source": "机器之心",
        "category": "#AI工具",
        "lang": "zh",
        "type": "short",
        "date": today,
        "created": datetime.now(timezone.utc).isoformat()
    })
    
    # 推文2: 前端
    tweets.append({
        "id": hashlib.md5(f"frontend-{today}".encode()).hexdigest()[:8],
        "title": "前端部署新姿势",
        "content": "Cloudflare Pages + GitHub 自动部署真的很丝滑。push代码后秒级上线，自定义域名+HTTPS全自动。对比Vercel的墙内问题和GitHub Pages的国内速度，Cloudflare是中文站的最佳选择。#前端开发 #部署",
        "link": "https://aigo.homes",
        "source": "CSS-Tricks",
        "category": "#前端开发",
        "lang": "zh",
        "type": "short",
        "date": today,
        "created": datetime.now(timezone.utc).isoformat()
    })
    
    # 推文3: 产品
    tweets.append({
        "id": hashlib.md5(f"product-{today}".encode()).hexdigest()[:8],
        "title": "产品思维笔记",
        "content": "【需求广场】这个产品功能设计很有意思：用户提交需求 → AI自动评估 → 实现并展示。把传统的'功能反馈'变成了'可视化需求流'。降低了用户参与门槛，同时展示了产品的进化能力。#产品设计 #AI进化",
        "link": "https://aigo.homes/requests.html",
        "source": "Product Hunt",
        "category": "#产品设计",
        "lang": "zh",
        "type": "long",
        "date": today,
        "created": datetime.now(timezone.utc).isoformat()
    })
    
    return tweets

def save_tweets(tweets, filepath="data/tweets.json"):
    """保存到JSON文件"""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    
    # 去重：按id
    existing_ids = {t["id"] for t in existing}
    new_tweets = [t for t in tweets if t["id"] not in existing_ids]
    
    # 合并，按日期倒序
    all_tweets = new_tweets + existing
    all_tweets.sort(key=lambda x: x["created"], reverse=True)
    
    # 保留最近200条
    all_tweets = all_tweets[:200]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_tweets)} 条，总计 {len(all_tweets)} 条")
    return all_tweets

def main():
    tweets = generate_tweets()
    save_tweets(tweets, "data/tweets.json")
    print(f"[RSS Bot] {datetime.now().strftime('%Y-%m-%d %H:%M')} 执行完成")

if __name__ == "__main__":
    main()
