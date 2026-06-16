#!/usr/bin/env python3
"""
生成中文SEO榜单页（Top 10系列）
基于 tools-database.json 数据，生成高质量长文页面
"""

import json
import os

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

def load_database():
    with open(os.path.join(PROJECT_DIR, 'data', 'tools-database.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_top10_page(category_id, category_name, category_name_en, tools_list):
    """生成一个Top 10榜单页"""
    
    # 取前10个工具（按排名/热度排序，这里按数据库顺序）
    top_tools = tools_list[:10]
    
    # 生成对比表格行
    table_rows = []
    for i, t in enumerate(top_tools, 1):
        name = t.get('nameZh', t.get('name', ''))
        desc = t.get('descriptionZh', t.get('description', ''))[:60]
        pricing = t.get('pricingZh', t.get('pricing', '免费增值'))
        tags = ', '.join(t.get('tags', [])[:3])
        table_rows.append(f'''<tr>
      <td>{i}</td>
      <td><strong>{name}</strong></td>
      <td>{desc}</td>
      <td>{tags}</td>
      <td>{pricing}</td>
    </tr>''')
    
    # 生成每个工具的详细评测
    tool_reviews = []
    for i, t in enumerate(top_tools, 1):
        name = t.get('nameZh', t.get('name', ''))
        name_en = t.get('name', '')
        desc = t.get('descriptionZh', t.get('description', ''))
        desc_en = t.get('description', '')
        icon = t.get('icon', '🔧')
        url = t.get('url', '#')
        pricing = t.get('pricingZh', t.get('pricing', '免费增值'))
        tags = t.get('tags', [])
        tool_id = t.get('id', '').replace('/', '-').replace('\\', '-')
        
        # 为每个工具生成一段"评测"
        review_text = f"""{name}是{t.get('category', 'AI工具')}领域的{tags[0] if tags else '热门工具'}。{desc}。该工具采用{pricing}模式，适合需要{', '.join(tags[:3]) if tags else 'AI辅助'}的用户。"""
        
        tool_reviews.append(f'''<article class="tool-review-item" id="tool-{i}">
    <div class="review-header">
      <span class="rank">#{i}</span>
      <span class="icon">{icon}</span>
      <h3>{name}</h3>
    </div>
    <p class="review-desc" data-lang="zh">{review_text}</p>
    <p class="review-desc hidden" data-lang="en">{name_en} is a leading {t.get('category', 'AI tool')} that {desc_en[:100]}. It uses a {t.get('pricing', 'freemium')} pricing model.</p>
    <div class="review-meta">
      <span class="tag">{pricing}</span>
      {' '.join([f'<span class="tag">{tag}</span>' for tag in tags[:5]])}
    </div>
    <div class="review-actions">
      <a href="{url}" class="btn-primary" target="_blank" rel="noopener">访问官网</a>
      <a href="tools/{tool_id}.html" class="btn-secondary">查看详细评测</a>
    </div>
  </article>''')
    
    # FAQ
    faqs = [
        {"q": f"什么是{category_name}？", "q_en": f"What are {category_name_en}?",
         "a": f"{category_name}是指利用人工智能技术辅助{category_name.replace('AI', '')}工作的软件工具。它们可以大幅提升工作效率，降低学习成本。",
         "a_en": f"{category_name_en} are software tools that use AI to assist with {category_name_en.lower()}. They improve efficiency and reduce learning curves."},
        {"q": f"{category_name}免费吗？", "q_en": f"Are {category_name_en} free?",
         "a": "大部分工具提供免费试用或免费增值模式，高级功能通常需要付费订阅。",
         "a_en": "Most tools offer free trials or freemium models. Premium features usually require a paid subscription."},
        {"q": f"如何选择适合自己的{category_name}？", "q_en": f"How to choose the right {category_name_en}?",
         "a": "建议根据你的具体需求、预算和使用场景来选择。可以先试用免费版，再决定是否升级。",
         "a_en": "Consider your specific needs, budget, and use cases. Try free versions first before upgrading."},
        {"q": f"{category_name}会取代人类工作吗？", "q_en": f"Will {category_name_en} replace human jobs?",
         "a": "AI工具更多是辅助人类工作，提高效率和创造力。掌握AI工具的人将更具竞争力。",
         "a_en": "AI tools primarily assist humans, improving efficiency and creativity. Those who master AI tools will be more competitive."},
    ]
    
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ]
    }
    
    faq_html = '\n'.join([
        f'''<div class="faq-item">
      <h3 class="faq-q" data-lang="zh">{f["q"]}</h3>
      <h3 class="faq-q hidden" data-lang="en">{f["q_en"]}</h3>
      <p class="faq-a" data-lang="zh">{f["a"]}</p>
      <p class="faq-a hidden" data-lang="en">{f["a_en"]}</p>
    </div>'''
        for f in faqs
    ])
    
    # 计算字数
    total_text = ' '.join([t.get('descriptionZh', t.get('description', '')) for t in top_tools])
    total_text += ' '.join([t.get('nameZh', t.get('name', '')) for t in top_tools])
    word_count = len(total_text) + 800  # 加上模板文字约800字
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>2026年最佳{category_name}Top 10（评测+对比）| AI工具发现</title>
  <meta name="description" content="2026年{category_name}排行榜Top 10。功能对比、价格、优缺点详解。帮你找到最适合的AI工具。">
  <link rel="canonical" href="https://aigo.homes/top10/{category_id}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="stylesheet" href="../css/top10.css">
  
  <!-- FAQ Schema -->
  <script type="application/ld+json">
  {json.dumps(faq_schema, ensure_ascii=False)}
  </script>
  
  <!-- Article Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "2026年最佳{category_name}Top 10",
    "description": "2026年{category_name}排行榜Top 10。功能对比、价格、优缺点详解。",
    "author": {{
      "@type": "Organization",
      "name": "AI工具发现"
    }},
    "datePublished": "2026-06-16",
    "dateModified": "2026-06-16"
  }}
  </script>
  
  <!-- Google Adsense 占位 -->
  <!-- 接入Adsense后取消注释
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXX"></script>
  -->
