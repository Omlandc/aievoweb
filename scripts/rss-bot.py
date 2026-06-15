import json
import hashlib
import re
import os
import sys
import random
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from xml.etree import ElementTree as ET

# 脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

# 双语 RSS 源配置
RSS_SOURCES = [
    {"key": "ruanyifeng", "url": "http://www.ruanyifeng.com/blog/atom.xml", "name": "阮一峰", "lang": "zh", "type": "atom"},
    {"key": "sspai", "url": "https://sspai.com/feed", "name": "少数派", "lang": "zh", "type": "rss"},
    {"key": "hackernews", "url": "https://news.ycombinator.com/rss", "name": "Hacker News", "lang": "en", "type": "rss"},
    {"key": "githubblog", "url": "https://github.blog/feed/", "name": "GitHub Blog", "lang": "en", "type": "atom"},
]

CATEGORIES = {
    "zh": ["#AI工具", "#前端开发", "#产品设计", "#科技新闻", "#创业干货", "#效率工具", "#开源项目"],
    "en": ["#AI Tools", "#Frontend", "#Product Design", "#Tech News", "#Startup", "#Productivity", "#Open Source"]
}

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
            
            title_text = title.text if title is not None and title.text else "No Title"
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
            
            title_text = title.text if title is not None and title.text else "No Title"
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

def simple_translate(text, is_title=False):
    """简单翻译：保留英文关键词，只做基础替换"""
    if not text:
        return text
    # 如果是中文内容，添加英文前缀
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return f"[Translated] {text[:50]}..." if is_title else text
    return text

def generate_tweet_bilingual(item, source_name, source_lang, tweet_type="short"):
    """生成双语推文"""
    title = item.get('title', '')
    desc = item.get('description', '')
    link = item.get('link', '')
    
    content = desc if desc else title
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    item_id = hashlib.md5(f"{source_name}-{title}-{today}".encode()).hexdigest()[:8]
    
    # 中文内容
    if source_lang == "zh":
        zh_body = extract_summary(content, 200) if tweet_type == "short" else extract_summary(content, 400)
        zh_tweet = f"【{source_name}】{zh_body}"
        if len(zh_tweet) > 280:
            zh_tweet = zh_tweet[:277] + "..."
        
        # 英文翻译（简单版）
        en_title = f"[CN] {title[:40]}" if title else "No Title"
        en_tweet = f"[{source_name}] {extract_summary(content, 250)}\n\n(Original: Chinese)"
        
        zh_cat = random.choice(CATEGORIES["zh"])
        en_cat = random.choice(CATEGORIES["en"])
    else:
        # 英文源
        en_body = extract_summary(content, 200) if tweet_type == "short" else extract_summary(content, 400)
        en_tweet = f"[{source_name}] {en_body}"
        if len(en_tweet) > 280:
            en_tweet = en_tweet[:277] + "..."
        
        # 中文翻译（简单版）
        zh_title = f"[EN] {title[:40]}" if title else "无标题"
        zh_tweet = f"【{source_name}】{extract_summary(content, 250)}\n\n（原文：英文）"
        
        zh_cat = random.choice(CATEGORIES["zh"])
        en_cat = random.choice(CATEGORIES["en"])
    
    if tweet_type == "long":
        if source_lang == "zh":
            zh_tweet += f"\n\n原文：{link}"
            en_tweet += f"\n\nOriginal: {link}"
        else:
            en_tweet += f"\n\nOriginal: {link}"
            zh_tweet += f"\n\n原文：{link}"
    
    zh_tweet += f"\n\n{zh_cat}"
    en_tweet += f"\n\n{en_cat}"
    
    return {
        "id": item_id,
        "zh": {
            "title": title[:60] if source_lang == "zh" else zh_title,
            "content": zh_tweet,
            "category": zh_cat
        },
        "en": {
            "title": title[:60] if source_lang == "en" else en_title,
            "content": en_tweet,
            "category": en_cat
        },
        "source": source_name,
        "date": today,
        "link": link,
        "type": tweet_type,
        "created": datetime.now(timezone.utc).isoformat()
    }

def get_month_file(date_str):
    """获取按月归档的文件路径"""
    month = date_str[:7]  # 2026-06
    return os.path.join(DATA_DIR, f"{month}.json")

