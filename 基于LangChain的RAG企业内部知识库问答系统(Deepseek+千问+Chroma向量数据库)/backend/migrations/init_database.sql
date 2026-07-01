-- ============================================
-- RAG企业内部知识库问答系统 - 数据库建表脚本
-- 数据库: db_enterprise_qa
-- MySQL 8.0+
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS db_enterprise_qa
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_enterprise_qa;

-- ============================================
-- 用户表（users）
-- 存储系统用户信息，包括管理员和普通用户
-- ============================================
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID，主键自增',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名，唯一约束',
    password VARCHAR(64) NOT NULL COMMENT 'MD5加密后的密码',
    email VARCHAR(100) COMMENT '邮箱地址',
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user' COMMENT '用户角色：admin管理员，user普通用户',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户信息表';

-- ============================================
-- 文档表（documents）
-- 存储上传的文档信息，包括标题、路径、内容摘要等
-- ============================================
DROP TABLE IF EXISTS documents;

CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文档ID，主键自增',
    title VARCHAR(255) NOT NULL COMMENT '文档标题',
    file_path VARCHAR(500) COMMENT '文件存储路径',
    file_type VARCHAR(20) COMMENT '文件类型：txt/pdf/docx/doc',
    content TEXT COMMENT '文档内容摘要（最多5000字符）',
    user_id INT NOT NULL COMMENT '上传用户ID',
    status TINYINT DEFAULT 0 COMMENT '状态：0待处理，1已入库向量数据库',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档信息表';

-- ============================================
-- 问答记录表（chat_history）
-- 存储用户的问答历史，包括问题、回答和参考来源
-- ============================================
DROP TABLE IF EXISTS chat_history;

CREATE TABLE chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID，主键自增',
    user_id INT NOT NULL COMMENT '提问用户ID',
    question TEXT NOT NULL COMMENT '用户问题内容',
    answer TEXT COMMENT 'AI生成的回答内容',
    sources TEXT COMMENT '参考来源，JSON格式存储',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问答历史记录表';

-- ============================================
-- 插入测试数据
-- 密码说明：123456 的MD5值为 e10adc3949ba59abbe56e057f20f883e
-- ============================================

-- 插入管理员用户
INSERT INTO users (username, password, email, role) VALUES
    ('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin@company.com', 'admin'),
    ('zhangsan', 'e10adc3949ba59abbe56e057f20f883e', 'zhangsan@company.com', 'user'),
    ('lisi', 'e10adc3949ba59abbe56e057f20f883e', 'lisi@company.com', 'user'),
    ('wangwu', 'e10adc3949ba59abbe56e057f20f883e', 'wangwu@company.com', 'user');

-- 插入测试文档
INSERT INTO documents (title, file_path, file_type, content, user_id, status) VALUES
    ('公司介绍', '/uploads/1/company_intro.txt', 'txt', 'ABC科技有限公司成立于2010年，专注于人工智能和大数据领域。公司总部位于北京，在上海、深圳设有分支机构。公司秉承"创新驱动、技术领先"的理念，致力于为客户提供优质的技术解决方案。', 1, 1),
    ('员工手册', '/uploads/1/employee_handbook.txt', 'txt', '第一章 总则\n第一条 为规范公司管理，维护正常工作秩序，特制定本手册。\n第二条 公司员工应当遵守国家法律法规和公司规章制度。\n第三条 员工应当爱岗敬业，诚实守信，勤勉尽责。\n\n第二章 工作时间\n第四条 公司实行标准工时制，每日工作8小时，每周工作40小时。\n第五条 员工应当按时上下班，不得无故迟到早退。\n\n第三章 薪酬福利\n第六条 员工工资按月发放，于每月15日发放上月工资。\n第七条 员工享有国家规定的各项社会保险。\n第八条 公司为员工提供年度体检、带薪年假等福利。', 1, 1),
    ('考勤制度', '/uploads/1/attendance_rules.txt', 'txt', '一、考勤管理规定\n1. 员工上下班需打卡签到签退。\n2. 迟到30分钟以内扣款50元，30分钟以上按旷工处理。\n3. 因公外出需提前填写外出申请单。\n\n二、请假制度\n1. 事假需提前1天申请，3天以上需部门经理批准。\n2. 病假需提供医院证明。\n3. 年假按入职年限计算：1-3年5天，4-6年10天，7年以上15天。', 1, 1),
    ('项目管理制度', '/uploads/1/project_management.txt', 'txt', '项目管理流程\n\n1. 项目立项\n   - 需求调研与分析\n   - 项目可行性评估\n   - 立项评审与审批\n\n2. 项目计划\n   - 制定项目计划书\n   - 资源分配与协调\n   - 里程碑设定\n\n3. 项目执行\n   - 任务分配与跟踪\n   - 进度监控与报告\n   - 质量管理与控制\n\n4. 项目验收\n   - 内部测试与评审\n   - 客户验收\n   - 项目总结与归档', 2, 1);

-- 插入问答测试记录
INSERT INTO chat_history (user_id, question, answer, sources) VALUES
    (2, '公司的上班时间是怎么规定的？', '根据公司员工手册规定，公司实行标准工时制，每日工作8小时，每周工作40小时。员工应当按时上下班，不得无故迟到早退。', '[{"content": "公司实行标准工时制，每日工作8小时，每周工作40小时...", "similarity": 0.95}]'),
    (2, '年假是怎么计算的？', '根据考勤制度规定，年假按入职年限计算：\n- 1-3年：5天\n- 4-6年：10天\n- 7年以上：15天', '[{"content": "年假按入职年限计算：1-3年5天，4-6年10天，7年以上15天", "similarity": 0.98}]'),
    (3, '工资什么时候发放？', '根据员工手册规定，员工工资按月发放，于每月15日发放上月工资。', '[{"content": "员工工资按月发放，于每月15日发放上月工资", "similarity": 0.99}]'),
    (3, '如何申请病假？', '根据考勤制度规定，员工申请病假需要提供医院证明。', '[{"content": "病假需提供医院证明", "similarity": 0.97}]'),
    (4, '项目立项需要哪些流程？', '根据项目管理制度，项目立项流程包括：\n1. 需求调研与分析\n2. 项目可行性评估\n3. 立项评审与审批', '[{"content": "项目立项包括：需求调研与分析、项目可行性评估、立项评审与审批", "similarity": 0.96}]');

-- ============================================
-- 验证数据
-- ============================================
SELECT '=== 用户表数据 ===' AS '';
SELECT id, username, email, role, created_at FROM users;

SELECT '=== 文档表数据 ===' AS '';
SELECT id, title, file_type, status, uploader_id, created_at FROM documents;

SELECT '=== 问答记录表数据 ===' AS '';
SELECT id, user_id, LEFT(question, 30) as question_preview, created_at FROM chat_history;
