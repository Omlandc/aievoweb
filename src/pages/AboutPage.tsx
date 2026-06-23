import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Info, Sparkles, Database, Globe, ArrowRight } from 'lucide-react'
import { tools } from '@/data/tools'
import { tasks } from '@/data/tasks'

export function AboutPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Info className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-bold">关于本站</h1>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="prose dark:prose-invert max-w-none">
          <div className="p-6 rounded-xl border bg-card mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-xl font-bold">AI工具发现站</h2>
                <p className="text-sm text-muted-foreground">aigo.homes</p>
              </div>
            </div>
            <p className="text-muted-foreground">
              致力于发现、评测和推荐最新AI工具。收录了{tools.length}款AI工具，覆盖{tasks.length}个使用场景，
              每日自动更新，帮助用户快速找到最适合的AI工具。
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="p-5 rounded-xl border bg-card">
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">数据规模</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                收录 {tools.length} 款AI工具，涵盖 {Object.keys(tasks).length} 个使用场景
              </p>
            </div>
            <div className="p-5 rounded-xl border bg-card">
              <div className="flex items-center gap-2 mb-2">
                <Globe className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">覆盖领域</h3>
              </div>
              <p className="text-sm text-muted-foreground">
                编程、设计、写作、音频、视频、数据分析等领域
              </p>
            </div>
          </div>

          <div className="p-6 rounded-xl border bg-card">
            <h3 className="font-semibold mb-3">技术栈</h3>
            <div className="flex flex-wrap gap-2">
              {['React 18', 'TypeScript', 'Vite', 'Tailwind CSS', 'shadcn/ui', 'Framer Motion'].map((tech) => (
                <span key={tech} className="tag-pill">
                  {tech}
                </span>
              ))}
            </div>
          </div>

          <div className="mt-6 text-center">
            <Link
              to="/"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
            >
              开始探索 <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
