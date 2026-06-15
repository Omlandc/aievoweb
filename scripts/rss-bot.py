import json
import hashlib
import re
import os
import sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from xml.etree import ElementTree as ET

# 脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_DIR, "data", "tweets.json")

RSS_SOURCES = [
    {"key": "ruanyifeng", "url": "http://www.ruanyifeng.com/blog/atom.xml", "name": "阮一峰", "lang": "zh", "type": "atom"},
    {"key": "sspai", "url": "https://sspai.com/feed", "name": "少数派", "lang": "zh", "type": "rss"},
]

CATEGORIES = ["#AI工具", "#前端开发", "#产品设计", "#科技新闻", "#创业干货", "#效率工具", "#开源项目"]

def fetch_xml(url, timeout=10):
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; RSSBot/1.0)',
            'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'
        })
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    return data.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[RSS Fetch Error] {url}: {e}")
        return None

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = text.replace('&nbsp;', ' ')
    return text.strip()

def parse_atom(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//atom:entry', ns):
            title = entry.find('atom:title', ns)
            link = entry.find('atom:link', ns)
            summary = entry.find('atom:summary', ns)
            content = entry.find('atom:content', ns)
            updated = entry.find('atom:updated', ns)
            
            title_text = title.text if title is not None and title.text else "无标题"
            link_href = link.get('href') if link is not None else ""
            desc = summary.text if summary is not None and summary.text else ""
            if not desc and content is not None and content.text:
                desc = content.text
            date_str = updated.text if updated is not None else datetime.now(timezone.utc).isoformat()
            
            items.append({
                'title': clean_html(title_text),
                'link': link_href,
                'description': clean_html(desc)[:500],
                'date': date_str
            })
    except Exception as e:
        print(f"[Atom Parse Error] {e}")
    return items

def parse_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')
            pub_date = item.find('pubDate')
            
            title_text = title.text if title is not None and title.text else "无标题"
            link_text = link.text if link is not None and link.text else ""
            desc_text = desc.text if desc is not None and desc.text else ""
            date_str = pub_date.text if pub_date is not None else datetime.now(timezone.utc).isoformat()
            
            items.append({
                'title': clean_html(title_text),
                'link': link_text,
                'description': clean_html(desc_text)[:500],
                'date': date_str
            })
    except Exception as e:
        print(f"[RSS Parse Error] {e}")
    return items

def extract_summary(text, max_len=280):
    text = text.strip()
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_period = max(truncated.rfind('。'), truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    if last_period > max_len * 0.6:
        return truncated[:last_period+1]
    return truncated + "..."

def generate_tweet_from_item(item, source_name, category, tweet_type="short"):
    title = item.get('title', '')
    desc = item.get('description', '')
    link = item.get('link', '')
    
    content = desc if desc else title
    
    if tweet_type == "short":
        body = extract_summary(content, 200)
        tweet = f"【{source_name}】{body}"
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
    else:
        body = extract_summary(content, 400)
        tweet = f"【{source_name} | 深度】{body}\n\n原文：{link}"
    
    if category:
        tweet += f"\n\n{category}"
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    item_id = hashlib.md5(f"{source_name}-{title}-{today}".encode()).hexdigest()[:8]
    
    return {
        "id": item_id,
        "title": title[:60],
        "content": tweet,
        "link": link,
        "source": source_name,
        "category": category,
        "lang": "zh" if source_name in ["阮一峰", "少数派", "机器之心"] else "en",
        "type": tweet_type,
        "date": today,
        "created": datetime.now(timezone.utc).isoformat()
    }

def fetch_all_sources():
    import random
    tweets = []
    
    for source in RSS_SOURCES:
        print(f"[RSS] 抓取 {source['name']} ...")
        xml = fetch_xml(source['url'])
        if not xml:
            continue
        
        if source['type'] == 'atom':
            items = parse_atom(xml)
        else:
            items = parse_rss(xml)
        
        if not items:
            print(f"[RSS] {source['name']} 无内容")
            continue
        
        for item in items[:1]:
            category = random.choice(CATEGORIES) if CATEGORIES else "#科技"
            tweet_type = random.choice(["short", "long"])
            tweet = generate_tweet_from_item(item, source['name'], category, tweet_type)
            tweets.append(tweet)
            print(f"[RSS] ✓ {source['name']}: {tweet['title'][:40]}...")
    
    return tweets

def save_tweets(tweets, filepath=DATA_FILE):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "tweets" in data:
                existing = data["tweets"]
            elif isinstance(data, list):
                existing = data
            else:
                existing = []
    except (FileNotFoundError, json.JSONDecodeError):
        existing = []
    
    existing_ids = {t["id"] for t in existing}
    new_tweets = [t for t in tweets if t["id"] not in existing_ids]
    
    all_tweets = new_tweets + existing
    all_tweets.sort(key=lambda x: x.get("created", ""), reverse=True)
    all_tweets = all_tweets[:200]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"tweets": all_tweets}, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_tweets)} 条，总计 {len(all_tweets)} 条")
    return all_tweets

def main():
    print(f"[RSS Bot] {datetime.now().strftime('%Y-%m-%d %H:%M')} 开始抓取...")
    tweets = fetch_all_sources()
    if tweets:
        save_tweets(tweets)
        print(f"[RSS Bot] {datetime.now().strftime('%Y-%m-%d %H:%M')} 完成")
    else:
        print(f"[RSS Bot] 未获取到任何内容，使用备用内容")
        # 生成备用内容
        import random
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        backup = [{
            "id": hashlib.md5(f"backup-{today}".encode()).hexdigest()[:8],
            "title": "RSS 源暂时不可用",
            "content": f"【系统提示】今日 RSS 抓取遇到问题，但网站仍在自动进化中。我们已记录了这个问题，将在下次运行时尝试修复。#系统状态\n\n时间：{today}",
            "link": "https://aigo.homes",
            "source": "系统",
            "category": "#系统状态",
            "lang": "zh",
            "type": "short",
            "date": today,
            "created": datetime.now(timezone.utc).isoformat()
        }]
        save_tweets(backup)

if __name__ == "__main__":
    main()
