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

# RSS 源配置
RSS_SOURCES = {
    "ruanyifeng": {"url": "http://www.ruanyifeng.com/blog/atom.xml", "name": "阮一峰", "lang": "zh", "weight": 1.2},
    "sspai": {"url": "https://sspai.com/feed", "name": "少数派", "lang": "zh", "weight": 1.0},
    "36kr": {"url": "https://36kr.com/feed", "name": "36氪", "lang": "zh", "weight": 1.3},
    "ifanr": {"url": "https://www.ifanr.com/feed", "name": "爱范儿", "lang": "zh", "weight": 1.0},
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
    "openai": {"url": "https://openai.com/blog/rss.xml", "name": "OpenAI Blog", "lang": "en", "weight": 1.4},
    "phys": {"url": "https://phys.org/rss-feed/", "name": "Phys.org", "lang": "en", "weight": 1.0},
    "lobsters": {"url": "https://lobste.rs/rss", "name": "Lobsters", "lang": "en", "weight": 1.1},
}

def clean_text(text, max_len=300):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

def fetch_rss(source_id, config):
    try:
        print(f"[RSS] 抓取: {config['name']} ...")
        feed = feedparser.parse(
            config['url'],
            agent='Mozilla/5.0 (compatible; RSSBot/1.0; +https://aigo.homes/)'
        )
        
        if not feed.entries:
            print(f"[RSS] ⚠️ {config['name']} 无条目")
            return []
        
        items = []
        for entry in feed.entries[:3]:
            title = clean_text(entry.get('title', ''), 100)
            summary = clean_text(entry.get('summary', entry.get('description', '')), 250)
            link = entry.get('link', '')
            
            if not title or not link:
                continue
            
            id_str = f"{source_id}-{title}-{entry.get('published', '')}"
            item_id = hashlib.md5(id_str.encode()).hexdigest()[:8]
            
            published = entry.get('published', entry.get('updated', ''))
            if not published:
                published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                try:
                    dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                    published = dt.strftime("%Y-%m-%d")
                except:
                    published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            items.append({
                "id": item_id,
                "title": title,
                "summary": summary,
                "link": link,
                "source": config['name'],
                "lang": config['lang'],
                "date": published,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "weight": config.get('weight', 1.0)
            })
        
        print(f"[RSS] ✅ {config['name']} 获取 {len(items)} 条")
        return items
    except Exception as e:
        print(f"[RSS] ❌ {config['name']} 失败: {e}")
        return []

def save_raw(items, filepath="data/raw-rss.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    filepath = os.path.join(project_dir, filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if not isinstance(existing, list):
            existing = []
    except:
        existing = []
    
    existing_ids = {item["id"] for item in existing}
    new_items = [item for item in items if item["id"] not in existing_ids]
    
    all_items = new_items + existing
    all_items.sort(key=lambda x: x.get("fetched_at", ""), reverse=True)
    all_items = all_items[:200]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_items)} 条原始数据，总计 {len(all_items)} 条")
    return all_items

def main():
    print(f"[RSS Bot] 开始抓取原始数据: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"[RSS Bot] 共 {len(RSS_SOURCES)} 个 RSS 源")
    
    all_items = []
    for source_id, config in RSS_SOURCES.items():
        items = fetch_rss(source_id, config)
        all_items.extend(items)
        time.sleep(0.5)
    
    save_raw(all_items, "data/raw-rss.json")
    print(f"[RSS Bot] 完成: 共 {len(all_items)} 条原始数据待翻译")

if __name__ == "__main__":
    main()
