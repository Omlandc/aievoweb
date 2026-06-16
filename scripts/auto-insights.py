#!/usr/bin/env python3
"""
竞品启发收集器 — 搜索行业动态，生成优化任务清单
这个脚本由定时任务触发，每天自动搜索并记录可执行的优化想法

注意：此脚本会调用搜索API（消耗少量配额），建议每天运行1-2次
"""

import json
import os
from datetime import datetime

PROJECT_DIR = '/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网'
INSIGHTS_FILE = os.path.join(PROJECT_DIR, 'data', 'auto-insights.json')

def load_insights():
    """加载已有的insight记录"""
    if os.path.exists(INSIGHTS_FILE):
        with open(INSIGHTS_FILE, 'r') as f:
            return json.load(f)
    return {'insights': [], 'last_update': ''}

def save_insights(data):
    """保存insight记录"""
    data['last_update'] = datetime.now().isoformat()
    with open(INSIGHTS_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_search_queries():
    """生成要搜索的查询词（轮换使用，避免重复）"""
    queries = [
        "AI tools directory new features 2026",
        "AI tool discovery platform traffic strategy",
        "new AI tools launched this week 2026",
        "AI导航站 新功能 2026",
        "Futurepedia new features traffic growth",
        "AI工具推荐网站 变现模式",
    ]
    return queries

def analyze_local_data():
    """分析本地数据，发现优化机会（不消耗API）"""
    insights = []
    
    # 加载数据库
    db_path = os.path.join(PROJECT_DIR, 'data', 'tools-database.json')
    if not os.path.exists(db_path):
        return insights
    
    with open(db_path, 'r') as f:
        db = json.load(f)
    
    tools = db.get('tools', [])
    
    # 统计各类别工具数量
    cat_counts = {}
    for t in tools:
        cat = t.get('category', '其他')
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    # 发现机会：工具数量少的类别需要补充
    for cat, count in cat_counts.items():
        if count < 5:
            insights.append({
                'type': 'content_gap',
                'priority': 'medium',
                'description': f'{cat}类别仅有{count}个工具，建议扩充到10+个',
                'action': f'搜索并添加{cat}类别的AI工具',
                'auto_executable': False  # 需要人工搜索
            })
    
    # 统计总工具数
    insights.append({
        'type': 'status',
        'priority': 'info',
        'description': f'当前共{len(tools)}个工具入库',
        'action': '继续扩充工具库',
        'auto_executable': False
    })
    
    # 检查是否有新工具页面未生成
    tools_dir = os.path.join(PROJECT_DIR, 'tools')
    existing_pages = set(f.replace('.html', '') for f in os.listdir(tools_dir) if f.endswith('.html'))
    
    missing_pages = []
    for t in tools:
        tid = t.get('id', '').replace('/', '-').replace('\\', '-')
        if tid and tid not in existing_pages:
            missing_pages.append(t.get('nameZh', t.get('name', '')))
    
    if missing_pages:
        insights.append({
            'type': 'technical',
            'priority': 'high',
            'description': f'{len(missing_pages)}个工具缺少详情页: {", ".join(missing_pages[:5])}',
            'action': '运行generate-tool-pages.py生成缺失页面',
            'auto_executable': True,
            'script': 'scripts/generate-tool-pages.py'
        })
    
    return insights

def main():
    print("🔍 竞品启发收集器启动...")
    print("=" * 50)
    
    data = load_insights()
    
    # 1. 本地数据分析（零API消耗）
    print("\n📊 分析本地数据...")
    local_insights = analyze_local_data()
    
    # 2. 记录insight（带有时间戳）
    new_insights = []
    for ins in local_insights:
        ins['discovered_at'] = datetime.now().isoformat()
        ins['status'] = 'pending'
        new_insights.append(ins)
        print(f"  {'🔴' if ins['priority'] == 'high' else '🟡' if ins['priority'] == 'medium' else '🔵'} {ins['description']}")
    
    # 合并到历史记录（保留最近100条）
    data['insights'] = (new_insights + data['insights'])[:100]
    save_insights(data)
    
    print(f"\n💾 已保存 {len(new_insights)} 条优化建议到 data/auto-insights.json")
    
    # 3. 输出可自动执行的任务
    auto_tasks = [i for i in new_insights if i.get('auto_executable')]
    if auto_tasks:
        print(f"\n🤖 可自动执行的任务（{len(auto_tasks)}个）:")
        for task in auto_tasks:
            print(f"  → {task['action']}")
            if 'script' in task:
                print(f"    脚本: {task['script']}")
    
    # 4. 输出需要人工处理的任务
    manual_tasks = [i for i in new_insights if not i.get('auto_executable')]
    if manual_tasks:
        print(f"\n👤 需要人工处理的任务（{len(manual_tasks)}个）:")
        for task in manual_tasks:
            print(f"  → {task['action']}")

if __name__ == '__main__':
    main()
