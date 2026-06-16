#!/usr/bin/env python3
"""生成sitemap.xml"""

import json
import os
from datetime import datetime, timezone

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '..')

def generate_sitemap():
    db_path = os.path.join(PROJECT_DIR, 'data', 'tools-database.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    tools = db.get('tools', [])
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    urls = [
        'https://aigo.homes/',
        'https://aigo.homes/tweets.html',
        'https://aigo.homes/explore.html',
        'https://aigo.homes/nav.html',
        'https://aigo.homes/games.html',
        'https://aigo.homes/about.html',
        'https://aigo.homes/faq.html',
        'https://aigo.homes/privacy.html',
    ]
    
    # 添加工具页面
    for tool in tools:
        tool_id = tool.get('id', '').replace('/', '-').replace('\\', '-')
        if tool_id:
            urls.append(f'https://aigo.homes/tools/{tool_id}.html')
    
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in urls:
        sitemap += f'  <url>\n'
        sitemap += f'    <loc>{url}</loc>\n'
        sitemap += f'    <lastmod>{today}</lastmod>\n'
        sitemap += f'    <changefreq>daily</changefreq>\n'
        sitemap += f'    <priority>0.8</priority>\n'
        sitemap += f'  </url>\n'
    
    sitemap += '</urlset>'
    
    sitemap_path = os.path.join(PROJECT_DIR, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    print(f"✅ Sitemap已生成: {len(urls)} 个URL")

if __name__ == '__main__':
    generate_sitemap()
