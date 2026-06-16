#!/usr/bin/env python3
"""
auto-tools-bot.py — 全自动AI工具发现引擎
从RSS和推文数据中提取AI工具，自动生成功能点评，更新数据库
"""

import json
import re
import os
import sys
from datetime import datetime, timezone
from collections import defaultdict

# 已知AI工具库（持续自动扩充）
KNOWN_TOOLS = {
    "chatgpt": {"name": "ChatGPT", "nameZh": "ChatGPT", "category": "productivity", "tags": ["对话", "写作", "AI助手"], "icon": "🤖"},
    "gpt-4": {"name": "GPT-4", "nameZh": "GPT-4", "category": "productivity", "tags": ["大模型", "AI助手"], "icon": "🧠"},
    "gpt-4o": {"name": "GPT-4o", "nameZh": "GPT-4o", "category": "productivity", "tags": ["多模态", "大模型"], "icon": "🧠"},
    "claude": {"name": "Claude", "nameZh": "Claude", "category": "productivity", "tags": ["对话", "写作", "AI助手"], "icon": "🤖"},
    "midjourney": {"name": "Midjourney", "nameZh": "Midjourney", "category": "image", "tags": ["图像生成", "AI绘画"], "icon": "🎨"},
    "stable diffusion": {"name": "Stable Diffusion", "nameZh": "Stable Diffusion", "category": "image", "tags": ["图像生成", "开源"], "icon": "🎨"},
    "dall-e": {"name": "DALL-E", "nameZh": "DALL-E", "category": "image", "tags": ["图像生成", "AI绘画"], "icon": "🎨"},
    "runway": {"name": "Runway", "nameZh": "Runway", "category": "video", "tags": ["视频生成", "AI视频"], "icon": "🎬"},
    "sora": {"name": "Sora", "nameZh": "Sora", "category": "video", "tags": ["视频生成", "OpenAI"], "icon": "🎬"},
    "notion": {"name": "Notion", "nameZh": "Notion", "category": "productivity", "tags": ["笔记", "协作", "知识管理"], "icon": "📝"},
    "cursor": {"name": "Cursor", "nameZh": "Cursor", "category": "code", "tags": ["AI编程", "代码编辑器"], "icon": "💻"},
    "github copilot": {"name": "GitHub Copilot", "nameZh": "GitHub Copilot", "category": "code", "tags": ["AI编程", "代码补全"], "icon": "💻"},
    "figma": {"name": "Figma", "nameZh": "Figma", "category": "design", "tags": ["设计", "UI/UX", "协作"], "icon": "🎨"},
    "canva": {"name": "Canva", "nameZh": "Canva", "category": "design", "tags": ["设计", "模板", "易用"], "icon": "🎨"},
    "jasper": {"name": "Jasper", "nameZh": "Jasper", "category": "writing", "tags": ["AI写作", "营销文案"], "icon": "✍️"},
    "copy.ai": {"name": "Copy.ai", "nameZh": "Copy.ai", "category": "writing", "tags": ["AI写作", "营销文案"], "icon": "✍️"},
    "grammarly": {"name": "Grammarly", "nameZh": "Grammarly", "category": "writing", "tags": ["语法检查", "写作辅助"], "icon": "✍️"},
    "elevenlabs": {"name": "ElevenLabs", "nameZh": "ElevenLabs", "category": "audio", "tags": ["语音合成", "AI配音"], "icon": "🎵"},
    "murf": {"name": "Murf", "nameZh": "Murf", "category": "audio", "tags": ["语音合成", "AI配音"], "icon": "🎵"},
    "descript": {"name": "Descript", "nameZh": "Descript", "category": "audio", "tags": ["音频编辑", "播客"], "icon": "🎵"},
    "perplexity": {"name": "Perplexity", "nameZh": "Perplexity", "category": "research", "tags": ["AI搜索", "问答"], "icon": "🔬"},
    "arc": {"name": "Arc Browser", "nameZh": "Arc浏览器", "category": "productivity", "tags": ["浏览器", "AI功能"], "icon": "🌐"},
    "replit": {"name": "Replit", "nameZh": "Replit", "category": "code", "tags": ["在线编程", "AI编程"], "icon": "💻"},
    "vercel": {"name": "Vercel", "nameZh": "Vercel", "category": "code", "tags": ["部署", "前端", "AI功能"], "icon": "🚀"},
    "supabase": {"name": "Supabase", "nameZh": "Supabase", "category": "code", "tags": ["数据库", "后端", "开源"], "icon": "🗄️"},
    "hugging face": {"name": "Hugging Face", "nameZh": "Hugging Face", "category": "code", "tags": ["AI模型", "开源", "社区"], "icon": "🤗"},
    "langchain": {"name": "LangChain", "nameZh": "LangChain", "category": "code", "tags": ["AI框架", "开发工具"], "icon": "🔗"},
    "llamaindex": {"name": "LlamaIndex", "nameZh": "LlamaIndex", "category": "code", "tags": ["AI框架", "RAG"], "icon": "🔗"},
    "pinecone": {"name": "Pinecone", "nameZh": "Pinecone", "category": "code", "tags": ["向量数据库", "AI基础设施"], "icon": "🗄️"},
    "weaviate": {"name": "Weaviate", "nameZh": "Weaviate", "category": "code", "tags": ["向量数据库", "AI搜索"], "icon": "🗄️"},
    "anthropic": {"name": "Anthropic", "nameZh": "Anthropic", "category": "productivity", "tags": ["AI公司", "Claude"], "icon": "🏢"},
    "openai": {"name": "OpenAI", "nameZh": "OpenAI", "category": "productivity", "tags": ["AI公司", "GPT"], "icon": "🏢"},
    "google bard": {"name": "Google Bard", "nameZh": "Google Bard", "category": "productivity", "tags": ["AI搜索", "对话"], "icon": "🔍"},
    "gemini": {"name": "Gemini", "nameZh": "Gemini", "category": "productivity", "tags": ["多模态", "大模型"], "icon": "♊"},
    "meta ai": {"name": "Meta AI", "nameZh": "Meta AI", "category": "productivity", "tags": ["大模型", "社交AI"], "icon": "🏢"},
    "llama": {"name": "LLaMA", "nameZh": "LLaMA", "category": "code", "tags": ["开源模型", "大模型"], "icon": "🦙"},
    "stablelm": {"name": "StableLM", "nameZh": "StableLM", "category": "code", "tags": ["开源模型", "Stability"], "icon": "🦙"},
    "nvidia": {"name": "NVIDIA", "nameZh": "NVIDIA", "category": "code", "tags": ["GPU", "AI芯片"], "icon": "🎮"},
    "cloudflare": {"name": "Cloudflare", "nameZh": "Cloudflare", "category": "code", "tags": ["CDN", "部署", "AI Workers"], "icon": "☁️"},
    "fastapi": {"name": "FastAPI", "nameZh": "FastAPI", "category": "code", "tags": ["后端框架", "Python"], "icon": "🚀"},
    "docker": {"name": "Docker", "nameZh": "Docker", "category": "code", "tags": ["容器", "部署"], "icon": "🐳"},
    "kubernetes": {"name": "Kubernetes", "nameZh": "Kubernetes", "category": "code", "tags": ["容器编排", "DevOps"], "icon": "☸️"},
    "tailwind": {"name": "Tailwind CSS", "nameZh": "Tailwind CSS", "category": "code", "tags": ["CSS框架", "前端"], "icon": "🌊"},
    "shadcn": {"name": "shadcn/ui", "nameZh": "shadcn/ui", "category": "code", "tags": ["UI组件", "React"], "icon": "🧩"},
    "next.js": {"name": "Next.js", "nameZh": "Next.js", "category": "code", "tags": ["React框架", "全栈"], "icon": "▲"},
    "astro": {"name": "Astro", "nameZh": "Astro", "category": "code", "tags": ["静态站点", "前端"], "icon": "🚀"},
    "svelte": {"name": "Svelte", "nameZh": "Svelte", "category": "code", "tags": ["前端框架", "编译型"], "icon": "🔥"},
    "vue": {"name": "Vue.js", "nameZh": "Vue.js", "category": "code", "tags": ["前端框架", "渐进式"], "icon": "💚"},
    "react": {"name": "React", "nameZh": "React", "category": "code", "tags": ["前端框架", "组件化"], "icon": "⚛️"},
    "typescript": {"name": "TypeScript", "nameZh": "TypeScript", "category": "code", "tags": ["类型系统", "JavaScript"], "icon": "📘"},
    "bun": {"name": "Bun", "nameZh": "Bun", "category": "code", "tags": ["JS运行时", "快速"], "icon": "🥟"},
    "deno": {"name": "Deno", "nameZh": "Deno", "category": "code", "tags": ["JS运行时", "安全"], "icon": "🦕"},
    "rust": {"name": "Rust", "nameZh": "Rust", "category": "code", "tags": ["系统编程", "安全"], "icon": "🦀"},
    "go": {"name": "Go", "nameZh": "Go", "category": "code", "tags": ["后端语言", "并发"], "icon": "🐹"},
    "zig": {"name": "Zig", "nameZh": "Zig", "category": "code", "tags": ["系统编程", "现代C"], "icon": "⚡"},
    "tauri": {"name": "Tauri", "nameZh": "Tauri", "category": "code", "tags": ["桌面应用", "Rust"], "icon": "🦀"},
    "flutter": {"name": "Flutter", "nameZh": "Flutter", "category": "code", "tags": ["跨平台", "移动开发"], "icon": "🦋"},
    "electron": {"name": "Electron", "nameZh": "Electron", "category": "code", "tags": ["桌面应用", "JS"], "icon": "⚛️"},
    "raycast": {"name": "Raycast", "nameZh": "Raycast", "category": "productivity", "tags": ["启动器", "Mac工具"], "icon": "⚡"},
    "alfred": {"name": "Alfred", "nameZh": "Alfred", "category": "productivity", "tags": ["启动器", "Mac工具"], "icon": "🎩"},
    "obsidian": {"name": "Obsidian", "nameZh": "Obsidian", "category": "productivity", "tags": ["笔记", "知识管理", "Markdown"], "icon": "🪨"},
    "logseq": {"name": "Logseq", "nameZh": "Logseq", "category": "productivity", "tags": ["笔记", "大纲", "开源"], "icon": "🌳"},
    "heptabase": {"name": "Heptabase", "nameZh": "Heptabase", "category": "productivity", "tags": ["笔记", "白板", "可视化"], "icon": "📊"},
    "readwise": {"name": "Readwise", "nameZh": "Readwise", "category": "education", "tags": ["阅读", "笔记", "高亮"], "icon": "📖"},
    "omnivore": {"name": "Omnivore", "nameZh": "Omnivore", "category": "education", "tags": ["阅读", "稍后读", "开源"], "icon": "📚"},
    "pocket": {"name": "Pocket", "nameZh": "Pocket", "category": "education", "tags": ["稍后读", "阅读"], "icon": "📚"},
    "instapaper": {"name": "Instapaper", "nameZh": "Instapaper", "category": "education", "tags": ["稍后读", "阅读"], "icon": "📄"},
    "zotero": {"name": "Zotero", "nameZh": "Zotero", "category": "research", "tags": ["文献管理", "学术"], "icon": "📚"},
    "mendeley": {"name": "Mendeley", "nameZh": "Mendeley", "category": "research", "tags": ["文献管理", "学术"], "icon": "📚"},
    "connected papers": {"name": "Connected Papers", "nameZh": "Connected Papers", "category": "research", "tags": ["文献图谱", "学术"], "icon": "🔬"},
    "elicit": {"name": "Elicit", "nameZh": "Elicit", "category": "research", "tags": ["AI研究", "文献分析"], "icon": "🔬"},
    "semantic scholar": {"name": "Semantic Scholar", "nameZh": "Semantic Scholar", "category": "research", "tags": ["学术搜索", "AI"], "icon": "🔬"},
    "scholar.google": {"name": "Google Scholar", "nameZh": "Google Scholar", "category": "research", "tags": ["学术搜索", "论文"], "icon": "🎓"},
    "overleaf": {"name": "Overleaf", "nameZh": "Overleaf", "category": "education", "tags": ["LaTeX", "协作写作"], "icon": "📄"},
    "quip": {"name": "Quip", "nameZh": "Quip", "category": "productivity", "tags": ["文档", "协作"], "icon": "📝"},
    "slack": {"name": "Slack", "nameZh": "Slack", "category": "productivity", "tags": ["协作", "通讯"], "icon": "💬"},
    "discord": {"name": "Discord", "nameZh": "Discord", "category": "productivity", "tags": ["社区", "通讯"], "icon": "🎮"},
    "linear": {"name": "Linear", "nameZh": "Linear", "category": "productivity", "tags": ["项目管理", "Issue追踪"], "icon": "📊"},
    "notion calendar": {"name": "Notion Calendar", "nameZh": "Notion Calendar", "category": "productivity", "tags": ["日历", "时间管理"], "icon": "📅"},
    "cron": {"name": "Cron", "nameZh": "Cron", "category": "productivity", "tags": ["日历", "时间管理"], "icon": "⏰"},
    "amie": {"name": "Amie", "nameZh": "Amie", "category": "productivity", "tags": ["日历", "生产力"], "icon": "📅"},
    "calendly": {"name": "Calendly", "nameZh": "Calendly", "category": "business", "tags": ["预约", "日程"], "icon": "📅"},
    "loom": {"name": "Loom", "nameZh": "Loom", "category": "video", "tags": ["录屏", "视频消息"], "icon": "📹"},
    "screen studio": {"name": "Screen Studio", "nameZh": "Screen Studio", "category": "video", "tags": ["录屏", "Mac"], "icon": "🎬"},
    "clipchamp": {"name": "Clipchamp", "nameZh": "Clipchamp", "category": "video", "tags": ["视频编辑", "微软"], "icon": "✂️"},
    "capcut": {"name": "CapCut", "nameZh": "CapCut", "category": "video", "tags": ["视频编辑", "移动端"], "icon": "✂️"},
    "premiere": {"name": "Adobe Premiere", "nameZh": "Adobe Premiere", "category": "video", "tags": ["专业视频", "剪辑"], "icon": "🎬"},
    "davinci": {"name": "DaVinci Resolve", "nameZh": "DaVinci Resolve", "category": "video", "tags": ["专业视频", "调色", "免费"], "icon": "🎬"},
    "final cut": {"name": "Final Cut Pro", "nameZh": "Final Cut Pro", "category": "video", "tags": ["专业视频", "Mac"], "icon": "🎬"},
    "imovie": {"name": "iMovie", "nameZh": "iMovie", "category": "video", "tags": ["视频编辑", "Mac", "免费"], "icon": "🎬"},
    "blender": {"name": "Blender", "nameZh": "Blender", "category": "design", "tags": ["3D建模", "动画", "开源"], "icon": "🎨"},
    "sketch": {"name": "Sketch", "nameZh": "Sketch", "category": "design", "tags": ["UI设计", "Mac"], "icon": "🎨"},
    "adobe xd": {"name": "Adobe XD", "nameZh": "Adobe XD", "category": "design", "tags": ["UI设计", "原型"], "icon": "🎨"},
    "invision": {"name": "InVision", "nameZh": "InVision", "category": "design", "tags": ["原型", "协作设计"], "icon": "🎨"},
    "framer": {"name": "Framer", "nameZh": "Framer", "category": "design", "tags": ["原型", "网站构建", "AI"], "icon": "🎨"},
    "webflow": {"name": "Webflow", "nameZh": "Webflow", "category": "design", "tags": ["无代码", "网站构建"], "icon": "🌐"},
    "wix": {"name": "Wix", "nameZh": "Wix", "category": "design", "tags": ["无代码", "网站构建"], "icon": "🌐"},
    "squarespace": {"name": "Squarespace", "nameZh": "Squarespace", "category": "design", "tags": ["无代码", "网站构建"], "icon": "🌐"},
    "shopify": {"name": "Shopify", "nameZh": "Shopify", "category": "business", "tags": ["电商", "建站"], "icon": "🛒"},
    "stripe": {"name": "Stripe", "nameZh": "Stripe", "category": "business", "tags": ["支付", "SaaS"], "icon": "💳"},
    "paddle": {"name": "Paddle", "nameZh": "Paddle", "category": "business", "tags": ["支付", "SaaS"], "icon": "💳"},
    "lemon squeezy": {"name": "Lemon Squeezy", "nameZh": "Lemon Squeezy", "category": "business", "tags": ["支付", "SaaS"], "icon": "🍋"},
    "posthog": {"name": "PostHog", "nameZh": "PostHog", "category": "business", "tags": ["分析", "产品分析", "开源"], "icon": "🦔"},
    "plausible": {"name": "Plausible", "nameZh": "Plausible", "category": "business", "tags": ["分析", "隐私友好", "开源"], "icon": "📊"},
    "mixpanel": {"name": "Mixpanel", "nameZh": "Mixpanel", "category": "business", "tags": ["分析", "用户行为"], "icon": "📊"},
    "amplitude": {"name": "Amplitude", "nameZh": "Amplitude", "category": "business", "tags": ["分析", "产品分析"], "icon": "📊"},
    "segment": {"name": "Segment", "nameZh": "Segment", "category": "business", "tags": ["数据平台", "CDP"], "icon": "📊"},
    "airbyte": {"name": "Airbyte", "nameZh": "Airbyte", "category": "business", "tags": ["数据集成", "ETL", "开源"], "icon": "✈️"},
    "fivetran": {"name": "Fivetran", "nameZh": "Fivetran", "category": "business", "tags": ["数据集成", "ETL"], "icon": "✈️"},
    "dbt": {"name": "dbt", "nameZh": "dbt", "category": "business", "tags": ["数据转换", "分析工程"], "icon": "🔄"},
    "snowflake": {"name": "Snowflake", "nameZh": "Snowflake", "category": "business", "tags": ["数据仓库", "云原生"], "icon": "❄️"},
    "bigquery": {"name": "BigQuery", "nameZh": "BigQuery", "category": "business", "tags": ["数据仓库", "Google"], "icon": "☁️"},
    "clickhouse": {"name": "ClickHouse", "nameZh": "ClickHouse", "category": "business", "tags": ["分析数据库", "OLAP", "开源"], "icon": "🐭"},
    "kafka": {"name": "Apache Kafka", "nameZh": "Apache Kafka", "category": "code", "tags": ["消息队列", "流处理"], "icon": "📨"},
    "redis": {"name": "Redis", "nameZh": "Redis", "category": "code", "tags": ["缓存", "数据库", "内存"], "icon": "🔴"},
    "postgresql": {"name": "PostgreSQL", "nameZh": "PostgreSQL", "category": "code", "tags": ["数据库", "关系型", "开源"], "icon": "🐘"},
    "mysql": {"name": "MySQL", "nameZh": "MySQL", "category": "code", "tags": ["数据库", "关系型"], "icon": "🐬"},
    "mongodb": {"name": "MongoDB", "nameZh": "MongoDB", "category": "code", "tags": ["数据库", "NoSQL", "文档"], "icon": "🍃"},
    "prisma": {"name": "Prisma", "nameZh": "Prisma", "category": "code", "tags": ["ORM", "数据库"], "icon": "💎"},
    "drizzle": {"name": "Drizzle", "nameZh": "Drizzle", "category": "code", "tags": ["ORM", "TypeScript"], "icon": "🌧️"},
    "trpc": {"name": "tRPC", "nameZh": "tRPC", "category": "code", "tags": ["API", "TypeScript", "端到端类型"], "icon": "🔌"},
    "graphql": {"name": "GraphQL", "nameZh": "GraphQL", "category": "code", "tags": ["API", "查询语言"], "icon": "◈"},
    "rest": {"name": "REST API", "nameZh": "REST API", "category": "code", "tags": ["API", "标准"], "icon": "🔌"},
    "openapi": {"name": "OpenAPI", "nameZh": "OpenAPI", "category": "code", "tags": ["API", "文档", "标准"], "icon": "📘"},
    "swagger": {"name": "Swagger", "nameZh": "Swagger", "category": "code", "tags": ["API文档", "工具"], "icon": "🐕"},
    "storybook": {"name": "Storybook", "nameZh": "Storybook", "category": "code", "tags": ["UI开发", "组件"], "icon": "📚"},
    "chromatic": {"name": "Chromatic", "nameZh": "Chromatic", "category": "code", "tags": ["UI测试", "视觉回归"], "icon": "🎨"},
    "playwright": {"name": "Playwright", "nameZh": "Playwright", "category": "code", "tags": ["浏览器测试", "自动化", "微软"], "icon": "🎭"},
    "cypress": {"name": "Cypress", "nameZh": "Cypress", "category": "code", "tags": ["前端测试", "E2E"], "icon": "🌲"},
    "jest": {"name": "Jest", "nameZh": "Jest", "category": "code", "tags": ["测试", "JavaScript", "React"], "icon": "🃏"},
    "vitest": {"name": "Vitest", "nameZh": "Vitest", "category": "code", "tags": ["测试", "Vite", "快速"], "icon": "⚡"},
    "msw": {"name": "MSW", "nameZh": "MSW", "category": "code", "tags": ["Mock", "API", "测试"], "icon": "🎭"},
    "zod": {"name": "Zod", "nameZh": "Zod", "category": "code", "tags": ["验证", "TypeScript", "Schema"], "icon": "🛡️"},
    "yup": {"name": "Yup", "nameZh": "Yup", "category": "code", "tags": ["验证", "Schema"], "icon": "🛡️"},
    "react-hook-form": {"name": "React Hook Form", "nameZh": "React Hook Form", "category": "code", "tags": ["表单", "React", "性能"], "icon": "📝"},
    "formik": {"name": "Formik", "nameZh": "Formik", "category": "code", "tags": ["表单", "React"], "icon": "📝"},
    "react-query": {"name": "TanStack Query", "nameZh": "TanStack Query", "category": "code", "tags": ["数据获取", "缓存", "React"], "icon": "⚡"},
    "swr": {"name": "SWR", "nameZh": "SWR", "category": "code", "tags": ["数据获取", "缓存", "Vercel"], "icon": "🔄"},
    "zustand": {"name": "Zustand", "nameZh": "Zustand", "category": "code", "tags": ["状态管理", "React", "轻量"], "icon": "🐻"},
    "redux": {"name": "Redux", "nameZh": "Redux", "category": "code", "tags": ["状态管理", "React"], "icon": "🔄"},
    "mobx": {"name": "MobX", "nameZh": "MobX", "category": "code", "tags": ["状态管理", "React", "响应式"], "icon": "🔄"},
    "recoil": {"name": "Recoil", "nameZh": "Recoil", "category": "code", "tags": ["状态管理", "React", "原子化"], "icon": "⚛️"},
    "jotai": {"name": "Jotai", "nameZh": "Jotai", "category": "code", "tags": ["状态管理", "React", "原子化"], "icon": "⚛️"},
    "valtio": {"name": "Valtio", "nameZh": "Valtio", "category": "code", "tags": ["状态管理", "React", "代理"], "icon": "🔄"},
    "xstate": {"name": "XState", "nameZh": "XState", "category": "code", "tags": ["状态机", "逻辑", "可视化"], "icon": "🤖"},
    "immer": {"name": "Immer", "nameZh": "Immer", "category": "code", "tags": ["不可变数据", "React"], "icon": "🧊"},
    "lodash": {"name": "Lodash", "nameZh": "Lodash", "category": "code", "tags": ["工具库", "JavaScript"], "icon": "🧰"},
    "ramda": {"name": "Ramda", "nameZh": "Ramda", "category": "code", "tags": ["函数式", "JavaScript"], "icon": "🐏"},
    "date-fns": {"name": "date-fns", "nameZh": "date-fns", "category": "code", "tags": ["日期处理", "JavaScript"], "icon": "📅"},
    "dayjs": {"name": "Day.js", "nameZh": "Day.js", "category": "code", "tags": ["日期处理", "轻量", "Moment替代"], "icon": "📅"},
    "moment": {"name": "Moment.js", "nameZh": "Moment.js", "category": "code", "tags": ["日期处理", "JavaScript"], "icon": "📅"},
    "axios": {"name": "Axios", "nameZh": "Axios", "category": "code", "tags": ["HTTP请求", "JavaScript"], "icon": "📡"},
    "fetch": {"name": "Fetch API", "nameZh": "Fetch API", "category": "code", "tags": ["HTTP请求", "原生"], "icon": "📡"},
    "ws": {"name": "WebSocket", "nameZh": "WebSocket", "category": "code", "tags": ["实时通信", "协议"], "icon": "🔌"},
    "socket.io": {"name": "Socket.io", "nameZh": "Socket.io", "category": "code", "tags": ["实时通信", "WebSocket"], "icon": "🔌"},
    "pusher": {"name": "Pusher", "nameZh": "Pusher", "category": "code", "tags": ["实时通信", "SaaS"], "icon": "📡"},
    "ably": {"name": "Ably", "nameZh": "Ably", "category": "code", "tags": ["实时通信", "SaaS"], "icon": "📡"},
    "pubnub": {"name": "PubNub", "nameZh": "PubNub", "category": "code", "tags": ["实时通信", "SaaS"], "icon": "📡"},
    "twilio": {"name": "Twilio", "nameZh": "Twilio", "category": "code", "tags": ["通信", "SMS", "API"], "icon": "📱"},
    "sendgrid": {"name": "SendGrid", "nameZh": "SendGrid", "category": "code", "tags": ["邮件", "API", "Twilio"], "icon": "📧"},
    "resend": {"name": "Resend", "nameZh": "Resend", "category": "code", "tags": ["邮件", "API", "开发者友好"], "icon": "📧"},
    "mailgun": {"name": "Mailgun", "nameZh": "Mailgun", "category": "code", "tags": ["邮件", "API"], "icon": "📧"},
    "postmark": {"name": "Postmark", "nameZh": "Postmark", "category": "code", "tags": ["邮件", "API", "高送达率"], "icon": "📧"},
    "loops": {"name": "Loops", "nameZh": "Loops", "category": "code", "tags": ["邮件营销", "SaaS"], "icon": "📧"},
    "beehiiv": {"name": "beehiiv", "nameZh": "beehiiv", "category": "business", "tags": ["邮件营销", "新闻通讯"], "icon": "📧"},
    "substack": {"name": "Substack", "nameZh": "Substack", "category": "business", "tags": ["付费邮件", "创作者"], "icon": "📧"},
    "convertkit": {"name": "ConvertKit", "nameZh": "ConvertKit", "category": "business", "tags": ["邮件营销", "创作者"], "icon": "📧"},
    "ghost": {"name": "Ghost", "nameZh": "Ghost", "category": "business", "tags": ["博客", "邮件", "开源"], "icon": "👻"},
    "wordpress": {"name": "WordPress", "nameZh": "WordPress", "category": "business", "tags": ["CMS", "博客", "建站"], "icon": "📝"},
    "strapi": {"name": "Strapi", "nameZh": "Strapi", "category": "code", "tags": ["CMS", "无头", "开源"], "icon": "🚀"},
    "directus": {"name": "Directus", "nameZh": "Directus", "category": "code", "tags": ["CMS", "无头", "开源"], "icon": "🚀"},
    "sanity": {"name": "Sanity", "nameZh": "Sanity", "category": "code", "tags": ["CMS", "无头", "结构化内容"], "icon": "🤪"},
    "contentful": {"name": "Contentful", "nameZh": "Contentful", "category": "code", "tags": ["CMS", "无头", "SaaS"], "icon": "📦"},
    "builder.io": {"name": "Builder.io", "nameZh": "Builder.io", "category": "code", "tags": ["可视化", "CMS", "React"], "icon": "🧱"},
    "plasmic": {"name": "Plasmic", "nameZh": "Plasmic", "category": "code", "tags": ["可视化", "设计到代码", "React"], "icon": "🧬"},
    "retool": {"name": "Retool", "nameZh": "Retool", "category": "business", "tags": ["内部工具", "低代码"], "icon": "🛠️"},
    "appsmith": {"name": "Appsmith", "nameZh": "Appsmith", "category": "business", "tags": ["内部工具", "低代码", "开源"], "icon": "🛠️"},
    "tooljet": {"name": "ToolJet", "nameZh": "ToolJet", "category": "business", "tags": ["内部工具", "低代码", "开源"], "icon": "🛠️"},
    "budibase": {"name": "Budibase", "nameZh": "Budibase", "category": "business", "tags": ["内部工具", "低代码", "开源"], "icon": "🛠️"},
    "n8n": {"name": "n8n", "nameZh": "n8n", "category": "business", "tags": ["工作流", "自动化", "开源"], "icon": "🔄"},
    "zapier": {"name": "Zapier", "nameZh": "Zapier", "category": "business", "tags": ["工作流", "自动化", "SaaS"], "icon": "⚡"},
    "make": {"name": "Make", "nameZh": "Make", "category": "business", "tags": ["工作流", "自动化", "可视化"], "icon": "🔧"},
    "ifttt": {"name": "IFTTT", "nameZh": "IFTTT", "category": "business", "tags": ["自动化", "简单", "消费者"], "icon": "🔗"},
    "huginn": {"name": "Huginn", "nameZh": "Huginn", "category": "business", "tags": ["自动化", "开源", "自托管"], "icon": "🐦"},
    " activepieces": {"name": "Activepieces", "nameZh": "Activepieces", "category": "business", "tags": ["工作流", "自动化", "开源"], "icon": "🧩"},
    "windmill": {"name": "Windmill", "nameZh": "Windmill", "category": "business", "tags": ["工作流", "自动化", "开源"], "icon": "🌬️"},
}

