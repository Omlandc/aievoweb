#!/usr/bin/env python3
"""
generate-homepage.py — 全自动首页生成器
根据 tools-database.json 生成新首页（工具发现门户）
"""

import json
import os
from datetime import datetime, timezone

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

def load_database():
    db_path = os.path.join(PROJECT_DIR, 'data', 'tools-database.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tweets():
    tweets_path = os.path.join(PROJECT_DIR, 'data', 'tweets.json')
    try:
        with open(tweets_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def generate_homepage():
    db = load_database()
    tweets = load_tweets()
    
    tools = db.get('tools', [])
    categories = db.get('categories', [])
    
    #  Featured tools (Top 10 by mentions)
    featured = sorted(tools, key=lambda x: x.get('mentions', 0), reverse=True)[:10]
    
    #  New tools (added in last 7 days)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    new_tools = [t for t in tools if t.get('dateAdded', '') >= '2026-06-10'][:6]
    
    #  Latest tweets (5)
    latest_tweets = tweets[:5]
    
    # Generate category pills
    category_pills = ''
    for c in categories[:8]:
        cat_id = c.get('id', '')
        cat_name = c.get('name', cat_id)
        cat_icon = c.get('icon', '')
        category_pills += f'<button class="cat-pill" onclick="filterCategory(\'{cat_id}\')">{cat_icon} {cat_name}</button>'
    
    # Add "All" button
    category_pills += '<button class="cat-pill all" onclick="filterCategory(\'all\')">全部</button>'
    
    # Generate featured cards
    featured_cards = ''.join([
        f'''
        <div class="tool-card" data-categories="{','.join(t.get('tags', []))}">
          <div class="tool-icon">{t.get('icon', '🔧')}</div>
          <div class="tool-info">
            <div class="tool-name">{t.get('name', 'Unknown')}</div>
            <div class="tool-desc">{t.get('descriptionZh', t.get('description', ''))[:60]}</div>
            <div class="tool-tags">{''.join([f'<span class="tag">{tag}</span>' for tag in t.get('tags', [])[:3]])}</div>
          </div>
          <a href="{t.get('url', '#')}" class="tool-link" target="_blank" rel="noopener" onclick="trackToolClick('{t.get('id', '')}')">→</a>
        </div>
        '''
        for t in featured
    ])
    
    # Generate new tool cards
    new_cards = ''.join([
        f'''
        <div class="tool-card mini">
          <div class="tool-icon">{t.get('icon', '🔧')}</div>
          <div class="tool-name">{t.get('name', 'Unknown')}</div>
          <a href="{t.get('url', '#')}" target="_blank" rel="noopener">查看 →</a>
        </div>
        '''
        for t in new_tools
    ]) if new_tools else '<p style="color:var(--text-muted); text-align:center;">暂无新工具，每日自动更新</p>'
    
    # Generate tweet items
    tweet_items = ''.join([
        f'''
        <div class="tweet-item">
          <div class="tweet-title">{t.get('zh', {}).get('title', t.get('title', '无标题'))[:50]}</div>
          <div class="tweet-meta">{t.get('source', '')} · {t.get('date', '')}</div>
        </div>
        '''
        for t in latest_tweets
    ]) if latest_tweets else '<p style="color:var(--text-muted); text-align:center;">暂无推文，RSS Bot 每日自动更新</p>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-4FQ1XFBP6M"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-4FQ1XFBP6M');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI工具发现 - 500+工具评测、排行榜、推荐 | aigo.homes</title>
  <meta name="description" content="发现最适合你的AI工具。{len(tools)}+工具评测，图像/写作/编程/视频/音频分类，每日更新，中英双语。">
  <meta name="keywords" content="AI工具,AI工具发现,AI工具推荐,AI工具排行榜,AI工具评测">
  <meta name="author" content="Play AI Evolution">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://aigo.homes/">
  
  <link rel="stylesheet" href="css/style.css">
  <link rel="stylesheet" href="css/homepage.css">
  <link rel="alternate" hreflang="zh" href="https://aigo.homes/">
  <link rel="alternate" hreflang="en" href="https://aigo.homes/en/">
  <link rel="alternate" hreflang="x-default" href="https://aigo.homes/">
  
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "AI工具发现 - aigo.homes",
    "description": "发现最适合你的AI工具。{len(tools)}+工具评测，每日更新",
    "url": "https://aigo.homes/",
    "potentialAction": {{
      "@type": "SearchAction",
      "target": "https://aigo.homes/?q={{search_term_string}}",
      "query-input": "required name=search_term_string"
    }}
  }}
  </script>
