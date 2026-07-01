# RAG企业内部知识库问答系统 - 项目规范

## 1. 项目概述

### 项目名称
RAG企业内部知识库问答系统

### 项目简介
基于LangChain框架开发的RAG（检索增强生成）企业内部知识库问答系统，支持用户上传文档、智能问答、管理员后台统计等功能。

### 目标用户
- 普通员工：查询企业内部知识、文档问答
- 系统管理员：管理用户、知识库、数据统计

---

## 2. 技术栈

### 后端
- Python 3.10+
- Flask 3.0+
- LangChain 0.1+
- Chroma向量数据库
- MySQL 8.0 (端口3308)
- DeepSeek API (LLM)
- 阿里通义千问API (Embeddings)

### 前端
- Vue 3.4+
- Vite 5.0+
- Element Plus
- ECharts (数据可视化)
- Pinia (状态管理)
- Vue Router 4

### 数据库
- MySQL 8.0
- 数据库名：db_enterprise_qa
- 端口：3308

---

## 3. 功能模块

### 3.1 用户认证模块
- 用户注册（普通用户）
- 用户登录（支持管理员/普通用户）
- 密码MD5加密存储
- JWT Token认证
- 角色区分（admin/user）

### 3.2 知识库管理模块（管理员）
- 文档上传（TXT、PDF、DOCX）
- 文档列表管理
- 文档删除
- 文档内容解析入库Chroma

### 3.3 问答模块
- 智能问答（基于RAG）
- 历史记录查询
- 相似问题推荐

### 3.4 管理后台
- 数据统计仪表盘
- 用户管理
- 文档管理
- 问答记录统计

---

## 4. 数据库设计

### 用户表（users）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键自增 |
| username | VARCHAR(50) | 用户名唯一 |
| password | VARCHAR(64) | MD5加密密码 |
| email | VARCHAR(100) | 邮箱 |
| role | ENUM('admin','user') | 角色 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 文档表（documents）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键自增 |
| title | VARCHAR(255) | 文档标题 |
| file_path | VARCHAR(500) | 文件存储路径 |
| file_type | VARCHAR(20) | 文件类型 |
| content | TEXT | 文档内容摘要 |
| user_id | INT | 上传用户ID |
| status | TINYINT | 状态(0未处理,1已入库) |
| created_at | DATETIME | 创建时间 |

### 问答记录表（chat_history）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键自增 |
| user_id | INT | 提问用户ID |
| question | TEXT | 问题内容 |
| answer | TEXT | 回答内容 |
| sources | TEXT | 参考来源(JSON) |
| created_at | DATETIME | 创建时间 |

---

## 5. API接口设计

### 认证接口
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- GET /api/auth/me - 获取当前用户信息

### 文档接口
- GET /api/documents - 获取文档列表
- POST /api/documents/upload - 上传文档
- DELETE /api/documents/{id} - 删除文档

### 问答接口
- POST /api/chat - 提交问答
- GET /api/chat/history - 获取问答历史

### 管理接口
- GET /api/admin/stats - 获取统计数据
- GET /api/admin/users - 用户列表
- GET /api/admin/documents - 文档列表

---

## 6. 前端页面

### 登录/注册页
- 黄白配色主题
- 表单验证
- 记住登录状态

### 用户首页
- 问答入口
- 历史记录
- 个人中心

### 管理后台
- 仪表盘统计
- 用户管理
- 文档管理
- 问答统计

---

## 7. 环境变量

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3308
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=db_enterprise_qa

# DeepSeek API
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_API_URL=https://api.deeepseek.com/v1

# 阿里通义千问 Embedding
QWENTY_API_KEY=your_api_key
QWENTY_API_URL=https://dashscope.aliyuncs.com/api/v1

# JWT密钥
JWT_SECRET=your_jwt_secret_key
```

---

## 8. 项目结构

```
backend/
├── app/
│   ├── api/          # API路由
│   ├── models/       # 数据模型
│   ├── services/     # 业务逻辑
│   └── utils/        # 工具函数
├── config/           # 配置文件
├── migrations/       # 数据库迁移
└── requirements.txt

frontend/
├── src/
│   ├── api/          # API调用
│   ├── components/   # 组件
│   ├── router/       # 路由
│   ├── stores/       # 状态管理
│   └── views/        # 页面
├── public/
└── package.json
```