# 自动生成的点评模板（根据分类）
DESCRIPTION_TEMPLATES = {
    "productivity": [
        "提升效率的AI工具，让工作流更智能",
        "自动化重复任务，专注创造性工作",
        "AI驱动的生产力工具，节省时间"
    ],
    "design": [
        "AI辅助设计工具，让创意更快落地",
        "智能设计助手，从概念到成品",
        "AI驱动的创意工具，设计更简单"
    ],
    "code": [
        "AI编程助手，提升开发效率",
        "开发者工具，让代码更智能",
        "开源技术，构建现代应用"
    ],
    "video": [
        "AI视频创作工具，让视频制作更简单",
        "智能视频编辑，快速出片",
        "AI驱动的视频生成工具"
    ],
    "audio": [
        "AI音频工具，让声音更智能",
        "语音合成与音频处理",
        "AI驱动的音频创作"
    ],
    "writing": [
        "AI写作助手，让内容创作更轻松",
        "智能写作工具，提升文字质量",
        "AI驱动的内容生成"
    ],
    "image": [
        "AI图像生成工具，让创意可视化",
        "智能图像创作，从文字到画面",
        "AI驱动的视觉设计"
    ],
    "business": [
        "AI商业工具，让决策更智能",
        "数据驱动的产品增长工具",
        "AI驱动的商业解决方案"
    ],
    "education": [
        "AI学习工具，让知识获取更高效",
        "智能教育工具，个性化学习",
        "AI驱动的知识管理"
    ],
    "research": [
        "AI研究工具，加速学术发现",
        "智能文献分析，提升研究效率",
        "AI驱动的学术搜索"
    ]
}

