import { Link } from 'react-router-dom'
import { Home, AlertTriangle } from 'lucide-react'

export function NotFoundPage() {
  return (
    <div className="py-20 px-4 text-center">
      <AlertTriangle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
      <h1 className="text-4xl font-bold mb-2">404</h1>
      <p className="text-muted-foreground mb-6">页面未找到</p>
      <Link
        to="/"
        className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
      >
        <Home className="w-4 h-4" />
        返回首页
      </Link>
    </div>
  )
}
