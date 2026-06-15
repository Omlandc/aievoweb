# 🤖 Kimi 协同工作流

## 分工模型

| 角色 | 负责 | 工具 |
|------|------|------|
| **我（Kimi Claw）** | 任务调度、文件操作、网站运维、RSS/数据流 | OpenClaw 工具链 |
| **Kimi Code** | 代码生成、游戏开发、复杂逻辑重写、代码审查 | `kimi -p` CLI |

## 调用方式

```bash
# 直接调用（非交互模式）
~/.local/share/uv/tools/kimi-cli/bin/kimi -p "你的任务描述"

# 带文件输入
echo "代码内容" | ~/.local/share/uv/tools/kimi-cli/bin/kimi -p "重构这段代码"
```

## 典型工作流

### 1. 游戏开发
```
我：用户要新游戏 → 写需求文档 → 调用 Kimi 生成代码 → 保存到 games/ → 部署
```

### 2. 代码审查
```
我：读取文件 → 调用 Kimi "审查这段代码的bug" → 获取结果 → 修复 → 推送
```

### 3. 批量翻译
```
我：读取 RSS 数据 → 调用 Kimi "翻译这些标题" → 保存双语数据 → 部署
```

## 缓存策略

1. **Kimi 输出先写临时文件**：`/tmp/kimi-output-{timestamp}.txt`
2. **我审查后确认**：满意才写入正式文件
3. **失败回退**：Kimi 超时/失败时，使用备用方案（如 MyMemory 翻译）

## 协同脚本

### `scripts/kimi-helper.sh`
封装 Kimi 调用，带超时和重试：

```bash
#!/bin/bash
# Kimi 协同助手 - 带超时保护

KIMI="/root/.local/share/uv/tools/kimi-cli/bin/kimi"
PROMPT="$1"
TIMEOUT="${2:-60}"

timeout $TIMEOUT $KIMI -p "$PROMPT" 2>/dev/null
```

### `scripts/kimi-game-gen.sh`
游戏生成专用：

```bash
#!/bin/bash
# 生成新游戏

GAME_NAME="$1"
GAME_TYPE="$2"  # snake, tetris, etc.

PROMPT="创建一个完整的 HTML5 ${GAME_TYPE} 游戏，文件名为 ${GAME_NAME}.html。
要求：
1. 纯前端，单文件
2. 响应式设计
3. 键盘控制
4. 计分系统
5. 浅色主题（白色背景）
6. 包含游戏说明

输出完整 HTML 代码。"

~/.local/share/uv/tools/kimi-cli/bin/kimi -p "$PROMPT" > "games/${GAME_NAME}.html"
```

## 任务队列

用文件 `/tmp/kimi-task-queue.json` 记录待办：

```json
[
  {"id": "1", "type": "game", "name": "tetris", "status": "pending"},
  {"id": "2", "type": "review", "file": "index.html", "status": "pending"}
]
```

Cron 每小时检查队列并执行。

## 已验证能力

- ✅ `kimi -p "翻译..."` - 文本翻译
- ✅ `kimi -p "生成代码..."` - 代码生成
- ✅ `kimi -p "审查这段代码..."` - 代码审查
- ❌ ACP 模式（需配对 Gateway）

## 注意事项

1. **超时**：Kimi 响应约 5-30 秒，复杂任务可能更久
2. **Token 消耗**：每次调用消耗 Kimi 套餐额度
3. **并发限制**：避免同时启动多个 Kimi 进程
4. **输出清理**：Kimi 会输出推理过程，需过滤提取实际结果

## 今日任务

- [x] 验证 Kimi CLI 可用
- [ ] 创建 `kimi-helper.sh` 封装脚本
- [ ] 测试游戏生成工作流（明天打砖块）
- [ ] 建立任务队列机制
