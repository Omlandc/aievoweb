import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Search, Filter, SlidersHorizontal } from 'lucide-react'
import { tools, categoryStats } from '@/data/tools'
import { ToolCard } from '@/components/ToolCard'
import { cn } from '@/lib/utils'

export function ToolsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'newest'>('name')

  const filteredTools = useMemo(() => {
    let result = [...tools]
    
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
    
    switch (sortBy) {
      case 'rating':
        result.sort((a, b) => (b.rating || 0) - (a.rating || 0))
        break
      case 'name':
        result.sort((a, b) => (a.nameZh || a.name).localeCompare(b.nameZh || b.name))
        break
    }
    
    return result
  }, [searchQuery, selectedCategory, sortBy])

  const categories = Object.entries(categoryStats).sort((a, b) => b[1] - a[1])

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">AI工具大全</h1>
        <p className="text-muted-foreground">共收录 {tools.length} 款AI工具，按分类浏览</p>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="搜索工具..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border bg-card focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-muted-foreground" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="px-3 py-2.5 rounded-lg border bg-card text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            <option value="name">按名称</option>
            <option value="rating">按评分</option>
          </select>
        </div>
      </div>

      {/* Category Filters */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setSelectedCategory('all')}
          className={cn(
            'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
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
              'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
              selectedCategory === cat
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            )}
          >
            {cat} ({count})
          </button>
        ))}
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredTools.map((tool, i) => (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03, duration: 0.3 }}
          >
            <ToolCard tool={tool} />
          </motion.div>
        ))}
      </div>

      {filteredTools.length === 0 && (
        <div className="text-center py-20 text-muted-foreground">
          <Filter className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>没有找到匹配的工具</p>
          <p className="text-sm mt-1">试试其他关键词或分类</p>
        </div>
      )}
    </div>
  )
}
