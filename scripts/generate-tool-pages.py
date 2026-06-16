#!/usr/bin/env python3
"""
生成AI工具独立页面（GEO优化版本）
为每个工具生成一个独立的SEO页面，带FAQ Schema和对比表格
"""

import json
import os
from datetime import datetime, timezone

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

def load_database():
    db_path = os.path.join(PROJECT_DIR, 'data', 'tools-database.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_tool_page(tool):
    """为单个工具生成GEO优化的HTML页面"""
    
    tool_id = tool.get('id', '')
    name = tool.get('name', '')
    name_zh = tool.get('nameZh', name)
    desc = tool.get('description', '')
    desc_zh = tool.get('descriptionZh', desc)
    icon = tool.get('icon', '🔧')
    url = tool.get('url', '#')
    category = tool.get('category', '')
    tags = tool.get('tags', [])
    pricing = tool.get('pricing', 'freemium')
    pricing_zh = tool.get('pricingZh', '免费增值')
    
    # GEO优化：FAQ结构化数据（AI最喜欢引用的格式）
    faqs = [
        {"q": f"{name_zh}是什么？", "q_en": f"What is {name}?", 
         "a": f"{name_zh}是一款{desc_zh[:100]}。", "a_en": f"{name} is a tool that {desc[:100]}."},
        {"q": f"{name_zh}免费吗？", "q_en": f"Is {name} free?",
         "a": f"{name_zh}采用{pricing_zh}模式。", "a_en": f"{name} uses a {pricing} pricing model."},
        {"q": f"{name_zh}和竞品哪个好？", "q_en": f"How does {name} compare to alternatives?",
         "a": f"{name_zh}在{', '.join(tags[:3])}方面表现出色。具体选择取决于你的需求。", 
         "a_en": f"{name} excels in {', '.join(tags[:3])}. The best choice depends on your specific needs."},
        {"q": f"{name_zh}适合谁用？", "q_en": f"Who should use {name}?",
         "a": f"适合需要{', '.join(tags[:3])}的用户。", "a_en": f"Best for users who need {', '.join(tags[:3])}."},
    ]
    
    # 生成FAQ Schema JSON-LD
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
            } for f in faqs
        ]
    }
    
    # 生成Product Schema
    product_schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "description": desc,
        "applicationCategory": category,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }
    
    # FAQ HTML
    faq_html = '\n'.join([
        f'''<div class="faq-item">
          <h3 class="faq-q" data-lang="zh">{f["q"]}</h3>
          <h3 class="faq-q hidden" data-lang="en">{f["q_en"]}</h3>
          <p class="faq-a" data-lang="zh">{f["a"]}</p>
          <p class="faq-a hidden" data-lang="en">{f["a_en"]}</p>
        </div>'''
        for f in faqs
    ])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name_zh} 评测：功能、价格、优缺点（2026） | AI工具发现</title>
  <meta name="description" content="{name_zh}完整评测。{desc_zh[:120]}。价格、核心功能、优缺点、同类工具对比。">
  <meta name="keywords" content="{name_zh},{name},AI工具评测,{category},AI工具推荐">
  <link rel="canonical" href="https://aigo.homes/tools/{tool_id}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/tool-page.css">
  
  <!-- FAQ Schema -->
  <script type="application/ld+json">
  {json.dumps(faq_schema, ensure_ascii=False)}
  </script>
  
  <!-- Product Schema -->
  <script type="application/ld+json">
  {json.dumps(product_schema, ensure_ascii=False)}
  </script>
