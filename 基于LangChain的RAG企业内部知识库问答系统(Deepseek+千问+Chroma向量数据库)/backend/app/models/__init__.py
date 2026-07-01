"""
数据模型包初始化文件
定义数据库表与Python对象的映射关系
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建SQLAlchemy数据库实例
db = SQLAlchemy()


class User(db.Model):
    """
    用户模型类
    存储系统用户信息，包括管理员和普通用户
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    password = db.Column(db.String(64), nullable=False, comment='MD5加密密码')
    email = db.Column(db.String(100), comment='邮箱地址')
    role = db.Column(db.Enum('admin', 'user', name='user_role'), default='user', comment='用户角色')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """将用户对象转换为字典格式（不含密码）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class Document(db.Model):
    """
    文档模型类
    存储上传的文档信息，包括标题、路径、状态等
    """
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='文档ID')
    title = db.Column(db.String(255), nullable=False, comment='文档标题')
    file_path = db.Column(db.String(500), comment='文件存储路径')
    file_type = db.Column(db.String(20), comment='文件类型')
    content = db.Column(db.Text, comment='文档内容摘要')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='上传用户ID')
    status = db.Column(db.SmallInteger, default=0, comment='状态:0未处理,1已入库,2向量入库失败,3解析失败')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关联上传用户
    uploader = db.relationship('User', backref=db.backref('documents', lazy=True))

    @staticmethod
    def status_text(status):
        mapping = {
            0: '待处理',
            1: '已入库',
            2: '向量入库失败',
            3: '解析失败'
        }
        return mapping.get(status, '未知')

    def to_dict(self):
        """将文档对象转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'content': self.content[:200] + '...' if self.content and len(self.content) > 200 else self.content,
            'user_id': self.user_id,
            'uploader_name': self.uploader.username if self.uploader else None,
            'status': self.status,
            'status_text': Document.status_text(self.status),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class ChatHistory(db.Model):
    """
    问答记录模型类
    存储用户的问答历史记录和AI回答
    """
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='记录ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='提问用户ID')
    question = db.Column(db.Text, nullable=False, comment='用户问题')
    answer = db.Column(db.Text, comment='AI回答')
    sources = db.Column(db.Text, comment='参考来源(JSON格式)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    # 关联提问用户
    user = db.relationship('User', backref=db.backref('chat_history', lazy=True))

    def to_dict(self):
        """将问答记录转换为字典格式"""
        import json
        sources_list = []
        if self.sources:
            try:
                sources_list = json.loads(self.sources)
            except:
                sources_list = []

        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else '未知用户',
            'question': self.question,
            'answer': self.answer,
            'sources': sources_list,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
