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
import urllib.request
import urllib.parse

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

def extract_summary(entry):
    """从 RSS entry 提取摘要"""
    summary = entry.get('summary', entry.get('description', ''))
    return clean_text(summary, 250)

def translate_text(text, source_lang, target_lang):
    """使用 MyMemory API 翻译"""
    if not text or len(text.strip()) < 3:
        return text
    
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair={source_lang}|{target_lang}"
        
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (RSSBot/1.0)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('responseStatus') == 200:
                return data['responseData']['translatedText']
            else:
                print(f"[Translate] API error: {data.get('responseDetails', 'unknown')}")
                return None
    except Exception as e:
        print(f"[Translate] Error: {e}")
        return None

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
            summary = extract_summary(entry)
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
            
            source_lang = config['lang']
            
            # 构建双语内容
            if source_lang == 'zh':
                # 中文源：中文是原文，英文是翻译
                zh_title = title
                zh_content = summary
                
                # 翻译标题
                en_title = translate_text(title, 'zh-CN', 'en')
                if not en_title:
                    en_title = f"[CN] {title}"
                
                # 翻译摘要
                en_content = translate_text(summary, 'zh-CN', 'en')
                if not en_content:
                    en_content = f"[Original: Chinese]\n\n{summary[:200]}"
                
                zh_category = "#科技新闻"
                en_category = "#Tech News"
                
            else:
                # 英文源：英文是原文，中文是翻译
                en_title = title
                en_content = summary
                
                # 翻译标题
                zh_title = translate_text(title, 'en', 'zh-CN')
                if not zh_title:
                    zh_title = f"[EN] {title}"
                
                # 翻译摘要
                zh_content = translate_text(summary, 'en', 'zh-CN')
                if not zh_content:
                    zh_content = f"[原文为英文]\n\n{summary[:200]}"
                
                zh_category = "#科技新闻"
                en_category = "#Tech News"
            
            items.append({
                "id": item_id,
                "zh": {
                    "title": zh_title,
                    "content": f"【{config['name']}】{zh_content}\n\n原文：{link}\n\n{zh_category}",
                    "category": zh_category
                },
                "en": {
                    "title": en_title,
                    "content": f"[{config['name']}] {en_content}\n\nOriginal: {link}\n\n{en_category}",
                    "category": en_category
                },
                "source": config['name'],
                "date": published,
                "link": link,
                "type": "short" if len(summary) < 150 else "long",
                "created": datetime.now(timezone.utc).isoformat()
            })
        
        print(f"[RSS] ✅ {config['name']} 获取 {len(items)} 条")
        return items
    except Exception as e:
        print(f"[RSS] ❌ {config['name']} 失败: {e}")
        return []

def save_tweets(tweets, filepath="data/tweets.json"):
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
    new_items = [item for item in tweets if item["id"] not in existing_ids]
    
    all_items = new_items + existing
    all_items.sort(key=lambda x: x.get("created", ""), reverse=True)
    all_items = all_items[:100]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_items)} 条，总计 {len(all_items)} 条")
    return all_items

def main():
    print(f"[RSS Bot] 开始执行: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"[RSS Bot] 共 {len(RSS_SOURCES)} 个 RSS 源")
    
    all_items = []
    for source_id, config in RSS_SOURCES.items():
        items = fetch_rss(source_id, config)
        all_items.extend(items)
        time.sleep(1)
    
    save_tweets(all_items, "data/tweets.json")
    print(f"[RSS Bot] 完成: 共 {len(all_items)} 条推文")

if __name__ == "__main__":
    main()
