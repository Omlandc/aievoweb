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
from deep_translator import MyMemoryTranslator

# 设置全局超时
socket.setdefaulttimeout(15)

# 翻译器实例
_zh_to_en = None
_en_to_zh = None

def get_translator(source, target):
    global _zh_to_en, _en_to_zh
    if source == 'zh-CN' and target == 'en-US':
        if _zh_to_en is None:
            _zh_to_en = MyMemoryTranslator(source='zh-CN', target='en-US')
        return _zh_to_en
    elif source == 'en-US' and target == 'zh-CN':
        if _en_to_zh is None:
            _en_to_zh = MyMemoryTranslator(source='en-US', target='zh-CN')
        return _en_to_zh
    return MyMemoryTranslator(source=source, target=target)

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

CATEGORIES = ["#AI工具", "#前端开发", "#产品设计", "#科技新闻", "#创业干货", "#效率工具", "#开源项目", "#AI研究", "#硬件新品"]

CATEGORY_KEYWORDS = {
    "#AI工具": ["AI工具", "ChatGPT", "Kimi", "Claude", "AI应用", "AI助手", "AI产品", "AI写作", "AI绘画", "AI编程", "AI coding", "AI agent"],
    "#前端开发": ["前端", "JavaScript", "CSS", "React", "Vue", "HTML", "Web", "browser", "DOM", "responsive", "JS", "框架", "tailwind"],
    "#产品设计": ["产品", "设计", "UX", "UI", "用户体验", "交互", "design", "prototype", "Figma", "product"],
    "#科技新闻": ["科技", "新闻", "发布", "更新", "推出", "宣布", "tech", "news", "release", "launch", "announcement"],
    "#创业干货": ["创业", "融资", "商业模式", "startup", "商业", "盈利", "marketing", "growth"],
    "#效率工具": ["效率", "工具", "生产力", "自动化", "workflow", "productivity", "tool"],
    "#开源项目": ["开源", "GitHub", "项目", "仓库", "open source", "github", "repo"],
    "#AI研究": ["论文", "模型", "训练", "算法", "研究", "paper", "model", "LLM", "transformer", "research"],
    "#硬件新品": ["芯片", "GPU", "手机", "电脑", "硬件", "device", "chip", "Apple", "NVIDIA"],
}

# 翻译缓存
TRANSLATE_CACHE = {}
CACHE_FILE = ".translate_cache.json"

def load_cache():
    global TRANSLATE_CACHE
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            TRANSLATE_CACHE = json.load(f)
    except:
        TRANSLATE_CACHE = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(TRANSLATE_CACHE, f, ensure_ascii=False, indent=2)

def translate_text(text, source_lang, target_lang):
    """翻译文本（带缓存）"""
    if not text or len(text.strip()) < 3:
        return text
    
    cache_key = f"{source_lang}:{target_lang}:{text}"
    if cache_key in TRANSLATE_CACHE:
        return TRANSLATE_CACHE[cache_key]
    
    try:
        # 限制长度，避免过长文本翻译失败
        text_short = text[:200]
        translator = get_translator(source_lang, target_lang)
        result = translator.translate(text_short)
        TRANSLATE_CACHE[cache_key] = result
        return result
    except Exception as e:
        print(f"[Translate] 失败 '{text[:50]}...': {e}")
        return text

def clean_text(text, max_len=200):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

def classify_content(title, summary):
    text = (title + " " + summary).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[cat] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else random.choice(CATEGORIES)

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
        
        tweets = []
        source_lang = config['lang']
        
        for entry in feed.entries[:3]:
            title = clean_text(entry.get('title', ''), 100)
            summary = clean_text(entry.get('summary', entry.get('description', '')), 200)
            link = entry.get('link', '')
            
            if not title or not link:
                continue
            
            id_str = f"{source_id}-{title}-{entry.get('published', '')}"
            tweet_id = hashlib.md5(id_str.encode()).hexdigest()[:8]
            category = classify_content(title, summary)
            
            # 构建双语内容
            if source_lang == 'zh':
                zh_title = title
                zh_content = f"【{config['name']}】{title}"
                if summary and len(summary) > 20:
                    zh_content += f" — {summary}"
                zh_content += f" {category}"
                
                # 自动翻译标题为英文
                en_title = translate_text(title, 'zh-CN', 'en-US')
                en_content = f"[{config['name']}] {en_title}"
                if summary and len(summary) > 20:
                    en_content += f" — {summary}"
                en_content += f" {category}"
            else:
                en_title = title
                en_content = f"[{config['name']}] {title}"
                if summary and len(summary) > 20:
                    en_content += f" — {summary}"
                en_content += f" {category}"
                
                # 自动翻译标题为中文
                zh_title = translate_text(title, 'en-US', 'zh-CN')
                zh_content = f"【{config['name']}】{zh_title}"
                if summary and len(summary) > 20:
                    zh_content += f" — {summary}"
                zh_content += f" {category}"
            
            published = entry.get('published', entry.get('updated', ''))
            if not published:
                published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            else:
                try:
                    dt = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                    published = dt.strftime("%Y-%m-%d")
                except:
                    published = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            tweets.append({
                "id": tweet_id,
                "zh": {"title": zh_title, "content": zh_content},
                "en": {"title": en_title, "content": en_content},
                "link": link,
                "source": config['name'],
                "category": category,
                "lang": source_lang,
                "type": "long" if len(title) + len(summary) > 100 else "short",
                "date": published,
                "created": datetime.now(timezone.utc).isoformat(),
                "weight": config.get('weight', 1.0)
            })
        
        print(f"[RSS] ✅ {config['name']} 获取 {len(tweets)} 条")
        return tweets
    except Exception as e:
        print(f"[RSS] ❌ {config['name']} 失败: {e}")
        return []

def select_best_tweets(all_tweets, max_count=30):
    all_tweets.sort(key=lambda x: x.get('weight', 1.0), reverse=True)
    selected = []
    category_counts = {}
    for tweet in all_tweets:
        cat = tweet.get('category', '#科技新闻')
        if category_counts.get(cat, 0) < 5:
            selected.append(tweet)
            category_counts[cat] = category_counts.get(cat, 0) + 1
        if len(selected) >= max_count:
            break
    return selected

def save_tweets(tweets, filepath="data/tweets.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    filepath = os.path.join(project_dir, filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
        if isinstance(existing, dict) and "tweets" in existing:
            existing = existing["tweets"]
        elif not isinstance(existing, list):
            existing = []
    except:
        existing = []
    
    existing_ids = {t["id"] for t in existing}
    new_tweets = [t for t in tweets if t["id"] not in existing_ids]
    
    all_tweets = new_tweets + existing
    all_tweets.sort(key=lambda x: x.get("created", ""), reverse=True)
    all_tweets = all_tweets[:300]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_tweets, f, ensure_ascii=False, indent=2)
    
    print(f"[RSS Bot] 新增 {len(new_tweets)} 条，总计 {len(all_tweets)} 条")
    return all_tweets

def main():
    load_cache()
    print(f"[RSS Bot] 开始执行: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"[RSS Bot] 缓存: {len(TRANSLATE_CACHE)} 条")
    
    all_tweets = []
    for source_id, config in RSS_SOURCES.items():
        tweets = fetch_rss(source_id, config)
        all_tweets.extend(tweets)
        time.sleep(0.5)
    
    save_cache()
    selected = select_best_tweets(all_tweets, max_count=30)
    save_tweets(selected, "data/tweets.json")
    
    print(f"[RSS Bot] 执行完成: 共 {len(selected)} 条")

if __name__ == "__main__":
    main()
