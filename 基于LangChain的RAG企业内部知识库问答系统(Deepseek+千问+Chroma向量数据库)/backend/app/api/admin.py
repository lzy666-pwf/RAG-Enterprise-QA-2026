"""
管理员API模块
处理管理后台的用户管理、数据统计等接口
"""
from flask import request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import Counter
import re
from . import api_bp
from app.models import db, User, Document, ChatHistory
from app.utils.auth import verify_token
from app.utils.chroma_client import clear_all_vectors, init_vector_store, get_chroma_client


def get_current_user_from_token():
    """
    从请求令牌获取当前用户

    Returns:
        User|None: 用户对象或None
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    token = auth_header.replace('Bearer ', '')
    payload = verify_token(token)
    if not payload:
        return None

    return User.query.get(payload['user_id'])


def admin_required(f):
    """
    管理员权限装饰器
    验证当前用户是否为管理员角色
    """
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user_from_token()
        if not user:
            return jsonify({'code': 401, 'msg': '请先登录'})
        if user.role != 'admin':
            return jsonify({'code': 403, 'msg': '需要管理员权限'})
        return f(*args, **kwargs)
    return decorated


@api_bp.route('/admin/stats', methods=['GET'])
@admin_required
def get_stats():
    """
    获取管理后台统计数据接口
    包含用户数、文档数、问答数等核心指标

    Returns:
        JSON: 统计数据和趋势信息
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    # 统计总数
    total_users = User.query.count()
    total_docs = Document.query.count()
    total_chats = ChatHistory.query.count()

    # 统计已入库文档数
    indexed_docs = Document.query.filter_by(status=1).count()

    # 今日新增
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_users = User.query.filter(User.created_at >= today).count()
    today_docs = Document.query.filter(Document.created_at >= today).count()
    today_chats = ChatHistory.query.filter(ChatHistory.created_at >= today).count()

    # 最近7天问答趋势
    week_ago = datetime.now() - timedelta(days=7)
    daily_chats = db.session.query(
        func.date(ChatHistory.created_at).label('date'),
        func.count(ChatHistory.id).label('count')
    ).filter(
        ChatHistory.created_at >= week_ago
    ).group_by(
        func.date(ChatHistory.created_at)
    ).all()

    # 格式化趋势数据
    chat_trend = [
        {'date': str(item.date), 'count': item.count}
        for item in daily_chats
    ]

    # 用户角色分布
    role_distribution = db.session.query(
        User.role,
        func.count(User.id).label('count')
    ).group_by(User.role).all()

    role_stats = [
        {'role': item.role, 'count': item.count}
        for item in role_distribution
    ]

    # 文档状态分布
    doc_status = db.session.query(
        Document.status,
        func.count(Document.id).label('count')
    ).group_by(Document.status).all()

    doc_status_stats = [
        {'status': '已入库', 'count': item.count}
        for item in doc_status
    ]

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'overview': {
                'total_users': total_users,
                'total_docs': total_docs,
                'total_chats': total_chats,
                'indexed_docs': indexed_docs
            },
            'today': {
                'users': today_users,
                'docs': today_docs,
                'chats': today_chats
            },
            'chat_trend': chat_trend,
            'role_distribution': role_stats,
            'doc_status': doc_status_stats,
            'question_stats': _build_question_stats(),
            'doc_usage': _build_doc_usage_stats()
        }
    })


def _build_question_stats():
    """
    构建问题关键词统计
    提取所有问题中的高频关键词，返回 Top15
    """
    try:
        all_questions = db.session.query(ChatHistory.question).all()
        words = []
        stopwords = {'的', '了', '是', '在', '和', '有', '我', '吗', '呢', '怎么',
                     '什么', '如何', '请问', '这个', '那个', '一个', '可以', '能',
                     '一下', '请', '多少', '哪些', '哪个', '需要', '应该', '要'}
        for (q,) in all_questions:
            if not q:
                continue
            # 简单分词：取连续2个以上字符的词组
            chars = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]{2,}', str(q))
            for w in chars:
                if w not in stopwords and len(w) >= 2:
                    words.append(w)
        counter = Counter(words)
        top = counter.most_common(15)
        return [{'keyword': k, 'count': c} for k, c in top]
    except Exception:
        return []


