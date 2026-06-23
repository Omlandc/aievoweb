export interface Task {
  id: string;
  title: string;
  description?: string;
  toolCount: number;
  tags?: string[];
}

export const tasks: Task[] = [
  { id: "code", title: "代码开发", toolCount: 90, description: "AI编程助手、代码补全、代码审查等开发工具" },
  { id: "business", title: "商业应用", toolCount: 32, description: "商业分析、营销、客户关系等AI工具" },
  { id: "productivity", title: "生产力提升", toolCount: 23, description: "AI助手、自动化、效率工具" },
  { id: "writing", title: "AI写作", toolCount: 16, description: "文案生成、博客写作、内容创作工具" },
  { id: "react", title: "React开发", toolCount: 14, description: "React组件、UI库、开发工具" },
  { id: "design", title: "设计创意", toolCount: 12, description: "AI设计、图像生成、创意工具" },
  { id: "image", title: "图像处理", toolCount: 10, description: "AI图像编辑、生成、处理工具" },
  { id: "video", title: "视频制作", toolCount: 10, description: "AI视频生成、编辑、处理工具" },
  { id: "audio", title: "音频处理", toolCount: 10, description: "AI语音合成、音乐生成、音频编辑" },
  { id: "api", title: "API服务", toolCount: 10, description: "AI API、模型接口、开发服务" },
  { id: "automation", title: "自动化", toolCount: 8, description: "工作流自动化、RPA、智能代理" },
  { id: "research", title: "科研辅助", toolCount: 7, description: "AI论文、研究分析、学术工具" },
  { id: "javascript", title: "JavaScript开发", toolCount: 7, description: "JS框架、工具库、开发资源" },
  { id: "database", title: "数据库", toolCount: 6, description: "AI数据库工具、数据管理" },
  { id: "state-management", title: "状态管理", toolCount: 6, description: "状态管理库、数据流工具" },
  { id: "cms", title: "内容管理", toolCount: 6, description: "CMS系统、内容管理平台" },
  { id: "image-generation", title: "图像生成", toolCount: 6, description: "AI绘画、图像生成工具" },
  { id: "llm", title: "大模型", toolCount: 5, description: "大语言模型、AI模型平台" },
  { id: "notes", title: "笔记工具", toolCount: 5, description: "AI笔记、知识管理工具" },
  { id: "visualization", title: "数据可视化", toolCount: 5, description: "图表生成、数据展示工具" },
];