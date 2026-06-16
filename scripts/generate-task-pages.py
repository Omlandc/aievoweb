#!/usr/bin/env python3
"""
按任务聚合页生成器 — 学习TAAFT策略
将工具按任务/场景聚合，生成高价值长尾页面
"""

import json
import os

PROJECT_DIR = '/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网'

def load_database():
    with open(os.path.join(PROJECT_DIR, 'data', 'tools-database.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def get_tools_by_task(tools):
    """按任务/功能聚合工具"""
    task_map = {}
    
    for tool in tools:
        tags = tool.get('tags', [])
        category = tool.get('category', '')
        
        # 从tags和category提取任务
        all_tasks = tags + [category]
        
        for task in all_tasks:
            task = task.strip().lower()
            if not task or task in ('ai', '免费', '付费', '开源', 'saas'):
                continue
            
            if task not in task_map:
                task_map[task] = []
            task_map[task].append(tool)
    
    # 只保留有3个以上工具的任务
    return {k: v for k, v in task_map.items() if len(v) >= 3}

def generate_task_page(task_name, tools_list):
    """生成任务聚合页"""
    
    # 页面标题
    title_zh = f"{task_name.capitalize()}AI工具推荐（2026年精选）"
    title_en = f"Best AI Tools for {task_name.capitalize()} in 2026"
    
    # 生成工具卡片
    tool_cards = []
    for i, tool in enumerate(tools_list[:15], 1):  # 最多15个
        name = tool.get('nameZh', tool.get('name', ''))
        name_en = tool.get('name', '')
        desc = tool.get('descriptionZh', tool.get('description', ''))[:80]
        icon = tool.get('icon', '🔧')
        tool_id = tool.get('id', '').replace('/', '-').replace('\\', '-')
        url = tool.get('url', '#')
        pricing = tool.get('pricingZh', tool.get('pricing', '免费增值'))
        
        card = f'''<div class="tool-card task-tool-card">
      <div class="tool-header">
        <span class="rank">#{i}</span>
        <span class="icon">{icon}</span>
        <h3>{name}</h3>
      </div>
      <p class="tool-desc">{desc}</p>
      <div class="tool-meta">
        <span class="tag">{pricing}</span>
      </div>
      <div class="tool-actions">
        <a href="{url}" class="btn-primary" target="_blank">访问官网</a>
        <a href="tools/{tool_id}.html" class="btn-secondary">评测详情</a>
      </div>
    </div>'''
        tool_cards.append(card)
    
    # FAQ
    faqs = [
        {"q": f"什么是{task_name}AI工具？", "a": f"{task_name}AI工具是指利用人工智能技术辅助{task_name}工作的软件。它们可以自动化处理重复性任务，提升工作效率和质量。"},
        {"q": f"{task_name}AI工具免费吗？", "a": "大部分工具提供免费试用或基础免费版，高级功能通常需要付费。建议先试用免费版评估是否满足需求。"},
        {"q": f"如何选择适合自己的{task_name}AI工具？", "a": "建议根据你的具体需求、预算、团队规模来选择。可以参考我们的评测对比，也可以直接试用几款工具后做决定。"},
    ]
    
    faq_html = '\n'.join([
        f'''<div class="faq-item">
      <h3 class="faq-q">{f["q"]}</h3>
      <p class="faq-a">{f["a"]}</p>
    </div>'''
        for f in faqs
    ])
    
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ]
    }
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_zh} | AI工具发现</title>
  <meta name="description" content="2026年最佳{task_name}AI工具排行榜。功能对比、价格、优缺点详解。基于{len(tools_list)}款工具精选。">
  <link rel="canonical" href="https://aigo.homes/tasks/{task_name}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/task-page.css">
  
  <script type="application/ld+json">
  {json.dumps(faq_schema, ensure_ascii=False)}
  </script>
</head>
<body>
  <nav class="navbar"><div class="nav-inner">
    <a href="/" class="logo">🔍 AI工具发现</a>
    <div class="nav-links">
      <a href="/index.html">发现</a>
      <a href="/top10/code.html">🏆 排行榜</a>
      <a href="/tweets.html">推文</a>
    </div>
  </div></nav>

  <article class="task-page">
    <header class="task-header">
      <h1>{title_zh}</h1>
      <p class="task-subtitle">基于{len(tools_list)}款{task_name}工具的综合评测与对比</p>
    </header>

    <div class="task-tools-grid">
      {chr(10).join(tool_cards)}
    </div>

    <section class="faq-section">
      <h2>❓ 常见问题</h2>
      {faq_html}
    </section>

    <section class="conclusion">
      <h2>🏆 总结</h2>
      <p>以上是我们精选的{len(tools_list)}款{task_name}AI工具。每款工具都有其独特的优势和适用场景。建议根据你的具体需求选择，大多数工具都提供免费试用。</p>
    </section>
  </article>

  <footer class="footer">
    <p>AI进化网站，你进化想法。</p>
  </footer>
</body>
</html>'''
    
    return html

def main():
    print('生成任务聚合页（学习TAAFT按任务搜索策略）...')
    db = load_database()
    tools = db.get('tools', [])
    
    task_map = get_tools_by_task(tools)
    
    # 按工具数量排序，取前20个任务
    top_tasks = sorted(task_map.items(), key=lambda x: -len(x[1]))[:20]
    
    tasks_dir = os.path.join(PROJECT_DIR, 'tasks')
    os.makedirs(tasks_dir, exist_ok=True)
    
    generated = []
    for task_name, task_tools in top_tasks:
        # 清理task_name作为文件名
        safe_name = re.sub(r'[^a-z0-9\u4e00-\u9fff]', '-', task_name).strip('-')
        if not safe_name:
            continue
        
        html = generate_task_page(task_name, task_tools)
        page_path = os.path.join(tasks_dir, f'{safe_name}.html')
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated.append({'task': task_name, 'tools': len(task_tools), 'file': f'tasks/{safe_name}.html'})
        print(f"  ✅ {task_name}: {len(task_tools)}个工具")
    
    print(f"\n共生成 {len(generated)} 个任务聚合页")
    
    # 保存任务索引
    with open(os.path.join(PROJECT_DIR, 'data', 'tasks-index.json'), 'w') as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import re
    main()