def load_database():
    """加载工具数据库"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tools-database.json')
    if os.path.exists(db_path):
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "total": 0, "categories": [], "tools": []}

def save_database(db):
    """保存工具数据库"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tools-database.json')
    db['total'] = len(db['tools'])
    db['version'] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据库已更新: {db['total']} 个工具")

def generate_description(tool_info):
    """根据分类自动生成点评"""
    import random
    category = tool_info.get('category', 'productivity')
    templates = DESCRIPTION_TEMPLATES.get(category, DESCRIPTION_TEMPLATES['productivity'])
    return random.choice(templates)

def detect_tools_from_text(text):
    """从文本中提取已知的工具名"""
    text_lower = text.lower()
    found = []
    for key, info in KNOWN_TOOLS.items():
        if key in text_lower:
            found.append(info)
    return found

def add_tool_to_database(db, tool_info, source=""):
    """添加工具到数据库（如果已存在则更新mentions）"""
    tool_id = tool_info['name'].lower().replace(' ', '-').replace('.', '')
    
    for existing in db['tools']:
        if existing['id'] == tool_id:
            existing['mentions'] = existing.get('mentions', 0) + 1
            if source and source not in existing.get('sources', []):
                existing.setdefault('sources', []).append(source)
            return False
    
    new_tool = {
        "id": tool_id,
        "name": tool_info['name'],
        "nameZh": tool_info.get('nameZh', tool_info['name']),
        "url": tool_info.get('url', f"https://www.google.com/search?q={tool_info['name']}"),
        "icon": tool_info.get('icon', '🔧'),
        "category": tool_info['category'],
        "tags": tool_info.get('tags', []),
        "description": tool_info.get('description', generate_description(tool_info)),
        "descriptionZh": tool_info.get('descriptionZh', generate_description(tool_info)),
        "pricing": tool_info.get('pricing', 'freemium'),
        "pricingZh": tool_info.get('pricingZh', '免费增值'),
        "featured": False,
        "dateAdded": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "mentions": 1,
        "sources": [source] if source else []
    }
    
    db['tools'].append(new_tool)
    return True