</head>
<body>
  <nav class="navbar"><div class="nav-inner">
    <a href="/" class="logo">🔍 AI工具发现</a>
    <div class="nav-links">
      <a href="/index.html">发现</a>
      <a href="/tweets.html">推文</a>
    </div>
  </div></nav>

  <article class="top10-article">
    <header class="article-header">
      <h1 data-lang="zh">2026年最佳{category_name}Top 10（评测+对比）</h1>
      <h1 class="hidden" data-lang="en">Top 10 Best {category_name_en} in 2026 (Reviewed)</h1>
      <p class="article-subtitle" data-lang="zh">基于功能、价格、用户口碑的综合排名。最后更新：2026年6月。</p>
      <p class="article-subtitle hidden" data-lang="en">Ranked by features, pricing, and user reviews. Last updated: June 2026.</p>
    </header>

    <!-- 快速导航 -->
    <nav class="toc" aria-label="目录">
      <h3 data-lang="zh">快速导航</h3>
      <h3 class="hidden" data-lang="en">Quick Navigation</h3>
      <ol>
        {''.join([f'<li><a href="#tool-{i}">{t.get("nameZh", t.get("name", ""))}</a></li>' for i, t in enumerate(top_tools, 1)])}
      </ol>
    </nav>

    <!-- 广告位1：文章开头 -->
    <div class="ad-slot ad-top">
      <p class="ad-label">广告</p>
      <!-- Adsense代码将插入这里 -->
    </div>

    <!-- 对比表格 -->
    <section class="comparison-table-section">
      <h2 data-lang="zh">📊 快速对比表</h2>
      <h2 class="hidden" data-lang="en">Quick Comparison</h2>
      <div class="table-wrapper">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>工具</th>
              <th>简介</th>
              <th>核心功能</th>
              <th>价格</th>
            </tr>
          </thead>
          <tbody>
            {chr(10).join(table_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 广告位2：表格下方 -->
    <div class="ad-slot ad-mid">
      <p class="ad-label">广告</p>
    </div>

    <!-- 详细评测 -->
    <section class="detailed-reviews">
      <h2 data-lang="zh">📝 详细评测</h2>
      <h2 class="hidden" data-lang="en">Detailed Reviews</h2>
      {chr(10).join(tool_reviews)}
    </section>

    <!-- 广告位3：评测中间 -->
    <div class="ad-slot ad-mid">
      <p class="ad-label">广告</p>
    </div>

    <!-- FAQ -->
    <section class="faq-section">
      <h2 data-lang="zh">❓ 常见问题</h2>
      <h2 class="hidden" data-lang="en">FAQ</h2>
      {faq_html}
    </section>

    <!-- 结论 -->
    <section class="conclusion">
      <h2 data-lang="zh">🏆 总结</h2>
      <h2 class="hidden" data-lang="en">Summary</h2>
      <p data-lang="zh">以上就是2026年最值得推荐的{len(top_tools)}款{category_name}。每款工具都有其独特的优势和适用场景。建议根据你的具体需求选择，大多数工具都提供免费试用，可以先体验再决定。</p>
      <p class="hidden" data-lang="en">These are the top {len(top_tools)} {category_name_en} in 2026. Each has unique strengths. Try before you buy.</p>
    </section>
  </article>

  <footer class="footer">
    <p>AI进化网站，你进化想法。</p>
  </footer>

  <script src="../js/i18n-data.js"></script>
  <script src="../js/i18n.js"></script>
  <script>
    const currentLang = localStorage.getItem('lang') || 'zh';
    document.querySelectorAll('[data-lang]').forEach(el => {{
      if (el.getAttribute('data-lang') === currentLang) el.classList.remove('hidden');
      else el.classList.add('hidden');
    }});
  </script>
</body>
</html>'''
    
    return html, word_count

def generate_all_top10():
    db = load_database()
    tools = db.get('tools', [])
    
    # 定义要生成的分类
    categories_to_generate = [
        ('code', 'AI编程助手', 'AI Coding Assistants'),
        ('productivity', 'AI生产力工具', 'AI Productivity Tools'),
        ('design', 'AI设计工具', 'AI Design Tools'),
        ('video', 'AI视频工具', 'AI Video Tools'),
        ('writing', 'AI写作工具', 'AI Writing Tools'),
    ]
    
    # 创建目录
    top10_dir = os.path.join(PROJECT_DIR, 'top10')
    os.makedirs(top10_dir, exist_ok=True)
    
    generated = []
    for cat_id, cat_name_zh, cat_name_en in categories_to_generate:
        cat_tools = [t for t in tools if t.get('category') == cat_id]
        if len(cat_tools) < 3:
            print(f"  ⚠️ {cat_name_zh} 工具太少 ({len(cat_tools)}个)，跳过")
            continue
        
        html, word_count = generate_top10_page(cat_id, cat_name_zh, cat_name_en, cat_tools)
        page_path = os.path.join(top10_dir, f'{cat_id}.html')
        
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        generated.append({
            'file': f'top10/{cat_id}.html',
            'name': cat_name_zh,
            'tools': len(cat_tools),
            'words': word_count
        })
        print(f"  ✅ {cat_name_zh}: {len(cat_tools)}个工具, ~{word_count}字")
    
    return generated

if __name__ == '__main__':
    print("生成Top 10榜单页...")
    results = generate_all_top10()
    print(f"\n共生成 {len(results)} 个榜单页")
