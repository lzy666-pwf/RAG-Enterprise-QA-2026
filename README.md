# RAG企业内部知识库问答系统

基于LangChain的RAG（检索增强生成）企业内部知识库智能问答平台，支持多轮对话、会话管理、文档管理、数据统计等企业级功能。

## 项目简介

本系统是一个功能完善的企业内部知识库问答平台，基于 DeepSeek 大语言模型 + 阿里通义千问 Embedding + Chroma 向量数据库构建 RAG 检索增强流程，具有以下核心特点：

### RAG 核心能力
- **RAG 检索增强生成**：从企业知识库中智能检索相关内容，结合大模型生成准确答案
- **查询扩展**：DeepSeek LLM 自动生成 2-3 个查询变体，显著提升检索召回率
- **多格式文档解析**：支持 TXT、PDF、DOCX、DOC 格式，自动分块（每块约500字符，50字符重叠）
- **向量嵌入入库**：阿里通义千问 `text-embedding-v3` 模型生成文本向量，批量存入 Chroma 向量数据库
- **参考来源展示**：回答附带相关文档片段及相似度分数，可溯源可验证

### 对话体验
- **SSE 流式输出**：AI 回答逐 token 实时流式返回，打字机效果，体验流畅
- **多轮对话**：支持上下文连续对话，自动携带最近 3-6 轮对话历史，理解更准确
- **会话管理**：创建、删除、重命名对话会话，每个会话独立上下文，互不干扰
- **问答历史**：完整记录用户问题、AI 回答、参考来源，随时回顾
- **快捷问题**：首页预设示例问题，一键体验

### 用户与权限
- **用户角色**：区分管理员与普通用户，权限分明，操作可控
- **JWT 认证**：安全的 Token 认证机制，前端路由守卫，Token 过期自动跳转登录
- **个人中心**：修改密码，管理个人文档和问答记录

### 管理后台
- **数据概览**：用户总数、文档总数、问答总数、入库状态实时统计
- **今日统计**：当日新增用户、文档、问答数量看板
- **问答趋势图**：近 7 天问答数量折线图
- **用户分布图**：管理员 / 普通用户角色分布饼图
- **问题关键词**：高频问题关键词 Top15 柱状图，洞察用户关注点
- **文档使用频率**：文档被查询次数 Top10 柱状图
- **用户管理**：查看、搜索、修改角色、删除用户
- **文档管理**：查看所有文档、状态、上传人，支持删除
- **问答记录**：查看所有用户问答详情
- **向量库管理**：查看集合名称、向量数量，支持一键清空向量库

## 项目截图

### 智能问答
基于 RAG 技术从企业知识库中检索相关内容，由大模型生成准确答案。

![智能问答](docs/images/duihua.png)

### 文档管理
支持上传 TXT、PDF、DOCX 文档，自动解析切片并写入 Chroma 向量数据库。

![文档管理](docs/images/wendang.png)

## 技术栈

### 后端
- Python 3.10+
- Flask 3.0+ Web 框架
- LangChain RAG 框架
- SQLAlchemy ORM
- Chroma 向量数据库（持久化存储）
- MySQL 8.0 关系型数据库
- DeepSeek API (`deepseek-chat` 大语言模型)
- 阿里通义千问 API (`text-embedding-v3` 文本向量嵌入)
- PyPDF2 / python-docx 文档解析
- PyJWT 身份认证
- SSE (Server-Sent Events) 流式输出

### 前端
- Vue 3.4+ (Composition API)
- Vite 5.0+ 构建工具
- Element Plus 企业级 UI 组件库
- ECharts 5 数据可视化
- Pinia 状态管理
- Vue Router 4 路由管理
- Axios HTTP 请求封装（含 Token 自动附加）

### 部署
- Docker & Docker Compose

## 项目结构

```
enterprise-qa/
├── backend/                    # 后端项目
│   ├── app/
│   │   ├── api/              # API路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务逻辑
│   │   └── utils/            # 工具函数
│   ├── config/               # 配置文件
│   ├── migrations/           # 数据库迁移
│   │   └── init_database.sql # 建表SQL
│   ├── requirements.txt       # Python依赖
│   ├── run.py               # 应用入口
│   └── .env.example         # 环境变量示例
│
├── frontend/                   # 前端项目
│   ├── src/
│   │   ├── api/             # API调用
│   │   ├── components/       # 组件
│   │   ├── router/          # 路由
│   │   ├── stores/          # 状态管理
│   │   └── views/           # 页面
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml         # Docker编排配置
└── README.md                 # 项目说明
```

## 快速开始

### 1. 环境准备

- Python 3.10+
- Node.js 18+
- MySQL 8.0 (或使用Docker)
- Docker (可选)

### 2. 配置环境变量

```bash
# 进入后端目录
cd backend

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，填入实际配置
```

主要配置项说明：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3308
DB_USER=root
DB_PASSWORD=123456
DB_NAME=db_enterprise_qa

# DeepSeek API（LLM）
DEEPSEEK_API_KEY=your_api_key

# 阿里通义千问（Embedding）
QWEN_API_KEY=your_api_key
```

### 3. 初始化数据库

#### 使用Docker（推荐）

```bash
# 启动MySQL服务
docker-compose up -d mysql

# 查看日志确认启动成功
docker-compose logs -f mysql
```

#### 手动执行SQL

```bash
# 登录MySQL
mysql -h localhost -P 3308 -u root -p