def process_rss_data():
    """从RSS数据中提取工具"""
    db = load_database()
    rss_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw-rss.json')
    
    if not os.path.exists(rss_path):
        print("⚠️ raw-rss.json 不存在，跳过")
        return db
    
    try:
        with open(rss_path, 'r', encoding='utf-8') as f:
            rss_data = json.load(f)
    except:
        print("⚠️ raw-rss.json 解析失败")
        return db
    
    added_count = 0
    
    # 处理不同格式的RSS数据
    if isinstance(rss_data, list):
        entries = rss_data
        for entry in entries[:20]:
            text = f"{entry.get('title', '')} {entry.get('summary', '')}"
            found_tools = detect_tools_from_text(text)
            for tool_info in found_tools:
                if add_tool_to_database(db, tool_info, "rss"):
                    added_count += 1
                    print(f"  + 发现工具: {tool_info['name']}")
    elif isinstance(rss_data, dict):
        for source_name, entries in rss_data.items():
            for entry in entries[:20]:
                text = f"{entry.get('title', '')} {entry.get('summary', '')}"
                found_tools = detect_tools_from_text(text)
                for tool_info in found_tools:
                    if add_tool_to_database(db, tool_info, source_name):
                        added_count += 1
                        print(f"  + 发现工具: {tool_info['name']} (来自 {source_name})")
    else:
        print("⚠️ RSS数据格式未知")
    
    print(f"\n📊 本次新增: {added_count} 个工具")
    save_database(db)
    return db

