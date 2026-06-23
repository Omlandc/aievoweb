import { motion } from 'framer-motion'
import { MessageSquare, Calendar, ExternalLink } from 'lucide-react'
import { tweets } from '@/data/tweets'

export function TweetsPage() {
  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-bold">AI动态</h1>
        </div>
        <p className="text-muted-foreground">来自全球科技媒体的最新AI动态</p>
      </div>

      <div className="space-y-4">
        {tweets.map((tweet, i) => (
          <motion.div
            key={tweet.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03, duration: 0.3 }}
            className="p-5 rounded-xl border bg-card hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className="tag-pill text-primary bg-primary/10">
                {tweet.source || 'AI动态'}
              </span>
              {tweet.category && (
                <span className="tag-pill">
                  {tweet.category}
                </span>
              )}
              {tweet.date && (
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {tweet.date}
                </span>
              )}
            </div>
            
            <p className="text-sm leading-relaxed whitespace-pre-line">
              {tweet.content}
            </p>
            
            {tweet.link && (
              <a
                href={tweet.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-3"
              >
                <ExternalLink className="w-3 h-3" />
                阅读原文
              </a>
            )}
          </motion.div>
        ))}
      </div>

      {tweets.length === 0 && (
        <div className="text-center py-20 text-muted-foreground">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>暂无动态</p>
        </div>
      )}
    </div>
  )
}
