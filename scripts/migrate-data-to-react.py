#!/usr/bin/env python3
"""
数据迁移脚本：将JSON数据库转换为TypeScript模块
用于React重写项目
"""
import json
import os
import re

PROJECT_DIR = '/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网'
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
SRC_DIR = os.path.join(PROJECT_DIR, 'src')

def escape_ts_string(s):
    """转义字符串用于TypeScript"""
    if not s:
        return ''
    s = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
    return s

def migrate_tools():
    """迁移工具数据库"""
    filepath = os.path.join(DATA_DIR, 'tools-database.json')
    with open(filepath, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    tools = db.get('tools', [])
    
    # 生成TypeScript文件
    ts_lines = [
        "export interface Tool {",
        "  id: string;",
        "  name: string;",
        "  nameZh?: string;",
        "  description: string;",
        "  descriptionZh?: string;",
        "  link: string;",
        "  icon?: string;",
        "  category: string;",
        "  tags: string[];",
        "  rating?: number;",
        "  pricing?: string;",
        "  pricingZh?: string;",
        "  featured?: boolean;",
        "  pros?: string[];",
        "  cons?: string[];",
        "  useCases?: string[];",
        "  alternatives?: string[];",
        "}",
        "",
        "export const tools: Tool[] = ["
    ]
    
    for tool in tools:
        ts_lines.append("  {")
        for key, value in tool.items():
            if isinstance(value, str):
                ts_lines.append(f'    {key}: "{escape_ts_string(value)}",')
            elif isinstance(value, list):
                items = [f'"{escape_ts_string(v)}"' for v in value]
                ts_lines.append(f'    {key}: [{", ".join(items)}],')
            elif isinstance(value, bool):
                ts_lines.append(f'    {key}: {str(value).lower()},')
            elif isinstance(value, (int, float)):
                ts_lines.append(f'    {key}: {value},')
        ts_lines.append("  },")
    
    ts_lines.append("];")
    ts_lines.append("")
    ts_lines.append(f"export const toolsCount = {len(tools)};")
    
    # 添加分类统计
    categories = {}
    for tool in tools:
        cat = tool.get('category', '其他')
        categories[cat] = categories.get(cat, 0) + 1
    
    ts_lines.append("")
    ts_lines.append("export const categoryStats: Record<string, number> = {")
    for cat, count in sorted(categories.items()):
        ts_lines.append(f'  "{cat}": {count},')
    ts_lines.append("};")
    
    # 添加所有标签
    all_tags = set()
    for tool in tools:
        for tag in tool.get('tags', []):
            all_tags.add(tag)
    
    ts_lines.append("")
    ts_lines.append("export const allTags: string[] = [")
    for tag in sorted(all_tags):
        ts_lines.append(f'  "{escape_ts_string(tag)}",')
    ts_lines.append("];")
    
    output_path = os.path.join(SRC_DIR, 'data', 'tools.ts')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ts_lines))
    
    print(f"[Migrate] tools.ts: {len(tools)} tools, {len(categories)} categories, {len(all_tags)} tags")

def migrate_tasks():
    """迁移任务数据"""
    tasks_path = os.path.join(DATA_DIR, 'tasks-index.json')
    if not os.path.exists(tasks_path):
        # 从任务页生成
        tasks_dir = os.path.join(PROJECT_DIR, 'tasks')
        if not os.path.exists(tasks_dir):
            print("[Migrate] No tasks data found")
            return
        
        tasks = []
        for fname in os.listdir(tasks_dir):
            if not fname.endswith('.html'):
                continue
            task_id = fname.replace('.html', '')
            html = open(os.path.join(tasks_dir, fname), 'r', encoding='utf-8').read()
            
            # 提取标题
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            title = title_match.group(1) if title_match else task_id
            
            # 提取描述
            desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.IGNORECASE)
            description = desc_match.group(1) if desc_match else ''
            
            # 提取工具数量
            count = len(re.findall(r'href="/tools/([^"]+)\.html"', html))
            
            tasks.append({
                'id': task_id,
                'title': title,
                'description': description,
                'toolCount': count
            })
    else:
        with open(tasks_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            tasks = data.get('tasks', [])
        else:
            tasks = data if isinstance(data, list) else []
    
    ts_lines = [
        "export interface Task {",
        "  id: string;",
        "  title: string;",
        "  description?: string;",
        "  toolCount: number;",
        "  tags?: string[];",
        "}",
        "",
        "export const tasks: Task[] = ["
    ]
    
    for task in tasks:
        ts_lines.append("  {")
        for key, value in task.items():
            if isinstance(value, str):
                ts_lines.append(f'    {key}: "{escape_ts_string(value)}",')
            elif isinstance(value, list):
                items = [f'"{escape_ts_string(v)}"' for v in value]
                ts_lines.append(f'    {key}: [{", ".join(items)}],')
            elif isinstance(value, (int, float)):
                ts_lines.append(f'    {key}: {value},')
        ts_lines.append("  },")
    
    ts_lines.append("];")
    
    output_path = os.path.join(SRC_DIR, 'data', 'tasks.ts')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ts_lines))
    
    print(f"[Migrate] tasks.ts: {len(tasks)} tasks")

def migrate_tweets():
    """迁移推文数据"""
    tweets_path = os.path.join(DATA_DIR, 'tweets.json')
    if not os.path.exists(tweets_path):
        print("[Migrate] No tweets data found")
        return
    
    with open(tweets_path, 'r', encoding='utf-8') as f:
        tweets = json.load(f)
    
    if isinstance(tweets, dict):
        tweets = tweets.get('tweets', [])
    
    # 取最新50条
    tweets = tweets[:50]
    
    ts_lines = [
        "export interface Tweet {",
        "  id: string;",
        "  title?: string;",
        "  content: string;",
        "  link?: string;",
        "  source?: string;",
        "  category?: string;",
        "  date?: string;",
        "  published?: boolean;",
        "}",
        "",
        "export const tweets: Tweet[] = ["
    ]
    
    for tweet in tweets:
        if not isinstance(tweet, dict):
            continue
        ts_lines.append("  {")
        for key, value in tweet.items():
            if isinstance(value, str):
                ts_lines.append(f'    {key}: "{escape_ts_string(value)}",')
            elif isinstance(value, bool):
                ts_lines.append(f'    {key}: {str(value).lower()},')
            elif isinstance(value, (int, float)):
                ts_lines.append(f'    {key}: {value},')
        ts_lines.append("  },")
    
    ts_lines.append("];")
    
    output_path = os.path.join(SRC_DIR, 'data', 'tweets.ts')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ts_lines))
    
    print(f"[Migrate] tweets.ts: {len(tweets)} tweets")

def main():
    print("🔧 数据迁移脚本启动")
    print("=" * 50)
    
    os.makedirs(os.path.join(SRC_DIR, 'data'), exist_ok=True)
    os.makedirs(os.path.join(SRC_DIR, 'components'), exist_ok=True)
    os.makedirs(os.path.join(SRC_DIR, 'pages'), exist_ok=True)
    os.makedirs(os.path.join(SRC_DIR, 'lib'), exist_ok=True)
    
    migrate_tools()
    migrate_tasks()
    migrate_tweets()
    
    print("=" * 50)
    print("✅ 数据迁移完成")

if __name__ == '__main__':
    main()
