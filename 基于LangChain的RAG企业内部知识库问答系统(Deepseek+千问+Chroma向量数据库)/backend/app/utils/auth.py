"""
认证工具模块
提供密码加密、JWT令牌生成与验证功能
"""
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app


def generate_password(password):
    """
    生成MD5加密密码

    Args:
        password: 原始密码字符串

    Returns:
        str: MD5加密后的64位十六进制字符串
    """
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def verify_password(password, hashed):
    """
    验证密码是否正确

    Args:
        password: 原始密码字符串
        hashed: 数据库中存储的MD5哈希值

    Returns:
        bool: 密码匹配返回True，否则返回False
    """
    return generate_password(password) == hashed


def generate_token(user_id, username, role):
    """
    生成JWT访问令牌

    Args:
        user_id: 用户ID
        username: 用户名
        role: 用户角色(admin/user)

    Returns:
        str: JWT令牌字符串
    """
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def verify_token(token):
    """
    验证JWT令牌有效性

    Args:
        token: JWT令牌字符串

    Returns:
        dict|None: 令牌有效返回payload字典，无效返回None
    """
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def admin_required(f):
    """
    管理员权限装饰器
    验证请求中的JWT令牌是否为管理员角色
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'msg': '未提供认证令牌'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': '令牌无效或已过期'}), 401

        if payload.get('role') != 'admin':
            return jsonify({'code': 403, 'msg': '需要管理员权限'}), 403

        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """
    登录验证装饰器
    验证请求中的JWT令牌是否有效
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'msg': '未提供认证令牌'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': '令牌无效或已过期'}), 401

        return f(*args, **kwargs)
    return decorated_function
