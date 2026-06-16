#!/usr/bin/env python3
"""
generate-homepage.py — 全自动首页生成器（带i18n双语支持）
根据 tools-database.json 生成新首页，支持中英文切换
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
    
    # Featured tools (Top 10 by mentions)
    featured = sorted(tools, key=lambda x: x.get('mentions', 0), reverse=True)[:10]
    
    # New tools (added in last 7 days)
    new_tools = [t for t in tools if t.get('dateAdded', '') >= '2026-06-10'][:6]
    
    # Latest tweets (5)
    latest_tweets = tweets[:5]
    
    # Generate category pills with i18n
    category_pills = ''
    for c in categories[:8]:
        cat_id = c.get('id', '')
        cat_icon = c.get('icon', '')
        # Use data-i18n for category names - we'll handle via JS
        category_pills += f'<button class="cat-pill" onclick="filterCategory(\'{cat_id}\')" data-cat-id="{cat_id}">{cat_icon} <span class="cat-name" data-cat="{cat_id}">{c.get("name", cat_id)}</span></button>'
    
    # Add "All" button
    category_pills += '<button class="cat-pill all" onclick="filterCategory(\'all\')" data-i18n="hero.allCategories">全部</button>'
    
    # Generate featured cards with bilingual support
    featured_cards = ''.join([
        f'''
        <div class="tool-card" data-categories="{','.join(t.get('tags', []))}">
          <div class="tool-icon">{t.get('icon', '🔧')}</div>
          <div class="tool-info">
            <div class="tool-name">{t.get('name', 'Unknown')}</div>
            <div class="tool-desc" data-lang="zh">{t.get('descriptionZh', t.get('description', ''))[:60]}</div>
            <div class="tool-desc hidden" data-lang="en">{t.get('description', '')[:60]}</div>
            <div class="tool-tags">{''.join([f'<span class="tag">{tag}</span>' for tag in t.get('tags', [])[:3]])}</div>
          </div>
          <a href="tools/{t.get('id', '').replace('/', '-').replace('\\', '-')}.html" class="tool-link" onclick="trackToolClick('{t.get('id', '')}')">→</a>
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
    ]) if new_tools else '<p style="color:var(--text-muted); text-align:center;" data-i18n="newTools.empty">暂无新工具，每日自动更新</p>'
    
    # Generate tweet items with bilingual support
    tweet_items = ''.join([
        f'''
        <div class="tweet-item">
          <div class="tweet-title" data-lang="zh">{t.get('zh', {}).get('title', t.get('title', '无标题'))[:50]}</div>
          <div class="tweet-title hidden" data-lang="en">{t.get('en', {}).get('title', t.get('title', 'No Title'))[:50]}</div>
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
  <title data-i18n="siteName">AI工具发现</title>
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
      <a href="/" class="logo" data-i18n="siteName">AI工具发现</a>
      <div class="nav-links" id="nav-links">
        <a href="index.html" class="active" data-i18n="nav.home">发现</a>
        <a href="tweets.html" data-i18n="nav.tweets">推文</a>
        <a href="explore.html" data-i18n="nav.explore">进化</a>
        <a href="nav.html" data-i18n="nav.nav">导航</a>
        <a href="games.html" data-i18n="nav.games">游戏</a>
      </div>
      <button id="lang-switch" data-i18n="langSwitch">English</button>
      <button class="mobile-menu-btn" id="mobile-menu-btn" aria-label="菜单">☰</button>
    </div>
  </nav>

  <!-- Hero: 搜索 + 品牌 -->
  <header class="hero-section">
    <h1 data-i18n="hero.title">发现AI工具，见证AI进化</h1>
    <p class="hero-subtitle" data-i18n="hero.subtitle">已收录 {len(tools)} 个AI工具，每日自动更新</p>
    
    <div class="search-box">
      <input type="text" id="tool-search" data-i18n="hero.searchPlaceholder" placeholder="搜索 AI 工具... 例如：ChatGPT、Midjourney、Notion" autocomplete="off">
      <button onclick="searchTools()" data-i18n="hero.searchBtn">🔍</button>
    </div>
    
    <div class="category-pills">
      {category_pills}
    </div>
  </header>

  <!-- 热门工具排行榜 -->
  <section class="section" aria-label="热门工具">
    <div class="section-header">
      <h2 data-i18n="featured.title">🔥 本周热门工具 Top 10</h2>
      <span class="section-count" data-i18n="featured.subtitle">基于全网提及频率自动排名</span>
    </div>
    <div class="tools-grid" id="featured-tools">
      {featured_cards}
    </div>
  </section>

  <!-- 新品速递 -->
  <section class="section" aria-label="新品速递">
    <div class="section-header">
      <h2 data-i18n="newTools.title">🆕 新品速递</h2>
      <span class="section-count" data-i18n="newTools.subtitle">最近发现的新工具</span>
    </div>
    <div class="tools-grid mini" id="new-tools">
      {new_cards}
    </div>
  </section>

  <!-- AI进化日报（推文） -->
  <section class="section" aria-label="AI快讯">
    <div class="section-header">
      <h2 data-i18n="tweets.title">📰 AI进化日报</h2>
      <a href="tweets.html" class="view-all" data-i18n="tweets.viewAll">查看全部 →</a>
    </div>
    <div class="tweets-list">
      {tweet_items}
    </div>
  </section>

  <!-- 邮件订阅 -->
  <section class="subscribe-section" aria-label="订阅">
    <div class="subscribe-content">
      <h3 data-i18n="subscribe.title">📬 每周AI工具精选</h3>
      <p data-i18n="subscribe.desc">每周一发送，5个最佳工具 + 1个深度评测。不spam。</p>
      <form class="subscribe-form" id="subscribe-form">
        <input type="email" id="subscribe-email" data-i18n="subscribe.placeholder" placeholder="your@email.com" required>
        <button type="submit" data-i18n="subscribe.btn">订阅</button>
      </form>
      <p class="subscribe-hint"><span data-i18n="subscribe.count">已订阅 0 人</span></p>
    </div>
  </section>

  <!-- 实验场 -->
  <section class="section" aria-label="实验场">
    <div class="section-header">
      <h2 data-i18n="evolution.title">🧪 实验场：这个网站在自我进化</h2>
      <a href="explore.html" class="view-all" data-i18n="evolution.viewAll">查看全部 →</a>
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
    <p data-i18n="footer.slogan">AI进化网站，你进化想法。</p>
    <p data-i18n="footer.contact">联系邮箱：</p>
    <p>
      <a href="privacy.html">隐私政策</a> · <a href="about.html">关于我们</a> · <a href="faq.html">常见问题</a>
    </p>
    <p style="font-size:0.8rem; margin-top:1rem; color:var(--text-muted);" data-i18n="disclaimer">本网站仅供演示和参考，不构成医疗、法律或财务建议。</p>
  </footer>

  <script src="js/i18n-data.js"></script>
  <script src="js/i18n.js"></script>
  <script src="js/mobile-nav.js"></script>
  <script>
    // 初始化语言（从localStorage或浏览器语言）
    const currentLang = localStorage.getItem('lang') || (navigator.language.startsWith('zh') ? 'zh' : 'en');
    
    // 更新页面上的动态计数
    function updateDynamicText() {{
      const t = i18n[currentLang];
      
      // 更新hero副标题中的工具数量
      const heroSubtitle = document.querySelector('.hero-subtitle');
      if (heroSubtitle) {{
        const template = t.hero?.subtitle || "已收录 {{count}} 个AI工具，每日自动更新";
        heroSubtitle.textContent = template.replace('{{count}}', '{len(tools)}');
      }}
      
      // 更新订阅人数
      const subs = JSON.parse(localStorage.getItem('subscribers') || '[]');
      const countEl = document.querySelector('#subscriber-count');
      if (countEl) countEl.textContent = subs.length;
    }}
    
    // 语言切换时切换内容显示
    function toggleLangContent(lang) {{
      // 切换所有带data-lang的元素
      document.querySelectorAll('[data-lang]').forEach(el => {{
        if (el.getAttribute('data-lang') === lang) {{
          el.classList.remove('hidden');
        }} else {{
          el.classList.add('hidden');
        }}
      }});
      
      // 切换分类名称
      const catNames = {{
        zh: {{productivity: "生产力", design: "设计", code: "编程", video: "视频", audio: "音频", writing: "写作", image: "图像", business: "商业", education: "教育", research: "研究"}},
        en: {{productivity: "Productivity", design: "Design", code: "Code", video: "Video", audio: "Audio", writing: "Writing", image: "Image", business: "Business", education: "Education", research: "Research"}}
      }};
      
      document.querySelectorAll('.cat-name').forEach(el => {{
        const catId = el.getAttribute('data-cat');
        if (catId && catNames[lang] && catNames[lang][catId]) {{
          el.textContent = catNames[lang][catId];
        }}
      }});
    }}
    
    // 覆盖原有的applyI18n，添加动态内容切换
    const originalApplyI18n = applyI18n;
    applyI18n = function() {{
      originalApplyI18n();
      updateDynamicText();
      toggleLangContent(currentLang);
    }};
    
    // 覆盖原有的setLang
    const originalSetLang = window.setLang || function(){{}};
    window.setLang = function(lang) {{
      localStorage.setItem('lang', lang);
      location.reload();
    }};
    
    // 初始化
    document.addEventListener('DOMContentLoaded', () => {{
      applyI18n();
    }});
    
    // 工具搜索
    function searchTools() {{
      const q = document.getElementById('tool-search').value.toLowerCase();
      const cards = document.querySelectorAll('.tool-card');
      cards.forEach(card => {{
        const name = card.querySelector('.tool-name')?.textContent?.toLowerCase() || '';
        const desc = card.querySelector('.tool-desc:not(.hidden)')?.textContent?.toLowerCase() || '';
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
      const t = i18n[currentLang]?.subscribe;
      
      let subs = JSON.parse(localStorage.getItem('subscribers') || '[]');
      if (!subs.includes(email)) {{
        subs.push(email);
        localStorage.setItem('subscribers', JSON.stringify(subs));
        document.getElementById('subscriber-count').textContent = subs.length;
        alert(t?.success || '✅ 订阅成功！');
        document.getElementById('subscribe-email').value = '';
      }} else {{
        alert(t?.exists || '⚠️ 已订阅');
      }}
    }});
  </script>
</body>
</html>'''
    
    # 保存首页
    index_path = os.path.join(PROJECT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 首页已生成: {len(tools)} 个工具, {len(latest_tweets)} 条推文")
    print(f"   Featured: {len(featured)} 个, New: {len(new_tools)} 个")
    return True

if __name__ == '__main__':
    generate_homepage()