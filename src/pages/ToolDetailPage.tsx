import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Star, ExternalLink, ArrowLeft, Tag, Check, X, Zap, ThumbsUp } from 'lucide-react'
import { tools } from '@/data/tools'
import { ToolCard } from '@/components/ToolCard'

export function ToolDetailPage() {
  const { id } = useParams<{ id: string }>()
  const tool = tools.find(t => t.id === id)

  if (!tool) {
    return (
      <div className="py-20 text-center">
        <p className="text-muted-foreground">工具未找到</p>
        <Link to="/tools" className="text-primary hover:underline mt-4 inline-block">
          返回工具列表
        </Link>
      </div>
    )
  }

  const displayName = tool.nameZh || tool.name
  const displayDesc = tool.descriptionZh || tool.description
  const toolLink = tool.link || tool.url || '#'

  // 相关工具
  const relatedTools = tools
    .filter(t => t.id !== tool.id && t.category === tool.category)
    .slice(0, 5)

  // 替代工具
  const alternativeTools = tools
    .filter(t => t.id !== tool.id && t.tags?.some(tag => tool.tags?.includes(tag)))
    .slice(0, 3)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto"
    >
      {/* Back */}
      <Link to="/tools" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="w-4 h-4" /> 返回工具列表
      </Link>

      {/* Tool Header */}
      <div className="flex flex-col md:flex-row gap-6 mb-8">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center text-3xl font-bold text-primary flex-shrink-0">
          {tool.name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-bold">{displayName}</h1>
            {tool.rating && (
              <div className="flex items-center gap-1 bg-amber-50 dark:bg-amber-950/30 px-3 py-1 rounded-full">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span className="font-semibold">{tool.rating}</span>
              </div>
            )}
          </div>
          <p className="text-muted-foreground mt-2">{displayDesc}</p>
          <div className="flex items-center gap-2 mt-4 flex-wrap">
            <span className="tag-pill">{tool.category}</span>
            {tool.tags?.map((tag) => (
              <span key={tag} className="tag-pill">
                <Tag className="w-3 h-3 mr-1" />{tag}
              </span>
            ))}
          </div>
        </div>
        <a
          href={toolLink}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors flex-shrink-0 h-fit"
        >
          访问官网 <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="rounded-xl border bg-card p-6">
            <h2 className="text-lg font-semibold mb-4">工具详情</h2>
            <p className="text-muted-foreground leading-relaxed">{displayDesc}</p>
            
            {tool.useCases && tool.useCases.length > 0 && (
              <div className="mt-4">
                <h3 className="font-medium mb-2">适用场景</h3>
                <ul className="space-y-1">
                  {tool.useCases.map((useCase, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <Zap className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                      {useCase}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Pros & Cons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {tool.pros && tool.pros.length > 0 && (
              <div className="rounded-xl border bg-card p-6">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <ThumbsUp className="w-4 h-4 text-green-500" /> 优点
                </h3>
                <ul className="space-y-2">
                  {tool.pros.map((pro, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {pro}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {tool.cons && tool.cons.length > 0 && (
              <div className="rounded-xl border bg-card p-6">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <X className="w-4 h-4 text-red-500" /> 缺点
                </h3>
                <ul className="space-y-2">
                  {tool.cons.map((con, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <X className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                      {con}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Sidebar */}
        <div className="space-y-6">
          {/* Pricing */}
          {(tool.pricing || tool.pricingZh) && (
            <div className="rounded-xl border bg-card p-6">
              <h3 className="font-semibold mb-2">定价</h3>
              <p className="text-sm text-muted-foreground">{tool.pricingZh || tool.pricing}</p>
            </div>
          )}

          {/* Related Tools */}
          {relatedTools.length > 0 && (
            <div className="rounded-xl border bg-card p-6">
              <h3 className="font-semibold mb-4">同类工具</h3>
              <div className="space-y-3">
                {relatedTools.map((t) => (
                  <ToolCard key={t.id} tool={t} variant="compact" />
                ))}
              </div>
            </div>
          )}

          {/* Alternatives */}
          {alternativeTools.length > 0 && (
            <div className="rounded-xl border bg-card p-6">
              <h3 className="font-semibold mb-4">替代方案</h3>
              <div className="space-y-3">
                {alternativeTools.map((t) => (
                  <ToolCard key={t.id} tool={t} variant="compact" />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
