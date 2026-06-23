import { Link } from 'react-router-dom'
import { Star, ExternalLink, Tag } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Tool } from '@/data/tools'

interface ToolCardProps {
  tool: Tool
  variant?: 'default' | 'compact' | 'featured'
}

export function ToolCard({ tool, variant = 'default' }: ToolCardProps) {
  const { id, name, nameZh, descriptionZh, description, category, tags, rating, link, url } = tool
  const toolLink = link || url || '#'
  const displayName = nameZh || name
  const displayDesc = descriptionZh || description

  if (variant === 'compact') {
    return (
      <Link
        to={`/tools/${id}`}
        className="flex items-center gap-3 p-3 rounded-lg border hover:border-primary/50 hover:bg-muted/50 transition-all group"
      >
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-lg flex-shrink-0">
          {name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm truncate group-hover:text-primary transition-colors">{displayName}</div>
          <div className="text-xs text-muted-foreground truncate">{displayDesc?.slice(0, 40)}...</div>
        </div>
        {rating && (
          <div className="flex items-center gap-0.5 text-xs">
            <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
            {rating}
          </div>
        )}
      </Link>
    )
  }

  return (
    <div className={cn(
      'rounded-xl border bg-card p-5 card-hover',
      variant === 'featured' && 'ring-1 ring-primary/20'
    )}>
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-xl font-bold text-primary flex-shrink-0">
          {name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-lg">
              <Link to={`/tools/${id}`} className="hover:text-primary transition-colors">
                {displayName}
              </Link>
            </h3>
            {rating && (
              <div className="flex items-center gap-1 text-sm">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span className="font-medium">{rating}</span>
              </div>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1 line-clamp-2">{displayDesc}</p>
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <span className="tag-pill">{category}</span>
            {tags?.slice(0, 3).map((tag) => (
              <span key={tag} className="tag-pill opacity-70">
                <Tag className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
          </div>
        </div>
        <a
          href={toolLink}
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg hover:bg-muted text-muted-foreground hover:text-primary transition-colors flex-shrink-0"
          onClick={(e) => e.stopPropagation()}
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  )
}
