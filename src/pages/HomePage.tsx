import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Search, Sparkles, TrendingUp, ArrowRight, Zap } from 'lucide-react'
import { tools, categoryStats } from '@/data/tools'
import { tasks } from '@/data/tasks'
import { ToolCard } from '@/components/ToolCard'
import { cn } from '@/lib/utils'

export function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const featuredTools = useMemo(() => 
    tools.filter(t => t.featured).slice(0, 6), 
  [])

  const filteredTools = useMemo(() => {
    let result = tools
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      result = result.filter(t => 
        (t.nameZh || t.name).toLowerCase().includes(q) ||
        (t.descriptionZh || t.description).toLowerCase().includes(q) ||
        t.tags?.some(tag => tag.toLowerCase().includes(q))
      )
    }
    if (selectedCategory !== 'all') {
      result = result.filter(t => t.category === selectedCategory)
    }
    return result.slice(0, 12)
  }, [searchQuery, selectedCategory])

  const categories = Object.entries(categoryStats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8)

  return (
    <div>
      {/* Hero */}
      <section className="hero-gradient py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              已收录 {tools.length} 款AI工具
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              发现<span className="gradient-text">2026</span>最新AI工具
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              覆盖编程、设计、写作、音频、视频等领域。每日更新，助力AI时代效率提升。
            </p>
            
            {/* Search */}
            <div className="relative max-w-xl mx-auto">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                placeholder="搜索AI工具（如：ChatGPT、Midjourney...）"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-xl border bg-card/80 backdrop-blur focus:outline-none focus:ring-2 focus:ring-primary/50 text-lg"
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Categories */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Sparkles className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold">按分类浏览</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory('all')}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium transition-colors',
              selectedCategory === 'all'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            )}
          >
            全部 ({tools.length})
          </button>
          {categories.map(([cat, count]) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                'px-4 py-2 rounded-full text-sm font-medium transition-colors',
                selectedCategory === cat
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              )}
            >
              {cat} ({count})
            </button>
          ))}
        </div>
      </section>

      {/* Featured / Search Results */}
      <section className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">
              {searchQuery ? `搜索结果 (${filteredTools.length})` : '精选工具'}
            </h2>
          </div>
          <Link to="/tools" className="text-sm text-primary flex items-center gap-1 hover:underline">
            查看全部 <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(searchQuery ? filteredTools : featuredTools).map((tool, i) => (
            <motion.div
              key={tool.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
            >
              <ToolCard tool={tool} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* Tasks */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto border-t">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-semibold">按任务发现</h2>
          </div>
          <Link to="/tasks" className="text-sm text-primary flex items-center gap-1 hover:underline">
            查看全部 <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {tasks.slice(0, 10).map((task) => (
            <Link
              key={task.id}
              to={`/tasks/${task.id}`}
              className="p-4 rounded-xl border bg-card hover:border-primary/50 hover:shadow-md transition-all group"
            >
              <div className="font-medium text-sm group-hover:text-primary transition-colors line-clamp-1">
                {task.title}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {task.toolCount} 个工具
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