def init_database():
    """初始化数据库：加载所有已知工具"""
    db = load_database()
    
    if len(db['tools']) > 0:
        print(f"📦 数据库已有 {len(db['tools'])} 个工具，跳过初始化")
        return db
    
    print("🚀 初始化工具数据库...")
    added = 0
    for key, info in KNOWN_TOOLS.items():
        if add_tool_to_database(db, info, "init"):
            added += 1
    
    print(f"✅ 初始化完成: {added} 个工具")
    save_database(db)
    return db

def update_tool_rankings():
    """更新工具排名（根据mentions）"""
    db = load_database()
    
    # 按mentions排序，取Top 10设为featured
    sorted_tools = sorted(db['tools'], key=lambda x: x.get('mentions', 0), reverse=True)
    
    for tool in db['tools']:
        tool['featured'] = False
    
    for tool in sorted_tools[:10]:
        tool['featured'] = True
    
    save_database(db)
    print(f"🏆 已更新排名，Top 10: {[t['name'] for t in sorted_tools[:10]]}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        init_database()
    elif len(sys.argv) > 1 and sys.argv[1] == 'rank':
        update_tool_rankings()
    else:
        # 默认：从RSS提取 + 更新排名
        db = init_database() if len(db['tools']) == 0 else load_database()
        process_rss_data()
        update_tool_rankings()

if __name__ == '__main__':
    db = load_database()
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        init_database()
    elif len(sys.argv) > 1 and sys.argv[1] == 'rank':
        update_tool_rankings()
    else:
        if len(db['tools']) == 0:
            init_database()
        process_rss_data()
        update_tool_rankings()
