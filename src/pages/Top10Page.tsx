import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Trophy, Star, ArrowRight, TrendingUp, Award } from 'lucide-react'
import { tools, categoryStats } from '@/data/tools'
import { cn } from '@/lib/utils'

const rankingCategories = Object.entries(categoryStats)
  .sort((a, b) => b[1] - a[1])
  .map(([cat, count]) => ({
    id: cat.toLowerCase().replace(/\s+/g, '-'),
    name: cat,
    count,
  }))

export function Top10Page() {
  const { category } = useParams<{ category: string }>()
  
  const selectedCategory = category 
    ? rankingCategories.find(c => c.id === category)?.name 
    : null

  const categoryTools = selectedCategory 
    ? tools.filter(t => t.category === selectedCategory).sort((a, b) => (b.rating || 0) - (a.rating || 0))
    : tools.sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 10)

  const top10 = categoryTools.slice(0, 10)

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Trophy className="w-6 h-6 text-amber-500" />
          <h1 className="text-3xl font-bold">
            {selectedCategory ? `${selectedCategory} Top 10` : 'AI工具排行榜'}
          </h1>
        </div>
        <p className="text-muted-foreground">
          {selectedCategory 
            ? `基于评分和热度排名的${selectedCategory}领域Top 10工具`
            : '基于评分和热度排名的全站Top 10工具'}
        </p>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap gap-2 mb-8">
        <Link
          to="/top10"
          className={cn(
            'px-4 py-2 rounded-full text-sm font-medium transition-colors',
            !selectedCategory
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          )}
        >
          全站Top10
        </Link>
        {rankingCategories.map((cat) => (
          <Link
            key={cat.id}
            to={`/top10/${cat.id}`}
            className={cn(
              'px-4 py-2 rounded-full text-sm font-medium transition-colors',
              selectedCategory === cat.name
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
            )}
          >
            {cat.name}
          </Link>
        ))}
      </div>

      {/* Top 10 List */}
      <div className="space-y-4">
        {top10.map((tool, index) => (
          <motion.div
            key={tool.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05, duration: 0.3 }}
            className={cn(
              'flex items-center gap-4 p-4 rounded-xl border bg-card hover:shadow-md transition-all',
              index === 0 && 'ring-2 ring-amber-200 dark:ring-amber-900',
              index === 1 && 'ring-2 ring-gray-200 dark:ring-gray-800',
              index === 2 && 'ring-2 ring-orange-200 dark:ring-orange-900',
            )}
          >
            {/* Rank */}
            <div className={cn(
              'w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0',
              index === 0 && 'bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300',
              index === 1 && 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
              index === 2 && 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
              index > 2 && 'bg-muted text-muted-foreground',
            )}>
              {index === 0 && <Award className="w-5 h-5" />}
              {index === 1 && <TrendingUp className="w-5 h-5" />}
              {index === 2 && <Star className="w-5 h-5" />}
              {index > 2 && index + 1}
            </div>

            {/* Tool Info */}
            <div className="flex-1 min-w-0">
              <Link 
                to={`/tools/${tool.id}`}
                className="font-semibold hover:text-primary transition-colors"
              >
                {tool.nameZh || tool.name}
              </Link>
              <p className="text-sm text-muted-foreground truncate">
                {tool.descriptionZh || tool.description}
              </p>
            </div>

            {/* Rating */}
            <div className="flex items-center gap-1 flex-shrink-0">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              <span className="font-semibold">{tool.rating || '4.0'}</span>
            </div>

            {/* Action */}
            <Link
              to={`/tools/${tool.id}`}
              className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-primary transition-colors flex-shrink-0"
            >
              <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>
        ))}
      </div>

      {top10.length === 0 && (
        <div className="text-center py-20 text-muted-foreground">
          <Trophy className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>该分类暂无足够数据</p>
        </div>
      )}
    </div>
  )
}
