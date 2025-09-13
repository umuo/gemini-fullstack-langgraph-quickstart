#!/bin/bash

# 启动开发服务器脚本

echo "🚀 启动 DeepResearcher 开发环境..."

# 检查是否在项目根目录
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 检查后端环境配置
if [ ! -f "backend/.env" ]; then
    echo "⚠️  后端 .env 文件不存在，请先配置 OpenAI API"
    echo "   复制 backend/.env.example 到 backend/.env 并填入你的 API 配置"
    exit 1
fi

echo "📦 安装依赖..."

# 安装后端依赖
echo "  - 安装后端依赖..."
cd backend
pip install -e . > /dev/null 2>&1
cd ..

# 安装前端依赖
echo "  - 安装前端依赖..."
cd frontend
npm install > /dev/null 2>&1
cd ..

echo "🔧 启动服务..."

# 启动后端服务（后台运行）
echo "  - 启动后端服务 (http://localhost:2024)..."
cd backend
langgraph dev --port 2024 --allow-blocking > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端服务（后台运行）
echo "  - 启动前端服务 (http://localhost:5173)..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ 服务启动完成！"
echo ""
echo "🌐 访问地址："
echo "   前端应用: http://localhost:5173"
echo "   后端API:  http://localhost:2024"
echo ""
echo "📝 功能："
echo "   /        - 研究助手 (原有功能)"
echo "   /exam    - 试卷生成器 (新功能)"
echo ""
echo "📋 进程ID："
echo "   后端: $BACKEND_PID"
echo "   前端: $FRONTEND_PID"
echo ""
echo "🛑 停止服务: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 查看日志:"
echo "   后端: tail -f backend.log"
echo "   前端: tail -f frontend.log"

# 保存进程ID到文件
echo "$BACKEND_PID $FRONTEND_PID" > .dev_pids

echo ""
echo "按 Ctrl+C 停止所有服务..."

# 等待用户中断
trap 'echo ""; echo "🛑 停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .dev_pids backend.log frontend.log; echo "✅ 服务已停止"; exit 0' INT

# 保持脚本运行
while true; do
    sleep 1
done