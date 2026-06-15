#!/usr/bin/env python3
"""
内容处理助手 - 人工审核 + AI 生成高质量双语摘要

工作流程:
1. rss-bot.py 自动抓取原始数据到 data/raw-rss.json
2. 运行此脚本查看待处理内容
3. 人工挑选有价值的内容
4. 调用 Kimi 生成高质量双语摘要
5. 保存到 data/tweets.json

用法:
  python3 scripts/process-content.py          # 查看待处理内容
  python3 scripts/process-content.py --auto   # 自动处理（需配置API）
"""

import json
import os
import sys
from datetime import datetime, timezone

def load_json(filepath):
    """加载 JSON 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    filepath = os.path.join(project_dir, filepath)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(data, filepath):
    """保存 JSON 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    filepath = os.path.join(project_dir, filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def show_pending():
    """显示待处理的原始数据"""
    raw = load_json("data/raw-rss.json")
    
    if not raw:
        print("📭 没有待处理的原始数据")
        print("   先运行: python3 scripts/rss-bot.py")
        return
    
    print(f"\n📥 待处理原始数据: {len(raw)} 条\n")
    print("=" * 80)
    
    for i, item in enumerate(raw[:30], 1):
        lang_emoji = "🇨🇳" if item.get('lang') == 'zh' else "🇺🇸"
        print(f"\n[{i}] {lang_emoji} [{item['source']}] {item['date']}")
        print(f"    标题: {item['title'][:80]}")
        if item.get('summary'):
            print(f"    摘要: {item['summary'][:120]}...")
        print(f"    链接: {item['link']}")
        print(f"    ID: {item['id']}")
    
    print(f"\n{'=' * 80}")
    print(f"\n💡 下一步:")
    print(f"   1. 挑选有价值的内容（记住编号）")
    print(f"   2. 用 Kimi 生成高质量双语摘要")
    print(f"   3. 保存到 data/tweets.json")

def generate_kimi_prompt(selected_items):
    """生成给 Kimi 的提示词"""
    prompt = """请为以下 RSS 内容生成高质量的双语（中文+英文）摘要推文。

要求：
1. 每条内容生成:
   - 中文标题（精炼有力，15字以内）
   - 中文摘要（80-150字，包含核心观点）
   - 英文标题（准确翻译）
   - 英文摘要（自然流畅，不是直译）
   - 分类标签（#AI工具 #前端开发 #产品设计 #科技新闻 #创业干货 #效率工具 #开源项目 #AI研究 #硬件新品）
   - 原文链接

2. 风格要求:
   - 中文：像科技媒体编辑写的，有观点有洞察
   - 英文：native speaker 水平，专业但易读
   - 不是机器翻译，而是重新组织表达

3. 输出格式（严格JSON）:
[
  {
    "id": "原始ID",
    "zh": {"title": "...", "content": "...", "category": "#标签"},
    "en": {"title": "...", "content": "...", "category": "#Tag"},
    "link": "原文链接",
    "source": "来源",
    "date": "日期",
    "type": "long/short"
  }
]

待处理内容：
"""
    
    for item in selected_items:
        prompt += f"\n---\n"
        prompt += f"ID: {item['id']}\n"
        prompt += f"来源: {item['source']} ({item['lang']})\n"
        prompt += f"标题: {item['title']}\n"
        if item.get('summary'):
            prompt += f"摘要: {item['summary']}\n"
        prompt += f"链接: {item['link']}\n"
        prompt += f"日期: {item['date']}\n"
    
    prompt += "\n\n请输出完整JSON数组，不要省略任何字段。"
    return prompt

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("自动模式未实现，请先使用手动模式")
        return
    
    show_pending()
    
    raw = load_json("data/raw-rss.json")
    if raw:
        print(f"\n📝 生成 Kimi 提示词...")
        prompt = generate_kimi_prompt(raw[:10])
        
        # 保存提示词到文件，方便复制
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        prompt_file = os.path.join(project_dir, "data", "kimi-prompt.txt")
        
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        print(f"\n✅ Kimi 提示词已保存到: data/kimi-prompt.txt")
        print(f"\n📋 使用方式:")
        print(f"   1. 复制 kimi-prompt.txt 内容")
        print(f"   2. 发送给 Kimi，获取高质量双语摘要")
        print(f"   3. 将 Kimi 返回的 JSON 保存到 data/tweets.json")
        print(f"\n   快捷命令:")
        print(f"   cat data/kimi-prompt.txt | kimi -p")

if __name__ == "__main__":
    main()