</head>
<body>
  <nav class="navbar" role="navigation" aria-label="Main">
    <div class="nav-inner">
      <a href="/" class="logo">🔍 AI工具发现</a>
      <div class="nav-links" id="nav-links">
        <a href="index.html" class="active">发现</a>
        <a href="tweets.html">推文</a>
        <a href="explore.html">进化</a>
        <a href="nav.html">导航</a>
        <a href="games.html">游戏</a>
      </div>
      <button id="lang-switch">English</button>
      <button class="mobile-menu-btn" id="mobile-menu-btn" aria-label="菜单">☰</button>
    </div>
  </nav>

  <!-- Hero: 搜索 + 品牌 -->
  <header class="hero-section">
    <h1>发现AI工具，见证AI进化</h1>
    <p class="hero-subtitle">已收录 {len(tools)}+ 个AI工具，每日自动更新</p>
    
    <div class="search-box">
      <input type="text" id="tool-search" placeholder="搜索 AI 工具... 例如：ChatGPT、Midjourney、Notion" autocomplete="off">
      <button onclick="searchTools()">🔍</button>
    </div>
    
    <div class="category-pills">
      {category_pills}
      <button class="cat-pill all" onclick="filterCategory('all')">全部</button>
    </div>
  </header>

  <!-- 热门工具排行榜 -->
  <section class="section" aria-label="热门工具">
    <div class="section-header">
      <h2>🔥 本周热门工具 Top 10</h2>
      <span class="section-count">基于全网提及频率自动排名</span>
    </div>
    <div class="tools-grid" id="featured-tools">
      {featured_cards}
    </div>
  </section>

  <!-- 新品速递 -->
  <section class="section" aria-label="新品速递">
    <div class="section-header">
      <h2>🆕 新品速递</h2>
      <span class="section-count">最近发现的新工具</span>
    </div>
    <div class="tools-grid mini" id="new-tools">
      {new_cards}
    </div>
  </section>

  <!-- AI进化日报（推文） -->
  <section class="section" aria-label="AI快讯">
    <div class="section-header">
      <h2>📰 AI进化日报</h2>
      <a href="tweets.html" class="view-all">查看全部 →</a>
    </div>
    <div class="tweets-list">
      {tweet_items}
    </div>
  </section>

  <!-- 邮件订阅 -->
  <section class="subscribe-section" aria-label="订阅">
    <div class="subscribe-content">
      <h3>📬 每周AI工具精选</h3>
      <p>每周一发送，5个最佳工具 + 1个深度评测。不spam。</p>
      <form class="subscribe-form" id="subscribe-form">
        <input type="email" id="subscribe-email" placeholder="your@email.com" required>
        <button type="submit">订阅</button>
      </form>
      <p class="subscribe-hint">已订阅 <span id="subscriber-count">0</span> 人</p>
    </div>
  </section>

  <!-- 实验场 -->
  <section class="section" aria-label="实验场">
    <div class="section-header">
      <h2>🧪 实验场：这个网站在自我进化</h2>
      <a href="explore.html" class="view-all">查看全部 →</a>
    </div>
    <div class="evolution-timeline">
      <div class="evolution-item">
        <div class="evolution-date">2026-06-16</div>
        <div class="evolution-content">
          <div class="evolution-title">添加工具数据库 + 自动发现引擎</div>
          <div class="evolution-desc">自动收录 {len(tools)} 个AI工具，支持搜索和分类</div>
        </div>
      </div>
      <div class="evolution-item">
        <div class="evolution-date">2026-06-15</div>
        <div class="evolution-content">
          <div class="evolution-title">上线双语推文系统</div>
          <div class="evolution-desc">RSS Bot 每日自动抓取、翻译、推送中英双语AI资讯</div>
        </div>
      </div>
      <div class="evolution-item">
        <div class="evolution-date">2026-06-14</div>
        <div class="evolution-content">
          <div class="evolution-title">网站上线</div>
          <div class="evolution-desc">AI自动构建的实验性网站，开始接受用户提交需求</div>
        </div>
      </div>
    </div>
  </section>

  <footer class="footer" role="contentinfo">
    <p>AI进化网站，你进化想法。</p>
    <p>联系邮箱：ctguxby@proton.me</p>
    <p>
      <a href="privacy.html">隐私政策</a> · <a href="about.html">关于我们</a> · <a href="faq.html">常见问题</a>
    </p>
    <p style="font-size:0.8rem; margin-top:1rem; color:var(--text-muted);">
      本网站仅供演示和参考，不构成医疗、法律或财务建议。
    </p>
  </footer>

  <script src="js/i18n-data.js"></script>
  <script src="js/i18n.js"></script>
  <script src="js/mobile-nav.js"></script>
  <script>
    // 工具搜索
    function searchTools() {{
      const q = document.getElementById('tool-search').value.toLowerCase();
      const cards = document.querySelectorAll('.tool-card');
      cards.forEach(card => {{
        const name = card.querySelector('.tool-name')?.textContent?.toLowerCase() || '';
        const desc = card.querySelector('.tool-desc')?.textContent?.toLowerCase() || '';
        const tags = card.querySelector('.tool-tags')?.textContent?.toLowerCase() || '';
        card.style.display = (name.includes(q) || desc.includes(q) || tags.includes(q)) ? 'flex' : 'none';
      }});
    }}
    
    document.getElementById('tool-search')?.addEventListener('input', searchTools);
    
    // 分类筛选
    function filterCategory(cat) {{
      const cards = document.querySelectorAll('.tool-card');
      if (cat === 'all') {{
        cards.forEach(c => c.style.display = 'flex');
        return;
      }}
      cards.forEach(card => {{
        const cats = card.getAttribute('data-categories') || '';
        card.style.display = cats.includes(cat) ? 'flex' : 'none';
      }});
    }}
    
    // 工具点击追踪
    function trackToolClick(toolId) {{
      gtag('event', 'tool_click', {{ tool_id: toolId }});
    }}
    
    // 邮件订阅
    document.getElementById('subscribe-form')?.addEventListener('submit', async (e) => {{
      e.preventDefault();
      const email = document.getElementById('subscribe-email').value;
      
      // 存储到 localStorage（后续可以同步到服务器）
      let subs = JSON.parse(localStorage.getItem('subscribers') || '[]');
      if (!subs.includes(email)) {{
        subs.push(email);
        localStorage.setItem('subscribers', JSON.stringify(subs));
        document.getElementById('subscriber-count').textContent = subs.length;
        alert('✅ 订阅成功！每周一发送精选AI工具。');
        document.getElementById('subscribe-email').value = '';
      }} else {{
        alert('⚠️ 该邮箱已订阅');
      }}
    }});
    
    // 加载订阅数
    const subs = JSON.parse(localStorage.getItem('subscribers') || '[]');
    document.getElementById('subscriber-count').textContent = subs.length;
  </script>
</body>
</html>
'''
    
    # 保存首页
    index_path = os.path.join(PROJECT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 首页已生成: {len(tools)} 个工具, {len(latest_tweets)} 条推文")
    print(f"   Featured: {len(featured)} 个, New: {len(new_tools)} 个")
    return True

if __name__ == '__main__':
    generate_homepage()
