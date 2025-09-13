# DeepResearcher - AI驱动的智能试卷生成系统

🎯 **基于LangGraph的全栈AI研究和试卷生成系统**

这是一个集成了深度研究、智能试卷生成、学习笔记制作等功能的全栈应用。系统使用React前端和LangGraph后端，能够进行多轮智能研究，动态生成搜索查询，并基于研究结果生成专业的试卷和学习材料。

> **Note**: This project has been migrated from Google Genai to support OpenAI compatible APIs. See [OPENAI_MIGRATION.md](backend/OPENAI_MIGRATION.md) for migration details.

<img src="./app.png" title="Gemini Fullstack LangGraph" alt="Gemini Fullstack LangGraph" width="90%">

## ✨ 核心功能

### 🔬 AI深度研究助手
- 💬 React前端 + LangGraph后端的全栈架构
- 🧠 基于LangGraph的高级研究和对话AI
- 🔍 使用OpenAI兼容模型动态生成搜索查询
- 🌐 集成研究能力（可扩展搜索API）
- 🤔 反思推理识别知识空白并优化搜索
- 📄 生成带引用来源的答案

### 📝 智能试卷生成系统
- 🎯 **多题型支持**：选择题、判断题、填空题、简答题、论述题、计算题、分析题、应用题
- 📊 **难度分级**：简单、中等、困难三个等级
- 🏫 **学段适配**：小学、初中、高中全覆盖
- 📚 **学科齐全**：数学、语文、英语、物理、化学、生物等
- 📄 **专业PDF**：双栏布局、LaTeX数学公式、中文字体支持
- 🧹 **清洁格式**：简化头部、标准化选项、专业外观
- 📋 **多版本输出**：试卷、答案、学习笔记三合一

### 📚 学习笔记生成
- 📖 **结构化内容**：主题概述、核心知识点、学习技巧、扩展知识
- 🎯 **智能分类**：重要程度标注（🔵基础/🟡重要/🔴核心）
- 💡 **技巧指导**：🧠记忆/💡理解/⚡应用/🎯解题四大类别
- 🌟 **扩展学习**：相关知识点关联和拓展内容

## Project Structure

The project is divided into two main directories:

-   `frontend/`: Contains the React application built with Vite.
-   `backend/`: Contains the LangGraph/FastAPI application, including the research agent logic.

## Getting Started: Development and Local Testing

Follow these steps to get the application running locally for development and testing.

**1. Prerequisites:**

-   Node.js and npm (or yarn/pnpm)
-   Python 3.11+
-   **OpenAI Compatible API**: The backend agent requires an OpenAI compatible API configuration.
    1.  Navigate to the `backend/` directory.
    2.  Create a file named `.env` by copying the `backend/.env.example` file.
    3.  Open the `.env` file and configure your API settings:
        ```bash
        OPENAI_API_KEY=your_api_key_here
        OPENAI_BASE_URL=https://api.openai.com/v1  # or your custom endpoint
        OPENAI_MODEL=gpt-4o  # or your preferred model
        ```

**2. Install Dependencies:**

**Backend:**

```bash
cd backend
pip install .
```

**Frontend:**

```bash
cd frontend
npm install
```

**3. Test Configuration (Optional):**

Test your OpenAI compatible API configuration:

```bash
cd backend
python test_openai_config.py
```

**4. Run Development Servers:**

**快速启动 (推荐):**

```bash
./start_dev.sh
```

这将启动后端和前端开发服务器。访问 `http://localhost:5173` 使用应用。

**停止服务:**

```bash
./stop_dev.sh
```

**手动启动 (可选):**

```bash
make dev
```

_或者分别启动服务：后端在 `backend/` 目录运行 `langgraph dev`，前端在 `frontend/` 目录运行 `npm run dev`。_

**功能访问:**
- 🔬 研究助手: `http://localhost:5173/` 
- 📝 试卷生成器: `http://localhost:5173/exam`

## 🎯 试卷生成演示

### 快速生成示例
```
输入参数：
- 学科：数学
- 学段：初中  
- 主题：二次函数
- 题型：选择题 + 计算题
- 难度：中等
- 数量：15题

输出结果：
✅ 专业格式PDF试卷
✅ 详细解答PDF
✅ 学习笔记PDF
```

### 格式特性展示
```
修复前：
1. 0.6 + 0.4 = ? (2分)
A. A) 1.0    ← 重复标号问题
B. B) 0.10
C. C) 0.2

修复后：
1. 0.6 + 0.4 = ? (2分)  
A. 1.0       ← 清洁标准格式
B. 0.10
C. 0.2
```

