import { useState } from 'react'
import { motion } from 'framer-motion'
import { Scale, Star } from 'lucide-react'
import { tools } from '@/data/tools'
import { cn } from '@/lib/utils'

// Popular comparisons
const popularComparisons = [
  ['chatgpt', 'claude'],
  ['chatgpt', 'gemini'],
  ['midjourney', 'stable-diffusion'],
  ['github-copilot', 'cursor'],
  ['elevenlabs', 'murf'],
]

export function ComparePage() {
  const [tool1Id, setTool1Id] = useState('chatgpt')
  const [tool2Id, setTool2Id] = useState('claude')

  const tool1 = tools.find(t => t.id === tool1Id)
  const tool2 = tools.find(t => t.id === tool2Id)

  const setComparison = (id1: string, id2: string) => {
    setTool1Id(id1)
    setTool2Id(id2)
  }

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <Scale className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-bold">工具对比</h1>
        </div>
        <p className="text-muted-foreground">对比两款AI工具，选择最适合你的方案</p>
      </div>

      {/* Popular comparisons */}
      <div className="flex flex-wrap gap-2 mb-6">
        <span className="text-sm text-muted-foreground py-2">热门对比：</span>
        {popularComparisons.map(([id1, id2]) => {
          const t1 = tools.find(t => t.id === id1)
          const t2 = tools.find(t => t.id === id2)
          if (!t1 || !t2) return null
          return (
            <button
              key={`${id1}-${id2}`}
              onClick={() => setComparison(id1, id2)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium transition-colors',
                tool1Id === id1 && tool2Id === id2
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              )}
            >
              {t1.nameZh || t1.name} vs {t2.nameZh || t2.name}
            </button>
          )
        })}
      </div>

      {/* Tool Selectors */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div>
          <label className="text-sm font-medium mb-2 block">选择工具 A</label>
          <select
            value={tool1Id}
            onChange={(e) => setTool1Id(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg border bg-card focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            {tools.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nameZh || t.name} ({t.category})
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">选择工具 B</label>
          <select
            value={tool2Id}
            onChange={(e) => setTool2Id(e.target.value)}
            className="w-full px-4 py-2.5 rounded-lg border bg-card focus:outline-none focus:ring-2 focus:ring-primary/50"
          >
            {tools.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nameZh || t.name} ({t.category})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparison Cards */}
      {tool1 && tool2 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Tool 1 */}
            <div className="p-6 rounded-xl border bg-card">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center text-2xl font-bold text-primary mb-4">
                {tool1.name.charAt(0).toUpperCase()}
              </div>
              <h2 className="text-xl font-bold mb-2">{tool1.nameZh || tool1.name}</h2>
              <p className="text-sm text-muted-foreground mb-4">
                {tool1.descriptionZh || tool1.description}
              </p>
              {tool1.rating && (
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span className="font-semibold">{tool1.rating}</span>
                </div>
              )}
            </div>

            {/* VS */}
            <div className="flex items-center justify-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-xl font-bold text-primary">
                VS
              </div>
            </div>

            {/* Tool 2 */}
            <div className="p-6 rounded-xl border bg-card">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center text-2xl font-bold text-primary mb-4">
                {tool2.name.charAt(0).toUpperCase()}
              </div>
              <h2 className="text-xl font-bold mb-2">{tool2.nameZh || tool2.name}</h2>
              <p className="text-sm text-muted-foreground mb-4">
                {tool2.descriptionZh || tool2.description}
              </p>
              {tool2.rating && (
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span className="font-semibold">{tool2.rating}</span>
                </div>
              )}
            </div>
          </div>

          {/* Comparison Table */}
          <div className="rounded-xl border bg-card overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-6 py-4 text-left text-sm font-medium">对比维度</th>
                  <th className="px-6 py-4 text-left text-sm font-medium">{tool1.nameZh || tool1.name}</th>
                  <th className="px-6 py-4 text-left text-sm font-medium">{tool2.nameZh || tool2.name}</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="px-6 py-4 text-sm font-medium">类型</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{tool1.category}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{tool2.category}</td>
                </tr>
                <tr className="border-b">
                  <td className="px-6 py-4 text-sm font-medium">定价</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{tool1.pricingZh || tool1.pricing || '未知'}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{tool2.pricingZh || tool2.pricing || '未知'}</td>
                </tr>
                <tr className="border-b">
                  <td className="px-6 py-4 text-sm font-medium">评分</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                      {tool1.rating || '4.0'}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                      {tool2.rating || '4.0'}
                    </div>
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="px-6 py-4 text-sm font-medium">标签</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex flex-wrap gap-1">
                      {tool1.tags?.slice(0, 3).map((tag) => (
                        <span key={tag} className="tag-pill text-xs">{tag}</span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex flex-wrap gap-1">
                      {tool2.tags?.slice(0, 3).map((tag) => (
                        <span key={tag} className="tag-pill text-xs">{tag}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  )
}
