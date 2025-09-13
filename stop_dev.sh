#!/bin/bash

# 停止开发服务器脚本

echo "🛑 停止 DeepResearcher 开发服务..."

# 读取进程ID
if [ -f ".dev_pids" ]; then
    PIDS=$(cat .dev_pids)
    echo "📋 停止进程: $PIDS"
    kill $PIDS 2>/dev/null
    rm -f .dev_pids
fi

# 清理日志文件
rm -f backend.log frontend.log

# 杀死可能残留的进程
pkill -f "langgraph dev" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "vite" 2>/dev/null

echo "✅ 所有服务已停止"