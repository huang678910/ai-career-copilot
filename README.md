# AI Career Copilot

全栈 AI 求职助手平台，涵盖 AI 简历助手、JD 分析、简历定制、AI 模拟面试和简历导出五大模块。

## 功能模块

| 模块 | 说明 |
|------|------|
| **AI 简历助手** | WebSocket 对话式引导构建简历，实时预览，支持导入简历继续完善 |
| **JD 分析** | 输入职位描述（最少5字符），AI 分析技术栈、关键词、难度评分、风险识别 |
| **简历定制** | 根据目标 JD 自动优化简历内容，突出匹配技能和量化成果 |
| **AI 模拟面试** | WebSocket 驱动的实时对话式 AI 面试，支持追问和深度评估 |
| **简历导出** | 一键导出 PDF/DOCX 格式简历，WeasyPrint 渲染，支持中文字体 |

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Next.js 14 (App Router) · React 18 · TypeScript · TailwindCSS · shadcn/ui · Zustand |
| **后端** | FastAPI · async SQLAlchemy 2.0 · Celery · Pydantic v2 |
| **AI** | DeepSeek API (OpenAI SDK 兼容) |
| **数据库** | PostgreSQL 16 + pgvector |
| **缓存/队列** | Redis 7 |
| **实时通信** | WebSocket |
| **PDF 导出** | WeasyPrint + python-docx |
| **认证** | JWT 双 Token (access + refresh) |
| **部署** | Docker Compose · Nginx · Gunicorn + Uvicorn |

## 架构

```
浏览器
  │
  ▼
Nginx (:80) ──┬── /api/*  ──►  Backend (:8000) ──► PostgreSQL (:5432)
               │                                         │
               ├── /ws/*   ──►  Backend (:8000) ──► DeepSeek API
               │                                         │
               └── /*      ──►  Frontend (:3000)        Redis (:6379)
                                                         │
                                                    Celery Worker
                                                    Celery Beat
```

## 快速开始

### 前置条件

- Docker Desktop
- DeepSeek API Key（注册地址：platform.deepseek.com）

### Docker 部署

```bash
# 1. 进入 docker 目录
cd docker

# 2. 配置环境变量（.env 文件已包含，只需确认 DEEPSEEK_API_KEY）
cat .env

# 3. 构建并启动
docker compose up -d --build

# 4. 访问
# 前端: http://localhost:3001
# Nginx: http://localhost:80
# 后端 API: http://localhost:8004/docs
```

### 本地开发

```bash
# 启动基础设施（PostgreSQL + Redis）
cd docker
docker compose up -d postgres redis

# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8004 --reload

# 前端
cd frontend
npm install
npm run dev -- -p 3001
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接 (async) | `postgresql+asyncpg://postgres:postgres@postgres:5432/career_copilot` |
| `REDIS_URL` | Redis 连接 | `redis://redis:6379/0` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `change-me-in-production` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | (必填) |
| `DEEPSEEK_BASE_URL` | AI API 地址 | `https://api.deepseek.com` |
| `CORS_ORIGINS` | 允许的跨域来源 | `http://localhost` |

## 项目结构

```
ai-career-copilot/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI 代理 (JD分析、简历助手、面试)
│   │   │   └── prompts/     # System prompt 文件
│   │   ├── api/v1/          # REST API 路由
│   │   ├── core/            # 配置、安全、限流
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 校验
│   │   ├── services/        # 业务逻辑
│   │   ├── tasks/           # Celery 异步任务
│   │   ├── utils/           # 工具函数（文档生成）
│   │   └── websocket/       # WebSocket 路由
│   ├── alembic/             # 数据库迁移
│   ├── tests/               # 测试
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router 页面
│   │   ├── components/      # React 组件
│   │   ├── stores/          # Zustand 状态管理
│   │   └── lib/             # 工具函数、API 客户端
│   ├── Dockerfile
│   └── package.json
├── docker/
│   ├── docker-compose.yml   # 容器编排
│   ├── nginx.conf            # Nginx 反向代理配置
│   └── .env                  # 环境变量
└── README.md
```
