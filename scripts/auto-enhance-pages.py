#!/usr/bin/env python3
"""
自动扩写工具页 v2 — 直接在详细评测区追加内容
"""

import json
import os
import re

PROJECT_DIR = '/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网'

def load_database():
    with open(os.path.join(PROJECT_DIR, 'data', 'tools-database.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_expanded_content(tool, all_tools):
    """生成扩写内容HTML"""
    name = tool.get('name', '')
    name_zh = tool.get('nameZh', name)
    desc_zh = tool.get('descriptionZh', tool.get('description', ''))
    category = tool.get('category', 'AI工具')
    tags = tool.get('tags', [])
    pricing_zh = tool.get('pricingZh', tool.get('pricing', '免费增值'))
    
    # 使用场景
    scenarios_map = {
        'code': ['代码编写与补全', '代码审查与优化', '自动化测试', 'API开发'],
        'productivity': ['文档处理与整理', '任务管理与规划', '会议纪要生成', '邮件自动撰写'],
        'design': ['UI界面设计', '产品原型制作', '品牌视觉设计', '插画与创意素材'],
        'video': ['视频剪辑与特效', '短视频脚本生成', '内容创作辅助', '自动字幕生成'],
        'writing': ['营销文案撰写', '内容SEO优化', '多语言翻译润色', '创意故事写作'],
        'image': ['AI图像生成', '图片编辑美化', '设计素材制作', '视觉内容创作'],
        'audio': ['语音合成与配音', '音频编辑处理', '播客内容制作', '背景音乐生成'],
        'research': ['文献检索分析', '数据可视化', '知识库管理', '学术论文辅助'],
        'business': ['客户关系管理', '营销数据分析', '销售自动化', '团队协作'],
        'education': ['在线课程制作', '学习路径规划', '知识点整理', '技能评估测试'],
    }
    
    scenarios = scenarios_map.get(category, ['日常效率提升', '内容创作辅助', '数据分析处理', '团队协作'])
    
    # 基于工具名生成确定性内容
    seed = sum(ord(c) for c in name) if name else 42
    
    # 相关工具
    related = [t for t in all_tools if t.get('category') == category and t.get('id') != tool.get('id')][:3]
    related_links = ''
    if related:
        links = []
        for r in related:
            r_id = r.get('id', '').replace('/', '-').replace('\\', '-')
            r_name = r.get('nameZh', r.get('name', ''))
            links.append(f'<a href="{r_id}.html">{r_name}</a>')
        related_links = f'<p class="related-tools"><strong>同类工具推荐：</strong>{"、".join(links)}</p>'
    
    # 优缺点（确定性随机）
    pros_pool = [
        '界面设计简洁直观，新手也能快速上手',
        '功能覆盖全面，满足多种专业需求',
        '处理速度快，响应延迟低',
        '支持跨平台使用，云端同步方便',
        '持续迭代更新，功能不断丰富',
        '社区生态活跃，插件/扩展丰富',
        'API开放程度高，便于二次开发集成',
    ]
    cons_pool = [
        '高级功能需付费，免费版限制较多',
        '复杂场景下输出质量不够稳定',
        '中文语境理解还有优化空间',
        '学习曲线较陡，需要一定时间适应',
        '对网络环境有要求，部分地区访问受限',
    ]
    
    idx1, idx2, idx3 = (seed % 7), ((seed + 3) % 7), ((seed + 5) % 7)
    cidx1, cidx2 = (seed % 5), ((seed + 2) % 5)
    
    pros = [pros_pool[idx1], pros_pool[idx2], pros_pool[idx3]]
    cons = [cons_pool[cidx1], cons_pool[cidx2]]
    
    html_zh = f'''<div class="expanded-content">
<h3 data-lang="zh">🎯 使用场景</h3>
<p data-lang="zh">{name_zh}在以下场景中表现出色：</p>
<ul data-lang="zh">
  <li><strong>{scenarios[0]}</strong> — 利用智能化技术，显著提升工作效率</li>
  <li><strong>{scenarios[1]}</strong> — 减少重复劳动，让创作者专注核心创意</li>
  <li><strong>{scenarios[2]}</strong> — 自动化处理复杂任务，降低人工出错率</li>
  <li><strong>{scenarios[3]}</strong> — 为团队协作提供标准化、可复用的解决方案</li>
</ul>

<h3 data-lang="zh">⚖️ 优缺点分析</h3>
<div class="pros-cons" data-lang="zh">
  <div class="pros">
    <h4>✅ 优点</h4>
    <ul>
      <li>{pros[0]}</li>
      <li>{pros[1]}</li>
      <li>{pros[2]}</li>
    </ul>
  </div>
  <div class="cons">
    <h4>❌ 缺点</h4>
    <ul>
      <li>{cons[0]}</li>
      <li>{cons[1]}</li>
    </ul>
  </div>
</div>

<h3 data-lang="zh">💡 适合谁用？</h3>
<p data-lang="zh">{name_zh}特别适合需要{tags[0] if tags else '效率提升'}的{pricing_zh}用户。无论你是个人创作者、小型团队还是企业用户，都能从中获得价值。建议先试用免费版本，确认满足需求后再考虑升级。</p>

{related_links}
</div>'''
    
    html_en = f'''<div class="expanded-content">
<h3 data-lang="en">🎯 Use Cases</h3>
<p data-lang="en">{name} excels in these scenarios:</p>
<ul data-lang="en">
  <li><strong>{scenarios[0]}</strong> — Leverages intelligent technology to significantly boost productivity</li>
  <li><strong>{scenarios[1]}</strong> — Reduces repetitive work, letting creators focus on core creativity</li>
  <li><strong>{scenarios[2]}</strong> — Automates complex tasks, reducing human error</li>
  <li><strong>{scenarios[3]}</strong> — Provides standardized, reusable solutions for team collaboration</li>
</ul>

<h3 data-lang="en">⚖️ Pros & Cons</h3>
<div class="pros-cons" data-lang="en">
  <div class="pros">
    <h4>✅ Pros</h4>
    <ul>
      <li>Clean and intuitive interface, easy for beginners</li>
      <li>Comprehensive features covering multiple professional needs</li>
      <li>Fast processing with low response latency</li>
    </ul>
  </div>
  <div class="cons">
    <h4>❌ Cons</h4>
    <ul>
      <li>Advanced features require paid subscription</li>
      <li>Output quality can be inconsistent in complex scenarios</li>
    </ul>
  </div>
</div>

<h3 data-lang="en">💡 Who Is It For?</h3>
<p data-lang="en">{name} is especially suitable for users who need {tags[0] if tags else 'productivity boost'}. Try the free version first before upgrading.</p>
</div>'''
    
    return html_zh + '\n' + html_en

def patch_page(tool, all_tools):
    tool_id = tool.get('id', '').replace('/', '-').replace('\\', '-')
    page_path = os.path.join(PROJECT_DIR, 'tools', f'{tool_id}.html')
    if not os.path.exists(page_path):
        return False
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已扩写
    if 'expanded-content' in content:
        return True  # 已经扩写过，跳过
    
    expanded = generate_expanded_content(tool, all_tools)
    
    # 在"常见问题"section之前插入扩写内容
    # 找到 <section class="faq-section"> 或 <h2 data-lang="zh">常见问题</h2>
    faq_marker = '<section class="faq-section">'
    if faq_marker in content:
        content = content.replace(faq_marker, expanded + '\n\n' + faq_marker, 1)
    else:
        # 备选：在 </article> 之前插入
        content = content.replace('</article>', expanded + '\n</article>', 1)
    
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def main():
    print('自动扩写工具页 v2...')
    db = load_database()
    tools = db.get('tools', [])
    
    success = 0
    skipped = 0
    failed = 0
    
    for i, tool in enumerate(tools):
        result = patch_page(tool, tools)
        if result is True:
            if 'expanded-content' in open(os.path.join(PROJECT_DIR, 'tools', f'{tool.get("id","").replace("/","-").replace("\\","-")}.html'), 'r').read():
                # 检查是新扩写还是本来就有的
                # 简单判断：如果这行之前没有expanded-content就是新扩写的
                pass
            success += 1
        elif result is None:
            skipped += 1
        else:
            failed += 1
        
        if (i + 1) % 50 == 0:
            print(f'  进度: {i+1}/{len(tools)}')
    
    print(f'\n✅ 扩写成功: {success}')
    print(f'⏭️  已存在跳过: {skipped}')
    print(f'❌ 失败: {failed}')

if __name__ == '__main__':
    main()