## 🧪 功能测试

```bash
cd backend

# 完整功能测试
python test_complete_generation.py

# 清洁格式测试  
python test_clean_format.py

# 数学公式测试
python test_latex_math.py

# 双栏布局测试
python test_two_column_layout.py

# 中文字体测试
python test_font_simple.py
```

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

<img src="./agent.png" title="Agent Flow" alt="Agent Flow" width="50%">

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using an OpenAI compatible model.
2.  **Research:** For each query, it uses the configured model to generate research content (extensible with search APIs).
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the research results to determine if the information is sufficient or if there are knowledge gaps.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer with citations.

## CLI Example

For quick one-off questions you can execute the agent from the command line. The
script `backend/examples/cli_research.py` runs the LangGraph agent and prints the
final answer:

```bash
cd backend
python examples/cli_research.py "What are the latest trends in renewable energy?"
```


## Deployment

In production, the backend server serves the optimized static frontend build. LangGraph requires a Redis instance and a Postgres database. Redis is used as a pub-sub broker to enable streaming real time output from background runs. Postgres is used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics. For more details on how to deploy the backend server, take a look at the [LangGraph Documentation](https://langchain-ai.github.io/langgraph/concepts/deployment_options/). Below is an example of how to build a Docker image that includes the optimized frontend build and the backend server and run it via `docker-compose`.

_Note: For the docker-compose.yml example you need a LangSmith API key, you can get one from [LangSmith](https://smith.langchain.com/settings)._

_Note: If you are not running the docker-compose.yml example or exposing the backend server to the public internet, you should update the `apiUrl` in the `frontend/src/App.tsx` file to your host. Currently the `apiUrl` is set to `http://localhost:8123` for docker-compose or `http://localhost:2024` for development._

**1. Build the Docker Image:**

   Run the following command from the **project root directory**:
   ```bash
   docker build -t openai-fullstack-langgraph -f Dockerfile .
   ```
**2. Run the Production Server:**

   ```bash
   OPENAI_API_KEY=<your_openai_api_key> OPENAI_BASE_URL=<your_base_url> OPENAI_MODEL=<your_model> LANGSMITH_API_KEY=<your_langsmith_api_key> docker-compose up
   ```

Open your browser and navigate to `http://localhost:8123/app/` to see the application. The API will be available at `http://localhost:8123`.

## 📚 完整文档

- 📖 **[项目完整介绍](PROJECT_OVERVIEW.md)** - 详细的功能特性、技术架构、部署指南
- 🚀 **[快速入门指南](QUICK_START_GUIDE.md)** - 5分钟上手，功能体验，问题解决
- 🆚 **[功能特性对比](FEATURES_COMPARISON.md)** - 与传统方法的全面对比分析
- 🧹 **[清洁格式指南](CLEAN_FORMAT_GUIDE.md)** - 试卷格式优化和问题修复
- 📐 **[双栏布局指南](TWO_COLUMN_LAYOUT_GUIDE.md)** - 专业布局设计详解
- 🔢 **[LaTeX数学指南](LATEX_MATH_GUIDE.md)** - 数学公式渲染支持
- 📝 **[学习笔记指南](STUDY_NOTES_GUIDE.md)** - 智能笔记生成功能

## 🛠️ 技术栈

### 前端技术
- **[React](https://reactjs.org/)** + **[Vite](https://vitejs.dev/)** - 现代化前端框架
- **[TypeScript](https://www.typescriptlang.org/)** - 类型安全的JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** - 实用优先的CSS框架
- **[Shadcn UI](https://ui.shadcn.com/)** - 高质量组件库

### 后端技术  
- **[LangGraph](https://github.com/langchain-ai/langgraph)** - AI工作流编排框架
- **[FastAPI](https://fastapi.tiangolo.com/)** - 高性能Python Web框架
- **[ReportLab](https://www.reportlab.com/)** - 专业PDF生成库
- **[OpenAI API](https://platform.openai.com/docs/api-reference)** - GPT-4驱动的AI服务

### 核心特性
- 🤖 **AI驱动** - GPT-4提供智能生成能力
- 📄 **专业PDF** - LaTeX数学公式 + 中文字体支持  
- 🎨 **双栏布局** - 40%空间利用率提升
- 🧹 **清洁格式** - 自动修复选项标号问题
- 🔍 **深度研究** - 多轮反思优化内容质量

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details. 
