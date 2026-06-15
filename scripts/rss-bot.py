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
import subprocess

# 设置全局超时
socket.setdefaulttimeout(15)

KIMI_PATH = "/root/.local/share/uv/tools/kimi-cli/bin/kimi"
KIMI_TIMEOUT = 120  # 每源120秒

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

def translate_titles_with_kimi(titles, source_lang):
    """使用 Kimi CLI 批量翻译标题（每源调用一次）"""
    if not titles:
        return []
    
    if source_lang == 'zh':
        prompt = f"将以下 {len(titles)} 个中文科技标题翻译成英文（简洁自然，像原生标题）。\n\n"
        for i, t in enumerate(titles, 1):
            prompt += f"{i}. {t}\n"
        prompt += f"\n只输出英文翻译，每行一个，不要编号和解释："
    else:
        prompt = f"将以下 {len(titles)} 个英文科技标题翻译成中文（精炼有力，15字以内，像科技媒体编辑写的）。\n\n"
        for i, t in enumerate(titles, 1):
            prompt += f"{i}. {t}\n"
        prompt += f"\n只输出中文翻译，每行一个，不要编号和解释："
    
    try:
        result = subprocess.run(
            [KIMI_PATH, '--quiet', '--prompt', prompt],
            capture_output=True, text=True, timeout=KIMI_TIMEOUT
        )
        
        if result.returncode != 0:
            print(f"[Kimi] Error: {result.stderr[:200]}")
            return [None] * len(titles)
        
        # 解析输出：每行一个翻译
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        
        # 去掉可能的 "To resume this session" 行
        lines = [l for l in lines if not l.startswith('To resume')]
        
        # 如果行数不够，用None填充
        while len(lines) < len(titles):
            lines.append(None)
        
        return lines[:len(titles)]
        
    except subprocess.TimeoutExpired:
        print(f"[Kimi] Timeout after {KIMI_TIMEOUT}s")
        return [None] * len(titles)
    except Exception as e:
        print(f"[Kimi] Error: {e}")
        return [None] * len(titles)

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
        
        entries = feed.entries[:3]
        
        # 提取标题和摘要
        titles = []
        summaries = []
        links = []
        dates = []
        
        for entry in entries:
            title = clean_text(entry.get('title', ''), 100)
            summary = clean_text(entry.get('summary', entry.get('description', '')), 250)
            link = entry.get('link', '')
            
            if not title or not link:
                continue
            
            published = entry.get('published', entry.get('updated', ''))
            if not published:
                published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                try:
                    dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                    published = dt.strftime("%Y-%m-%d")
                except:
                    published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            titles.append(title)
            summaries.append(summary)
            links.append(link)
            dates.append(published)
        
        if not titles:
            return []
        
        # 批量翻译标题（每源 1 次 Kimi 调用）
        source_lang = config['lang']
        print(f"[Kimi] 翻译 {config['name']} 的 {len(titles)} 个标题...")
        translated_titles = translate_titles_with_kimi(titles, source_lang)
        
        # 构建条目
        items = []
        for i in range(len(titles)):
            id_str = f"{source_id}-{titles[i]}-{dates[i]}"
            item_id = hashlib.md5(id_str.encode()).hexdigest()[:8]
            
            if source_lang == 'zh':
                # 中文源：中文是原文，英文是翻译
                zh_title = titles[i]
                en_title = translated_titles[i] if translated_titles[i] else f"[CN] {titles[i]}"
            else:
                # 英文源：英文是原文，中文是翻译
                en_title = titles[i]
                zh_title = translated_titles[i] if translated_titles[i] else f"[EN] {titles[i]}"
            
            items.append({
                "id": item_id,
                "zh": {
                    "title": zh_title,
                    "content": f"【{config['name']}】{summaries[i]}\n\n原文：{links[i]}\n\n#科技新闻",
                    "category": "#科技新闻"
                },
                "en": {
                    "title": en_title,
                    "content": f"[{config['name']}] {summaries[i]}\n\nOriginal: {links[i]}\n\n#Tech News",
                    "category": "#Tech News"
                },
                "source": config['name'],
                "date": dates[i],
                "link": links[i],
                "type": "short" if len(summaries[i]) < 150 else "long",
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
    print(f"[RSS Bot] 开始执行 (Kimi标题翻译): {datetime.now().strftime('%Y-%m-%d %H:%M')}")
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