# 执行建表脚本
source migrations/init_database.sql
```

### 4. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 安装前端依赖

```bash
cd frontend

# 安装依赖
npm install
```

### 6. 启动服务

#### 开发环境

```bash
# 启动后端（后端目录）
cd backend
python run.py
# 服务运行在 http://localhost:5000

# 启动前端（新终端）
cd frontend
npm run dev
# 服务运行在 http://localhost:3000
```

#### 使用Docker启动全部服务

```bash
# 启动所有服务（MySQL + 后端 + 前端）
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 7. 访问应用

- 前端地址：http://localhost:3000
- 后端API：http://localhost:5000

## 演示账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 管理员 |
| zhangsan | 123456 | 普通用户 |
| lisi | 123456 | 普通用户 |

## 功能模块

### 普通用户
- 用户登录 / 注册（用户名 + 密码，JWT Token 认证）
- 智能问答（基于 RAG 检索增强生成，流式输出，打字机效果）
- 多轮对话（自动携带上下文历史，理解更准确）
- 会话管理（创建、删除、重命名对话会话）
- 问答历史（查看、继续对话、删除历史记录）
- 快捷问题（首页预设示例问题，一键体验）
- 文档上传（支持 TXT、PDF、DOCX、DOC，拖拽上传，单文件最大 16MB）
- 文档解析状态跟踪（待处理 / 已入库 / 入库失败 / 解析失败）
- 个人密码修改

### 管理员
- 管理后台首页（数据概览 + 今日统计）
- 问答趋势图（近 7 天折线图，ECharts 可视化）
- 用户分布图（管理员 / 普通用户饼图）
- 问题关键词 Top15 柱状图
- 文档使用频率 Top10 柱状图
- 用户管理（查看、搜索、修改角色、删除用户）
- 文档管理（查看所有文档、状态、上传人，删除文档）
- 问答记录（查看所有用户问答详情）
- 向量库状态查看（集合名称、向量数量、所有集合列表）
- 一键清空向量库

## API接口

### 认证接口
- `POST /api/auth/register` - 用户注册（用户名/邮箱/密码）
- `POST /api/auth/login` - 用户登录（返回 JWT Token）
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/password` - 修改密码（旧密码 + 新密码验证）
- `GET /api/stats` - 用户个人统计数据

### 文档接口
- `GET /api/documents` - 获取文档列表（支持分页 / 关键词搜索）
- `POST /api/documents/upload` - 上传文档（TXT/PDF/DOCX/DOC，自动解析分块入库）
- `GET /api/documents/:id` - 获取文档详情
- `DELETE /api/documents/:id` - 删除文档（同步删除向量数据）

### 问答接口
- `POST /api/chat` - 提交问答（非流式，返回完整回答 + 参考来源）
- `POST /api/chat/stream` - SSE 流式问答（实时逐 token 返回）
- `GET /api/chat/history` - 获取问答历史（分页）
- `GET /api/chat/:id` - 获取单条问答详情
- `DELETE /api/chat/:id` - 删除问答记录

### 会话接口
- `POST /api/sessions` - 创建新会话
- `GET /api/sessions` - 获取会话列表（按更新时间倒序）
- `GET /api/sessions/:id` - 获取会话详情及消息
- `PATCH /api/sessions/:id` - 更新会话标题
- `DELETE /api/sessions/:id` - 删除会话（级联删除消息）
- `GET /api/sessions/:id/messages` - 获取会话消息列表
- `POST /api/sessions/:id/messages` - 向会话追加消息

### 管理接口
- `GET /api/admin/stats` - 系统统计数据（用户/文档/问答总数等）
- `GET /api/admin/users` - 用户列表（支持搜索）
- `PUT /api/admin/users/:id` - 更新用户（修改角色）
- `DELETE /api/admin/users/:id` - 删除用户
- `GET /api/admin/documents` - 所有文档列表
- `GET /api/admin/chats` - 所有问答记录
- `GET /api/admin/vectors/status` - 向量库状态
- `POST /api/admin/vectors/clear` - 清空向量库

## 开发说明

### RAG 工作流程

```
用户提问 → 查询扩展（DeepSeek 生成变体）→ Chroma 向量检索 → 上下文组装 → LLM 生成回答 → SSE 流式返回
```

### 添加新的 API 接口

1. 在 `backend/app/api/` 目录下创建新的蓝图文件
2. 定义路由和处理函数
3. 在 `backend/app/api/__init__.py` 中导入注册

### 添加新的前端页面

1. 在 `frontend/src/views/` 下创建页面组件
2. 在 `frontend/src/router/index.js` 中添加路由配置
3. 在侧边栏菜单中添加入口

## 注意事项

1. **API 密钥安全**：生产环境中请勿将 API 密钥直接写在代码中，使用 `.env` 环境变量管理
2. **密码安全**：用户密码使用 MD5 加密存储，实际生产环境建议使用更安全的加密方式（如 bcrypt）
3. **文件上传**：生产环境需要配置文件存储服务（如 OSS、S3 等），当前版本文件存储在本地
4. **向量数据库**：Chroma 数据默认存储在本地 `backend/chroma_db` 目录，生产环境建议使用分布式部署
5. **多轮对话**：RAG 流程自动携带最近 3-6 轮对话历史，提升连续对话理解能力
6. **查询扩展**：检索前由 DeepSeek 生成多个查询变体，有效提升复杂问题的召回率

## 许可证

MIT License

## 技术支持

如有问题，请提交Issue。
