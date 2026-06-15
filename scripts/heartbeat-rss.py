#!/usr/bin/env python3
"""
Heartbeat RSS 处理 - 由 Kimi Claw 自动运行

用法:
  python3 scripts/heartbeat-rss.py
  
工作流程:
  1. 读取 data/raw-rss.json（已抓取的原始数据）
  2. 筛选有价值的内容（去重、去噪）
  3. 调用 Kimi CLI 批量翻译标题
  4. 生成双语推文，保存到 data/tweets.json
  5. Git 推送
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
import hashlib

KIMI_PATH = "/root/.local/share/uv/tools/kimi-cli/bin/kimi"

def load_raw(filepath="data/raw-rss.json"):
    """加载原始 RSS 数据"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def load_existing(filepath="data/tweets.json"):
    """加载已有推文"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def translate_batch(titles, source_lang):
    """使用 Kimi CLI 批量翻译标题"""
    if not titles:
        return []
    
    if source_lang == 'zh':
        prompt = f"翻译以下中文科技标题为英文（简洁自然）：\n\n"
        for i, t in enumerate(titles, 1):
            prompt += f"{i}. {t}\n"
        prompt += f"\n只输出英文翻译，每行一个："
    else:
        prompt = f"翻译以下英文科技标题为中文（精炼有力，15字以内）：\n\n"
        for i, t in enumerate(titles, 1):
            prompt += f"{i}. {t}\n"
        prompt += f"\n只输出中文翻译，每行一个："
    
    try:
        result = subprocess.run(
            [KIMI_PATH, '--quiet', '--prompt', prompt],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode != 0:
            print(f"[Kimi] Error: {result.stderr[:200]}")
            return [None] * len(titles)
        
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        lines = [l for l in lines if not l.startswith('To resume')]
        
        while len(lines) < len(titles):
            lines.append(None)
        
        return lines[:len(titles)]
        
    except subprocess.TimeoutExpired:
        print(f"[Kimi] Timeout")
        return [None] * len(titles)
    except Exception as e:
        print(f"[Kimi] Error: {e}")
        return [None] * len(titles)

def process_items(raw_items, existing_ids):
    """处理原始数据，生成双语推文"""
    new_items = []
    
    # 按来源分组
    by_source = {}
    for item in raw_items:
        if item["id"] in existing_ids:
            continue
        source = item.get("source", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)
    
    print(f"[Process] 发现 {len(by_source)} 个来源有待处理内容")
    
    for source, items in by_source.items():
        if not items:
            continue
        
        # 每源最多处理3条
        items = items[:3]
        
        # 提取标题
        titles = [item["title"] for item in items]
        source_lang = items[0].get("lang", "en")
        
        print(f"[Kimi] 翻译 {source} 的 {len(titles)} 个标题...")
        translated = translate_batch(titles, source_lang)
        
        for i, item in enumerate(items):
            if source_lang == 'zh':
                zh_title = item["title"]
                en_title = translated[i] if translated[i] else f"[CN] {item['title']}"
            else:
                en_title = item["title"]
                zh_title = translated[i] if translated[i] else f"[EN] {item['title']}"
            
            summary = item.get("summary", "")
            link = item.get("link", "")
            
            new_items.append({
                "id": item["id"],
                "zh": {
                    "title": zh_title,
                    "content": f"【{source}】{summary}\n\n原文：{link}\n\n#科技新闻",
                    "category": "#科技新闻"
                },
                "en": {
                    "title": en_title,
                    "content": f"[{source}] {summary}\n\nOriginal: {link}\n\n#Tech News",
                    "category": "#Tech News"
                },
                "source": source,
                "date": item.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
                "link": link,
                "type": "short" if len(summary) < 150 else "long",
                "created": datetime.now(timezone.utc).isoformat()
            })
        
        time.sleep(1)
    
    return new_items

def save_tweets(items, filepath="data/tweets.json"):
    """保存推文"""
    existing = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except:
        pass
    
    if not isinstance(existing, list):
        existing = []
    
    all_items = items + existing
    all_items.sort(key=lambda x: x.get("created", ""), reverse=True)
    all_items = all_items[:100]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    
    return all_items

def git_push():
    """Git 推送"""
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "auto: heartbeat RSS update"], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True)
        print("[Git] ✅ 推送成功")
        return True
    except Exception as e:
        print(f"[Git] ❌ 推送失败: {e}")
        return False

def main():
    print(f"[Heartbeat] 开始处理: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    raw = load_raw()
    existing = load_existing()
    existing_ids = {item["id"] for item in existing}
    
    print(f"[Heartbeat] 原始数据: {len(raw)} 条，已有: {len(existing)} 条")
    
    new_items = process_items(raw, existing_ids)
    
    if not new_items:
        print("[Heartbeat] 没有新内容需要处理")
        return
    
    print(f"[Heartbeat] 生成 {len(new_items)} 条新推文")
    
    all_items = save_tweets(new_items)
    print(f"[Heartbeat] 总计 {len(all_items)} 条推文")
    
    git_push()
    
    print(f"[Heartbeat] 完成")

if __name__ == "__main__":
    main()
