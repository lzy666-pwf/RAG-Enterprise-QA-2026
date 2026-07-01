"""
多轮对话记忆模型
ChatSession: 对话会话
ChatMessage: 单条消息
"""
from datetime import datetime
from ..models import db


class ChatSession(db.Model):
    """
    对话会话模型
    每个用户可以有多个对话会话
    """
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='会话ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    title = db.Column(db.String(200), default='新对话', comment='会话标题')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联用户和消息
    user = db.relationship('User', backref=db.backref('chat_sessions', lazy=True))
    messages = db.relationship('ChatMessage', backref='session', lazy=True, order_by='ChatMessage.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'message_count': len(self.messages) if self.messages else 0,
        }


class ChatMessage(db.Model):
    """
    对话消息模型
    存储单轮对话的用户问题和AI回答
    """
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='消息ID')
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, comment='会话ID')
    role = db.Column(db.String(20), default='user', comment='角色')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    sources = db.Column(db.Text, comment='参考来源(JSON格式)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        import json
        sources_list = []
        if self.sources:
            try:
                sources_list = json.loads(self.sources)
            except Exception:
                sources_list = []

        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'sources': sources_list,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