</head>
<body>
  <nav class="navbar"><div class="nav-inner">
    <a href="/" class="logo">🔍 AI工具发现</a>
    <div class="nav-links">
      <a href="/index.html">发现</a>
      <a href="/tweets.html">推文</a>
    </div>
  </div></nav>

  <article class="tool-detail">
    <!-- GEO优化：答案优先 - 前40-60字直接回答核心问题 -->
    <header class="tool-header">
      <div class="tool-icon-large">{icon}</div>
      <h1>{name_zh}</h1>
      <p class="tool-one-liner" data-lang="zh">{name_zh}是一款{desc_zh[:80]}。{pricing_zh}使用。</p>
      <p class="tool-one-liner hidden" data-lang="en">{name} is a tool that {desc[:80]}. {pricing} model.</p>
      <div class="tool-meta">
        <span class="tag">{category}</span>
        <span class="tag">{pricing_zh}</span>
        {' '.join([f'<span class="tag">{t}</span>' for t in tags[:5]])}
      </div>
      <a href="{url}" class="cta-btn" target="_blank" rel="noopener">访问官网 →</a>
    </header>

    <!-- 快速摘要（AI最喜欢引用的部分） -->
    <section class="quick-summary" aria-label="快速摘要">
      <h2>快速摘要</h2>
      <ul class="summary-list">
        <li data-lang="zh"><strong>是什么：</strong>{desc_zh[:100]}</li>
        <li class="hidden" data-lang="en"><strong>What:</strong> {desc[:100]}</li>
        <li data-lang="zh"><strong>价格：</strong>{pricing_zh}</li>
        <li class="hidden" data-lang="en"><strong>Pricing:</strong> {pricing}</li>
        <li data-lang="zh"><strong>核心功能：</strong>{', '.join(tags[:5])}</li>
        <li class="hidden" data-lang="en"><strong>Key features:</strong> {', '.join(tags[:5])}</li>
      </ul>
    </section>

    <!-- 详细评测 -->
    <section class="tool-review" aria-label="评测">
      <h2 data-lang="zh">详细评测</h2>
      <h2 class="hidden" data-lang="en">Detailed Review</h2>
      
      <div class="review-section">
        <h3 data-lang="zh">功能特点</h3>
        <h3 class="hidden" data-lang="en">Features</h3>
        <p data-lang="zh">{name_zh}主要提供以下功能：{', '.join(tags)}。</p>
        <p class="hidden" data-lang="en">{name} offers: {', '.join(tags)}.</p>
      </div>
      
      <div class="review-section">
        <h3 data-lang="zh">价格方案</h3>
        <h3 class="hidden" data-lang="en">Pricing</h3>
        <p data-lang="zh">{name_zh}采用{pricing_zh}模式。</p>
        <p class="hidden" data-lang="en">{name} uses a {pricing} model.</p>
      </div>
    </section>

    <!-- FAQ区块（GEO优化核心） -->
    <section class="faq-section" aria-label="常见问题">
      <h2 data-lang="zh">常见问题</h2>
      <h2 class="hidden" data-lang="en">FAQ</h2>
      {faq_html}
    </section>

    <!-- 相关工具推荐 -->
    <section class="related-tools" aria-label="相关工具">
      <h2 data-lang="zh">你可能还喜欢</h2>
      <h2 class="hidden" data-lang="en">You May Also Like</h2>
      <p data-lang="zh">查看更多<a href="/index.html">AI工具</a>。</p>
      <p class="hidden" data-lang="en">Browse more <a href="/index.html">AI tools</a>.</p>
    </section>
  </article>

  <footer class="footer">
    <p>AI进化网站，你进化想法。</p>
  </footer>

  <script src="../js/i18n-data.js"></script>
  <script src="../js/i18n.js"></script>
  <script>
    // 初始化语言
    const currentLang = localStorage.getItem('lang') || 'zh';
    document.querySelectorAll('[data-lang]').forEach(el => {{
      if (el.getAttribute('data-lang') === currentLang) {{
        el.classList.remove('hidden');
      }} else {{
        el.classList.add('hidden');
      }}
    }});
  </script>
</body>
</html>'''
    
    return html

def generate_all_tool_pages():
    """为所有工具生成独立页面"""
    db = load_database()
    tools = db.get('tools', [])
    
    # 创建tools目录
    tools_dir = os.path.join(PROJECT_DIR, 'tools')
    os.makedirs(tools_dir, exist_ok=True)
    
    generated = 0
    for tool in tools:
        tool_id = tool.get('id', '')
        if not tool_id:
            continue
        
        # 清理特殊字符，避免路径问题
        tool_id = tool_id.replace('/', '-').replace('\\', '-')
        tool['id'] = tool_id
        
        html = generate_tool_page(tool)
        page_path = os.path.join(tools_dir, f'{tool_id}.html')
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(html)
        generated += 1
        
        if generated <= 3:
            print(f"  + 生成页面: tools/{tool_id}.html ({tool.get('name', '')})")
    
    print(f"\n✅ 已生成 {generated} 个工具详情页")
    return generated

if __name__ == '__main__':
    generate_all_tool_pages()