def get_current_month_file():
    """获取当前月份的文件路径"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return get_month_file(today)

def load_month_data(filepath):
    """加载某月的数据"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "tweets" in data:
                return data["tweets"]
            elif isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_month_data(tweets, filepath):
    """保存某月的数据"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"tweets": tweets}, f, ensure_ascii=False, indent=2)

def update_index():
    """更新索引文件（只存标题、日期、文件名，极小）"""
    index = {"months": [], "total": 0}
    
    for filename in sorted(os.listdir(DATA_DIR), reverse=True):
        if filename.endswith('.json') and filename != 'index.json':
            month = filename.replace('.json', '')
            filepath = os.path.join(DATA_DIR, filename)
            tweets = load_month_data(filepath)
            
            index["months"].append({
                "month": month,
                "count": len(tweets),
                "latest": tweets[0]["date"] if tweets else month
            })
            index["total"] += len(tweets)
    
    index_path = os.path.join(DATA_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"[Index] 已更新：{len(index['months'])} 个月份，共 {index['total']} 条推文")
    return index

def fetch_all_sources():
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
            tweet_type = random.choice(["short", "long"])
            tweet = generate_tweet_bilingual(item, source['name'], source['lang'], tweet_type)
            tweets.append(tweet)
            print(f"[RSS] ✓ {source['name']}: {tweet['zh']['title'][:40] if tweet['zh']['title'] else tweet['en']['title'][:40]}...")
    
    return tweets

def main():
    print(f"[RSS Bot] {datetime.now().strftime('%Y-%m-%d %H:%M')} 开始抓取...")
    
    # 1. 抓取新推文
    tweets = fetch_all_sources()
    
    if not tweets:
        print(f"[RSS Bot] 未获取到任何内容，使用备用内容")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tweets = [{
            "id": hashlib.md5(f"backup-{today}".encode()).hexdigest()[:8],
            "zh": {
                "title": "RSS 源暂时不可用",
                "content": f"【系统提示】今日 RSS 抓取遇到问题，但网站仍在自动进化中。#系统状态\n\n时间：{today}",
                "category": "#系统状态"
            },
            "en": {
                "title": "RSS Sources Temporarily Unavailable",
                "content": f"[System Notice] RSS fetching encountered issues today, but the site is still evolving. #SystemStatus\n\nTime: {today}",
                "category": "#System Status"
            },
            "source": "系统",
            "date": today,
            "link": "https://aigo.homes",
            "type": "short",
            "created": datetime.now(timezone.utc).isoformat()
        }]
    
    # 2. 加载当月已有数据
    month_file = get_current_month_file()
    existing = load_month_data(month_file)
    
    # 3. 去重合并
    existing_ids = {t["id"] for t in existing}
    new_tweets = [t for t in tweets if t["id"] not in existing_ids]
    all_tweets = new_tweets + existing
    all_tweets.sort(key=lambda x: x.get("created", ""), reverse=True)
    
    # 4. 保存当月数据
    save_month_data(all_tweets, month_file)
    
    # 5. 更新索引
    update_index()
    
    # 6. 同时更新旧的统一文件（兼容旧版前端）
    legacy_file = os.path.join(DATA_DIR, "tweets.json")
    # 合并最近2个月的数据到 legacy 文件
    recent_tweets = []
    for filename in sorted(os.listdir(DATA_DIR), reverse=True):
        if filename.endswith('.json') and filename not in ['index.json', 'tweets.json']:
            filepath = os.path.join(DATA_DIR, filename)
            month_data = load_month_data(filepath)
            recent_tweets.extend(month_data)
            if len(recent_tweets) >= 100:
                break
    
    recent_tweets.sort(key=lambda x: x.get("created", ""), reverse=True)
    recent_tweets = recent_tweets[:100]
    
    with open(legacy_file, "w", encoding="utf-8") as f:
        json.dump({"tweets": recent_tweets}, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_tweets)} 条，本月总计 {len(all_tweets)} 条")
    print(f"[RSS Bot] {datetime.now().strftime('%Y-%m-%d %H:%M')} 完成")

if __name__ == "__main__":
    main()
