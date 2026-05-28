全栈 AI 求职助手平台，涵盖 AI 简历助手、JD 分析、简历定制、AI 模拟面试和简历导出五大模块。

## 功能模块

| 模块 | 说明 |
|------|------|
| **AI 简历助手** | AI 对话式引导构建简历，实时 WebSocket 预览，数据自动提取与更新，支持导入简历继续完善 |
| **JD 分析** | 输入职位描述，AI 分析关键技能要求、软实力需求和薪资范围 |
| **简历定制** | 根据目标 JD 自动优化简历内容，突出匹配技能和量化成果 |
| **AI 模拟面试** | WebSocket 驱动的实时对话式 AI 面试，支持追问和深度评估 |
| **简历导出** | 一键导出 PDF/DOCX 格式简历，支持多种排版模板 |

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Next.js 14 (App Router) · React 18 · TypeScript · TailwindCSS · shadcn/ui · Zustand · TanStack Query |
| **后端** | FastAPI · async SQLAlchemy 2.0 · Celery · Pydantic v2 |
| **AI** | DeepSeek API (OpenAI SDK 兼容) |
| **数据库** | PostgreSQL 16 |
| **缓存/队列** | Redis |
| **实时通信** | WebSocket |
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

- Docker & Docker Compose
- DeepSeek API Key（注册地址：platform.deepseek.com）

### Docker 部署（推荐）

```bash
# 1. 进入 docker 目录
cd docker

# 2. 配置环境变量
cat > .env << 'EOF'
JWT_SECRET_KEY=<随机生成至少32位字符串>
DEEPSEEK_API_KEY=<你的DeepSeek API Key>
CORS_ORIGINS=http://localhost
EOF

# 3. 构建并启动
docker-compose up -d --build

# 4. 访问
open http://localhost
```

### 本地开发

```bash
# 启动基础设施（PostgreSQL + Redis）
docker-compose -f docker/docker-compose.yml up -d postgres redis

# 后端
cd backend
cp .env.example .env  # 编辑 .env 填入实际配置
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# 前端
cd frontend
npm install
npm run dev
```

前端: `http://localhost:3000` · 后端: `http://localhost:8004`

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接字符串 (async) | `postgresql+asyncpg://postgres:postgres@localhost:5432/career_copilot` |
| `REDIS_URL` | Redis 连接字符串 | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `change-me` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 有效期 | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 有效期 | `7` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | (必填) |
| `DEEPSEEK_BASE_URL` | AI API 地址 | `https://api.deepseek.com` |
| `CORS_ORIGINS` | 允许的跨域来源 (逗号分隔) | `http://localhost:3000` |
| `APP_ENV` | 运行环境 (`development` / `production`) | `development` |

## API 文档

启动后端后访问 `http://localhost:8000/docs` 查看自动生成的 Swagger 文档。

### 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 |
| POST | `/api/v1/auth/login` | 用户登录 |
| POST | `/api/v1/auth/refresh` | 刷新 Token |
| GET | `/api/v1/resumes` | 获取简历列表 |
| POST | `/api/v1/resumes` | 创建简历 |
| GET | `/api/v1/resumes/{id}` | 获取简历详情 |
| POST | `/api/v1/resumes/import` | 导入简历文件 |
| POST | `/api/v1/jd-analysis` | 分析职位描述 |
| POST | `/api/v1/tailor` | 定制简历 |
| POST | `/api/v1/export/resume/{id}/{format}/sync` | 导出简历 (PDF/DOCX) |
| WS | `/ws/resume/{id}` | AI 简历助手 WebSocket |
| WS | `/ws/interview/{id}` | 模拟面试 WebSocket |

## 项目结构

```
ai-career-copilot/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI 代理、Prompt
│   │   │   └── prompts/     # System prompt 文件
│   │   ├── api/v1/          # REST API 路由
│   │   ├── core/            # 配置、安全、异常
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 校验
│   │   ├── services/        # 业务逻辑
│   │   ├── tasks/           # Celery 异步任务
│   │   ├── utils/           # 工具函数（含文档生成）
│   │   └── websocket/       # WebSocket 路由
│   ├── alembic/             # 数据库迁移
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router 页面
│   │   ├── components/      # React 组件
│   │   ├── stores/          # Zustand 状态管理
│   │   └── lib/             # 工具函数、API 客户端
│   └── package.json
├── docker/
│   ├── docker-compose.yml       # 开发环境
│   ├── docker-compose.prod.yml  # 生产环境
│   ├── nginx.conf               # 开发 Nginx 配置
│   └── nginx.prod.conf          # 生产 Nginx 配置 (含 HTTPS)
└── README.md
```

## 生产部署

```bash
# 1. 进入 docker 目录，使用生产配置
cd docker

# 2. 编辑 .env，填入生产环境变量（特别是 JWT_SECRET_KEY 和 CORS_ORIGINS）

# 3. 修改 nginx.prod.conf 中的域名 (搜索 your-domain.com)

# 4. 申请 SSL 证书
certbot certonly --standalone -d your-domain.com

# 5. 启动
docker-compose -f docker-compose.prod.yml up -d --build
```

## AI 简历助手设计

采用**无状态全量提取**架构，彻底消除传统状态机带来的阶段不同步、数据丢失等问题。

### 两阶段处理流程

```
用户消息
  │
  ├─ Phase 1: 对话生成（流式推送至前端）
  │     AI 以职业规划师身份自然引导对话
  │     覆盖基本信息、求职意向、教育、技能、项目、工作经历
  │
  └─ Phase 2: 全量数据提取（json_object 模式，temperature=0.1）
        输入: 完整对话历史 + 当前完整简历数据
        输出: 全部 6 个章节的 JSON
        └─ 替换预览面板数据（复制旧值 + 更新新值）
```

### 核心设计原则

- **无状态机**：不跟踪"当前章节"——用户可随时讨论任何话题，AI 始终输出完整简历状态
- **数据即状态**：进度条完全从 `collected_data` 派生，不依赖额外的状态变量
- **全量替换**：Phase 2 输出完整快照（复制旧值 + 更新新值），保证预览面板数据始终完整一致
- **AI 看到现有数据**：提取 prompt 传入当前完整简历数据，AI 知道哪些字段已填充，只更新用户提及的变更
- **高质量提取**：`response_format={"type": "json_object"}` + `temperature=0.1` 确保 JSON 输出可靠

