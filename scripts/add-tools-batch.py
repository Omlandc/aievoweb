#!/usr/bin/env python3
"""
批量补充AI工具到数据库
目标：image/writing/audio各补7个，共+21个新工具
"""

import json
import os

PROJECT_DIR = '/root/.openclaw/workspace/clawdocs/projects/玩转ai进化网'
DB_PATH = os.path.join(PROJECT_DIR, 'data', 'tools-database.json')

def load_db():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_db(db):
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_existing_ids(db):
    return {t.get('id', '') for t in db.get('tools', [])}

def get_existing_names(db):
    names = set()
    for t in db.get('tools', []):
        names.add(t.get('name', '').lower())
        names.add(t.get('nameZh', '').lower())
    return names

# 新工具列表
NEW_TOOLS = [
    # ============ IMAGE (7个) ============
    {
        "id": "leonardo-ai",
        "name": "Leonardo AI",
        "nameZh": "Leonardo AI",
        "description": "AI-powered image generation platform with fine-tuned models for game assets, concept art, and photorealistic images",
        "descriptionZh": "AI图像生成平台，专为游戏资产、概念艺术和写实图像优化的模型",
        "url": "https://leonardo.ai",
        "icon": "🎨",
        "category": "image",
        "tags": ["image generation", "game assets", "concept art"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "ideogram",
        "name": "Ideogram",
        "nameZh": "Ideogram",
        "description": "AI image generator specializing in text-in-image accuracy and typography",
        "descriptionZh": "专注于图像内文字准确性和排版设计的AI图像生成器",
        "url": "https://ideogram.ai",
        "icon": "✏️",
        "category": "image",
        "tags": ["image generation", "text-in-image", "typography"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "playground-ai",
        "name": "Playground AI",
        "nameZh": "Playground AI",
        "description": "Free AI image generator with mixed image editing and creative tools",
        "descriptionZh": "免费AI图像生成器，支持混合图像编辑和创意工具",
        "url": "https://playgroundai.com",
        "icon": "🖼️",
        "category": "image",
        "tags": ["image generation", "image editing", "mixed image editing"],
        "pricing": "Free",
        "pricingZh": "免费",
        "featured": False
    },
    {
        "id": "krea-ai",
        "name": "Krea AI",
        "nameZh": "Krea AI",
        "description": "Real-time AI image generation and upscaling tool for designers",
        "descriptionZh": "面向设计师的实时AI图像生成和放大工具",
        "url": "https://krea.ai",
        "icon": "🎭",
        "category": "image",
        "tags": ["image generation", "real-time", "upscaling"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "recraft",
        "name": "Recraft",
        "nameZh": "Recraft",
        "description": "AI-powered vector image generator for professional design workflows",
        "descriptionZh": "面向专业设计工作流的AI矢量图像生成器",
        "url": "https://recraft.ai",
        "icon": "🔷",
        "category": "image",
        "tags": ["vector generation", "design", "illustration"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "adobe-firefly",
        "name": "Adobe Firefly",
        "nameZh": "Adobe Firefly",
        "description": "Adobe's generative AI tool for creating images, vectors, and designs integrated with Creative Cloud",
        "descriptionZh": "Adobe的生成式AI工具，与Creative Cloud集成，可创建图像、矢量图和设计",
        "url": "https://firefly.adobe.com",
        "icon": "🔥",
        "category": "image",
        "tags": ["image generation", "vector", "design", "Adobe"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": True
    },
    {
        "id": "flux",
        "name": "Flux",
        "nameZh": "Flux",
        "description": "Open-source AI image generation model by Black Forest Labs, offering high-quality text-to-image generation",
        "descriptionZh": "Black Forest Labs开源的AI图像生成模型，提供高质量文本到图像生成",
        "url": "https://blackforestlabs.ai",
        "icon": "⚡",
        "category": "image",
        "tags": ["image generation", "open-source", "text-to-image"],
        "pricing": "Open Source",
        "pricingZh": "开源免费",
        "featured": False
    },
    
    # ============ AUDIO (7个) ============
    {
        "id": "suno",
        "name": "Suno",
        "nameZh": "Suno",
        "description": "AI music generation tool that creates songs with lyrics and vocals from text prompts",
        "descriptionZh": "AI音乐生成工具，可根据文本提示创作带歌词和人声的歌曲",
        "url": "https://suno.ai",
        "icon": "🎵",
        "category": "audio",
        "tags": ["music generation", "AI vocals", "song creation"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": True
    },
    {
        "id": "udio",
        "name": "Udio",
        "nameZh": "Udio",
        "description": "AI music creation platform for generating high-quality songs with vocals and instrumentals",
        "descriptionZh": "AI音乐创作平台，可生成带人声和伴奏的高质量歌曲",
        "url": "https://udio.com",
        "icon": "🎶",
        "category": "audio",
        "tags": ["music generation", "vocals", "instrumentals"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "resemble-ai",
        "name": "Resemble AI",
        "nameZh": "Resemble AI",
        "description": "AI voice cloning and text-to-speech platform for creating realistic voice content",
        "descriptionZh": "AI语音克隆和文本转语音平台，可创建逼真语音内容",
        "url": "https://resemble.ai",
        "icon": "🗣️",
        "category": "audio",
        "tags": ["voice cloning", "text-to-speech", "voice AI"],
        "pricing": "Paid",
        "pricingZh": "付费",
        "featured": False
    },
    {
        "id": "playht",
        "name": "PlayHT",
        "nameZh": "PlayHT",
        "description": "AI text-to-speech platform with ultra-realistic voices and voice cloning capabilities",
        "descriptionZh": "AI文本转语音平台，提供超逼真语音和语音克隆功能",
        "url": "https://play.ht",
        "icon": "📢",
        "category": "audio",
        "tags": ["text-to-speech", "voice cloning", "AI voice"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "lmnt",
        "name": "LMNT",
        "nameZh": "LMNT",
        "description": "Real-time AI voice synthesis and voice changer for developers and creators",
        "descriptionZh": "面向开发者和创作者的实时AI语音合成和变声器",
        "url": "https://lmnt.com",
        "icon": "🔊",
        "category": "audio",
        "tags": ["voice synthesis", "voice changer", "real-time"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "voicemod",
        "name": "Voicemod",
        "nameZh": "Voicemod",
        "description": "Real-time voice changer and soundboard for gaming and streaming",
        "descriptionZh": "面向游戏和直播的实时语音变声和音效板",
        "url": "https://voicemod.net",
        "icon": "🎤",
        "category": "audio",
        "tags": ["voice changer", "soundboard", "gaming"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "kits-ai",
        "name": "Kits AI",
        "nameZh": "Kits AI",
        "description": "AI voice platform for musicians to create vocal covers and experiment with AI voices",
        "descriptionZh": "面向音乐人的AI语音平台，可创建人声翻唱和AI语音实验",
        "url": "https://kits.ai",
        "icon": "🎧",
        "category": "audio",
        "tags": ["AI voice", "vocal covers", "music"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    
    # ============ WRITING (7个) ============
    {
        "id": "rytr",
        "name": "Rytr",
        "nameZh": "Rytr",
        "description": "AI writing assistant for creating marketing copy, emails, and blog posts in multiple tones",
        "descriptionZh": "AI写作助手，支持多种语气创建营销文案、邮件和博客文章",
        "url": "https://rytr.me",
        "icon": "✍️",
        "category": "writing",
        "tags": ["writing", "marketing copy", "blog posts"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "writesonic",
        "name": "Writesonic",
        "nameZh": "Writesonic",
        "description": "AI content creation platform for SEO-optimized articles, ads, and product descriptions",
        "descriptionZh": "AI内容创作平台，用于SEO优化的文章、广告和产品描述",
        "url": "https://writesonic.com",
        "icon": "📝",
        "category": "writing",
        "tags": ["writing", "SEO", "content creation"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "wordtune",
        "name": "Wordtune",
        "nameZh": "Wordtune",
        "description": "AI writing companion that helps rewrite and improve sentences for clarity and tone",
        "descriptionZh": "AI写作伴侣，帮助重写和改进句子，提升清晰度和语气",
        "url": "https://wordtune.com",
        "icon": "🔧",
        "category": "writing",
        "tags": ["writing", "rewriting", "tone adjustment"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "quillbot",
        "name": "QuillBot",
        "nameZh": "QuillBot",
        "description": "AI paraphrasing and grammar checking tool for academic and professional writing",
        "descriptionZh": "AI改写和语法检查工具，面向学术和专业写作",
        "url": "https://quillbot.com",
        "icon": "🦜",
        "category": "writing",
        "tags": ["paraphrasing", "grammar", "academic writing"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "notion-ai",
        "name": "Notion AI",
        "nameZh": "Notion AI",
        "description": "AI writing assistant integrated into Notion for drafting, summarizing, and editing documents",
        "descriptionZh": "集成在Notion中的AI写作助手，用于起草、总结和编辑文档",
        "url": "https://notion.so/product/ai",
        "icon": "📓",
        "category": "writing",
        "tags": ["writing", "summarization", "document editing"],
        "pricing": "Paid",
        "pricingZh": "付费",
        "featured": False
    },
    {
        "id": "hyperwrite",
        "name": "HyperWrite",
        "nameZh": "HyperWrite",
        "description": "AI writing assistant with autocomplete and content generation for faster writing",
        "descriptionZh": "AI写作助手，支持自动补全和内容生成，加速写作过程",
        "url": "https://hyperwriteai.com",
        "icon": "⚡",
        "category": "writing",
        "tags": ["writing", "autocomplete", "content generation"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
    {
        "id": "textcortex",
        "name": "TextCortex",
        "nameZh": "TextCortex",
        "description": "AI writing assistant focused on multilingual content creation and rewriting",
        "descriptionZh": "专注于多语言内容创作和重写的AI写作助手",
        "url": "https://textcortex.com",
        "icon": "🧠",
        "category": "writing",
        "tags": ["writing", "multilingual", "rewriting"],
        "pricing": "Freemium",
        "pricingZh": "免费增值",
        "featured": False
    },
]

def main():
    print("=" * 50)
    print("批量补充AI工具到数据库")
    print("=" * 50)
    
    db = load_db()
    existing_ids = get_existing_ids(db)
    existing_names = get_existing_names(db)
    
    added = 0
    skipped = 0
    
    for tool in NEW_TOOLS:
        tool_id = tool.get('id', '')
        name = tool.get('name', '').lower()
        name_zh = tool.get('nameZh', '').lower()
        
        # 检查是否已存在
        if tool_id in existing_ids or name in existing_names or name_zh in existing_names:
            print(f"  ⏭️  跳过（已存在）: {tool['name']}")
            skipped += 1
            continue
        
        db['tools'].append(tool)
        existing_ids.add(tool_id)
        existing_names.add(name)
        existing_names.add(name_zh)
        print(f"  ✅ 添加: {tool['name']} ({tool['category']})")
        added += 1
    
    save_db(db)
    
    print(f"\n{'=' * 50}")
    print(f"✅ 新增: {added} 个工具")
    print(f"⏭️  跳过: {skipped} 个（已存在）")
    print(f"📊 数据库总计: {len(db['tools'])} 个工具")
    
    # 统计各类别
    print(f"\n各类别统计:")
    for cat in ['image', 'writing', 'audio', 'code', 'productivity', 'design', 'video', 'business']:
        count = len([t for t in db['tools'] if t.get('category') == cat])
        print(f"  {cat}: {count} 个")

if __name__ == '__main__':
    main()
