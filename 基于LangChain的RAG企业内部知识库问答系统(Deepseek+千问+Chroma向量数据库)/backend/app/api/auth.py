"""
认证API模块
处理用户注册、登录、获取用户信息等接口
"""
from flask import request, jsonify
from . import api_bp
from app.models import db, User, Document, ChatHistory
from app.utils.auth import generate_password, verify_password, generate_token, verify_token


@api_bp.route('/auth/register', methods=['POST'])
def register():
    """
    用户注册接口
    请求体: {"username": "xxx", "password": "xxx", "email": "xxx"}

    Returns:
        JSON: 包含用户信息或错误信息
    """
    data = request.get_json()

    # 参数验证
    if not data:
        return jsonify({'code': 400, 'msg': '请求参数不能为空'})

    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()

    if not username or len(username) < 3:
        return jsonify({'code': 400, 'msg': '用户名至少需要3个字符'})

    if not password or len(password) < 6:
        return jsonify({'code': 400, 'msg': '密码至少需要6个字符'})

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'code': 400, 'msg': '用户名已存在'})

    # 创建新用户（默认普通用户角色）
    user = User(
        username=username,
        password=generate_password(password),
        email=email,
        role='user'
    )

    try:
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'code': 200,
            'msg': '注册成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'注册失败: {str(e)}'})


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录接口
    请求体: {"username": "xxx", "password": "xxx"}

    Returns:
        JSON: 包含token和用户信息
    """
    data = request.get_json()

    if not data:
        return jsonify({'code': 400, 'msg': '请求参数不能为空'})

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'})

    # 查找用户
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'code': 401, 'msg': '用户名或密码错误'})

    # 验证密码
    if not verify_password(password, user.password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'})

    # 生成JWT令牌
    token = generate_token(user.id, user.username, user.role)

    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }
    })


@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """
    获取当前登录用户信息接口
    请求头: Authorization: Bearer <token>

    Returns:
        JSON: 包含用户信息
    """
    # 从请求头获取令牌
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未提供认证令牌'})

    token = auth_header.replace('Bearer ', '')

    # 验证令牌
    payload = verify_token(token)
    if not payload:
        return jsonify({'code': 401, 'msg': '令牌无效或已过期'})

    # 获取用户信息
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'})

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': user.to_dict()
    })


@api_bp.route('/auth/password', methods=['PUT'])
def change_password():
    """
    修改密码接口
    请求头: Authorization: Bearer <token>
    请求体: {"old_password": "xxx", "new_password": "xxx"}

    Returns:
        JSON: 操作结果
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'code': 401, 'msg': '未提供认证令牌'})

    token = auth_header.replace('Bearer ', '')
    payload = verify_token(token)
    if not payload:
        return jsonify({'code': 401, 'msg': '令牌无效或已过期'})

    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'code': 400, 'msg': '旧密码和新密码不能为空'})

    if len(new_password) < 6:
        return jsonify({'code': 400, 'msg': '新密码至少需要6个字符'})

    # 获取用户
    user = User.query.get(payload['user_id'])
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'})

    # 验证旧密码
    if not verify_password(old_password, user.password):
        return jsonify({'code': 400, 'msg': '旧密码不正确'})

    # 更新密码
    user.password = generate_password(new_password)

    try:
        db.session.commit()
        return jsonify({'code': 200, 'msg': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'修改失败: {str(e)}'})


def get_user_from_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.replace('Bearer ', '')
    payload = verify_token(token)
    if not payload:
        return None
    return User.query.get(payload['user_id'])


@api_bp.route('/stats', methods=['GET'])
def get_user_stats():
    """
    获取当前用户的统计数据
    专供首页仪表盘使用
    """
    user = get_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    doc_query = Document.query.filter_by(user_id=user.id)
    chat_query = ChatHistory.query.filter_by(user_id=user.id)

    doc_count = doc_query.count()
    indexed_count = doc_query.filter_by(status=1).count()
    pending_count = 0
    chat_count = chat_query.count()

    recent_chats = chat_query.order_by(ChatHistory.created_at.desc()).limit(3).all()

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'docCount': doc_count,
            'chatCount': chat_count,
            'indexedCount': indexed_count,
            'pendingCount': pending_count,
            'recentChats': [c.to_dict() for c in recent_chats]
        }
    })