def _build_doc_usage_stats():
    """
    构建文档使用频率排行
    统计每个文档被查询参考的次数（从 sources 字段解析）
    """
    try:
        all_chats = db.session.query(ChatHistory.sources).all()
        doc_id_counts = Counter()
        import json as _json
        for (sources_str,) in all_chats:
            if not sources_str:
                continue
            try:
                sources = _json.loads(sources_str)
                for s in sources:
                    meta = s.get('metadata', {})
                    doc_id = meta.get('doc_id')
                    if doc_id:
                        doc_id_counts[int(doc_id)] += 1
            except Exception:
                continue
        top_ids = doc_id_counts.most_common(10)
        result = []
        for doc_id, count in top_ids:
            doc = Document.query.get(doc_id)
            if doc:
                result.append({'doc_id': doc_id, 'title': doc.title, 'count': count})
        return result
    except Exception:
        return []


@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    获取用户列表接口
    支持分页和搜索

    Query参数:
        page: 页码（默认1）
        page_size: 每页数量（默认10）
        keyword: 用户名关键词搜索（可选）

    Returns:
        JSON: 用户列表和分页信息
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '')

    # 构建查询
    query = User.query

    # 关键词搜索
    if keyword:
        query = query.filter(User.username.like(f'%{keyword}%'))

    # 按创建时间倒序
    query = query.order_by(User.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'items': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })


@api_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """
    更新用户信息接口
    管理员可修改用户角色

    Args:
        user_id: 用户ID

    Returns:
        JSON: 操作结果
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'code': 404, 'msg': '用户不存在'})

    # 不能修改自己
    if target_user.id == user.id:
        return jsonify({'code': 400, 'msg': '不能修改自己的角色'})

    data = request.get_json()
    new_role = data.get('role')

    if new_role and new_role in ['admin', 'user']:
        target_user.role = new_role

    try:
        db.session.commit()
        return jsonify({'code': 200, 'msg': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'更新失败: {str(e)}'})


@api_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    删除用户接口

    Args:
        user_id: 用户ID

    Returns:
        JSON: 操作结果
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'code': 404, 'msg': '用户不存在'})

    # 不能删除自己
    if target_user.id == user.id:
        return jsonify({'code': 400, 'msg': '不能删除自己'})

    try:
        db.session.delete(target_user)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'删除失败: {str(e)}'})


@api_bp.route('/admin/documents', methods=['GET'])
@admin_required
def get_all_documents():
    """
    获取所有文档列表接口（管理员）

    Query参数:
        page: 页码（默认1）
        page_size: 每页数量（默认10）
        status: 状态筛选（可选）

    Returns:
        JSON: 文档列表和分页信息
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    status = request.args.get('status', type=int)

    # 构建查询
    query = Document.query

    # 状态筛选
    if status is not None:
        query = query.filter_by(status=status)

    # 按创建时间倒序
    query = query.order_by(Document.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'items': [doc.to_dict() for doc in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })


@api_bp.route('/admin/chats', methods=['GET'])
@admin_required
def get_all_chats():
    """
    获取所有问答记录接口（管理员）

    Query参数:
        page: 页码（默认1）
        page_size: 每页数量（默认20）

    Returns:
        JSON: 问答记录列表和分页信息
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    # 分页查询
    pagination = ChatHistory.query.order_by(
        ChatHistory.created_at.desc()
    ).paginate(page=page, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'items': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })


@api_bp.route('/admin/vectors/status', methods=['GET'])
def get_vector_status():
    """
    获取向量库状态接口（仅管理员）

    返回 Chroma 集合中的向量条数和集合名称，方便排查“显示已入库但检索不到”的问题
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    try:
        client = get_chroma_client()
        collections = client.list_collections()
        collection_names = [c.name for c in collections]

        count = 0
        target = None
        for c in collections:
            if c.name == 'documents':
                target = c
                break

        if target is not None:
            count = target.count()

        return jsonify({
            'code': 200,
            'msg': '获取成功',
            'data': {
                'collection_name': 'documents',
                'vector_count': count,
                'all_collections': collection_names
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'获取向量库状态失败: {str(e)}'})


@api_bp.route('/admin/vectors/clear', methods=['POST'])
def clear_vector_store():
    """
    清空向量库接口（仅管理员）

    清空 Chroma 中所有向量数据，方便重新整理知识库
    """
    user = get_current_user_from_token()
    if not user or user.role != 'admin':
        return jsonify({'code': 403, 'msg': '需要管理员权限'})

    try:
        clear_all_vectors()
        return jsonify({'code': 200, 'msg': '向量库已清空'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'清空失败: {str(e)}'})
