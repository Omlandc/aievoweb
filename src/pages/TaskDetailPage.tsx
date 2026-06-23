import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Wrench, Tag } from 'lucide-react'
import { tasks } from '@/data/tasks'
import { tools } from '@/data/tools'
import { ToolCard } from '@/components/ToolCard'

export function TaskDetailPage() {
  const { id } = useParams<{ id: string }>()
  const task = tasks.find(t => t.id === id)

  if (!task) {
    return (
      <div className="py-20 text-center">
        <p className="text-muted-foreground">任务未找到</p>
        <Link to="/tasks" className="text-primary hover:underline mt-4 inline-block">
          返回任务列表
        </Link>
      </div>
    )
  }

  // 匹配相关工具（简化匹配逻辑）
  const taskTools = tools.filter(t => {
    const taskTitle = task.title.toLowerCase()
    const toolName = (t.nameZh || t.name).toLowerCase()
    const toolDesc = (t.descriptionZh || t.description).toLowerCase()
    const toolTags = t.tags?.join(' ').toLowerCase() || ''
    
    return toolName.includes(taskTitle) || 
           toolDesc.includes(taskTitle) || 
           toolTags.includes(taskTitle) ||
           taskTitle.includes(toolName.split(' ')[0])
  }).slice(0, 12)

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto"
    >
      <Link to="/tasks" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="w-4 h-4" /> 返回任务列表
      </Link>

      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/30 to-primary/10 flex items-center justify-center">
            <Wrench className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">{task.title}</h1>
            <p className="text-muted-foreground">
              {task.description || `解决「${task.title}」任务的AI工具合集`}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2 mt-4">
          <span className="tag-pill">
            <Tag className="w-3 h-3 mr-1" />
            {task.toolCount} 个工具
          </span>
        </div>
      </div>

      {taskTools.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {taskTools.map((tool, i) => (
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
      ) : (
        <div className="text-center py-20 text-muted-foreground">
          <Wrench className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>该任务暂无匹配工具，我们正在扩充数据中</p>
        </div>
      )}
    </motion.div>
  )
}
