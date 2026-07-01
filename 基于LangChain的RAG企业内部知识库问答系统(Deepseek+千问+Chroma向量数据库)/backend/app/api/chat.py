"""
问答聊天API模块
处理智能问答、历史记录、多轮对话会话、SSE流式输出等接口
"""
import json
import threading
import time
from datetime import datetime
from flask import request, jsonify, Response, stream_with_context, current_app
from . import api_bp
from app.models import db, ChatHistory, User
from app.models.chat_models import ChatSession, ChatMessage
from app.utils.auth import verify_token
from app.services.rag_service import rag_service


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


@api_bp.route('/chat', methods=['POST'])
def ask_question():
    """
    智能问答接口（兼容旧版，非流式）
    基于RAG流程：检索相关文档 -> 生成回答

    请求体: {"question": "用户问题", "history": [{"role": "user"/"assistant", "content": "..."}]}

    Returns:
        JSON: 包含AI回答和参考来源
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'msg': '请求参数不能为空'})

    question = data.get('question', '').strip()
    if not question:
        return jsonify({'code': 400, 'msg': '问题不能为空'})

    conversation_history = data.get('history', [])

    try:
        result = rag_service.answer_question(question, conversation_history=conversation_history)

        chat_record = ChatHistory(
            user_id=user.id,
            question=question,
            answer=result['answer'],
            sources=str(result['sources'])
        )
        db.session.add(chat_record)
        db.session.commit()

        return jsonify({
            'code': 200,
            'msg': '回答成功',
            'data': {
                'id': chat_record.id,
                'question': question,
                'answer': result['answer'],
                'sources': result['sources'],
                'doc_count': result['doc_count']
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'问答服务异常: {str(e)}'})


@api_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    获取问答历史记录接口
    支持分页查询

    Query参数:
        page: 页码（默认1）
        page_size: 每页数量（默认20）

    Returns:
        JSON: 历史记录列表和分页信息
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    page_num = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = ChatHistory.query
    if user.role != 'admin':
        query = query.filter_by(user_id=user.id)

    query = query.order_by(ChatHistory.created_at.desc())
    pagination = query.paginate(page=page_num, per_page=page_size, error_out=False)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': {
            'items': [record.to_dict() for record in pagination.items],
            'total': pagination.total,
            'page': page_num,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })


@api_bp.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat_detail(chat_id):
    """
    获取单条问答详情
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    chat_record = ChatHistory.query.get(chat_id)
    if not chat_record:
        return jsonify({'code': 404, 'msg': '记录不存在'})

    if user.role != 'admin' and chat_record.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限查看此记录'})

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': chat_record.to_dict()
    })


@api_bp.route('/chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """
    删除问答记录
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    chat_record = ChatHistory.query.get(chat_id)
    if not chat_record:
        return jsonify({'code': 404, 'msg': '记录不存在'})

    if user.role != 'admin' and chat_record.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限删除此记录'})

    try:
        db.session.delete(chat_record)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'删除失败: {str(e)}'})


# ─────────────────────────────────────────
# 会话 API
# ─────────────────────────────────────────

@api_bp.route('/sessions', methods=['POST'])
def create_session():
    """
    创建新会话
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    data = request.get_json() or {}
    session = ChatSession(
        user_id=user.id,
        title=data.get('title') or '新对话'
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        'code': 200,
        'msg': '创建成功',
        'data': session.to_dict()
    })


@api_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """
    获取当前用户的会话列表
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    sessions = (
        ChatSession.query
        .filter_by(user_id=user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    print(f'[list_sessions] user_id={user.id}, count={len(sessions)}', flush=True)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': [s.to_dict() for s in sessions]
    })


@api_bp.route('/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """
    获取会话详情及消息
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({'code': 404, 'msg': '会话不存在'})

    if user.role != 'admin' and session.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限查看此会话'})

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': session.to_dict()
    })


@api_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    删除会话（级联删除消息）
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({'code': 404, 'msg': '会话不存在'})

    if user.role != 'admin' and session.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限删除此会话'})

    try:
        db.session.delete(session)
        db.session.commit()
        return jsonify({'code': 200, 'msg': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'msg': f'删除失败: {str(e)}'})


@api_bp.route('/sessions/<int:session_id>', methods=['PATCH'])
def update_session(session_id):
    """
    更新会话（如自动回填标题）
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({'code': 404, 'msg': '会话不存在'})

    if user.role != 'admin' and session.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限修改此会话'})

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'code': 400, 'msg': 'title 不能为空'})

    session.title = title[:200]
    db.session.commit()

    return jsonify({
        'code': 200,
        'msg': '更新成功',
        'data': session.to_dict()
    })


@api_bp.route('/sessions/<int:session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """
    获取会话消息列表
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({'code': 404, 'msg': '会话不存在'})

    if user.role != 'admin' and session.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限查看此会话'})

    messages = (
        ChatMessage.query
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    print(f'[get_session_messages] session_id={session_id}, count={len(messages)}', flush=True)

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': [m.to_dict() for m in messages]
    })


@api_bp.route('/sessions/<int:session_id>/messages', methods=['POST'])
def add_session_message(session_id):
    """
    向指定会话追加消息（用于历史记录继续对话）
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    session = ChatSession.query.get(session_id)
    if not session:
        return jsonify({'code': 404, 'msg': '会话不存在'})

    if user.role != 'admin' and session.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限操作此会话'})

    data = request.get_json() or {}
    role = data.get('role', 'user')
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'code': 400, 'msg': '消息内容不能为空'})

    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        sources=data.get('sources') or None,
    )
    db.session.add(message)
    session.updated_at = datetime.now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'msg': '添加成功',
        'data': message.to_dict()
    })


# ─────────────────────────────────────────
# SSE 流式问答
# ─────────────────────────────────────────

@api_bp.route('/chat/stream', methods=['POST'])
def chat_stream():
    """
    SSE 流式问答接口
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    data = request.get_json() or {}
    question = (data.get('question') or '').strip()
    if not question:
        return jsonify({'code': 400, 'msg': '问题不能为空'})

    session_id = data.get('session_id')
    conversation_history = data.get('history') or []

    def _background_answer(q, hist, q_obj, error_box, app):
        try:
            answer, sources = rag_service.stream_answer(
                q,
                conversation_history=hist,
                on_token=lambda token: q_obj.setdefault('tokens', []).append(token),
            )

            q_obj['answer'] = ''.join(q_obj.get('tokens', []))
            q_obj['sources'] = sources or []
            q_obj['doc_count'] = len(q_obj['sources'] or [])

            if session_id:
                try:
                    with app.app_context():
                        session = ChatSession.query.get(session_id)
                        if session:
                            user_msg = ChatMessage(session_id=session_id, role='user', content=q)
                            ai_msg = ChatMessage(
                                session_id=session_id,
                                role='assistant',
                                content=q_obj.get('answer', ''),
                                sources=json.dumps(q_obj.get('sources', []), ensure_ascii=False),
                            )
                            db.session.add(user_msg)
                            db.session.add(ai_msg)
                            session.updated_at = datetime.now()
                            if getattr(session, 'title', None) == '新对话':
                                session.title = q[:200]
                            db.session.commit()
                            print(f'[chat_stream] 会话消息保存成功: session_id={session_id}, user_msg_id={user_msg.id}, ai_msg_id={ai_msg.id}', flush=True)
                except Exception as save_err:
                    print(f'[chat_stream] 保存会话消息失败: {save_err}', flush=True)
        except Exception as e:
            import traceback
            print(f'[chat_stream] 后台线程异常: {e}', flush=True)
            traceback.print_exc()
            error_box['error'] = str(e)

    error_box = {'error': None}
    q_obj = {'question': question, 'tokens': [], 'sources': []}
    _app = current_app._get_current_object()
    t = threading.Thread(
        target=_background_answer,
        args=(question, conversation_history, q_obj, error_box, _app),
        daemon=True
    )
    t.start()

    def generate():
        start = time.time()
        timeout = 120
        last_len = 0
        last_sources = []
        while True:
            if error_box.get('error'):
                payload = {'msg': error_box['error']}
                yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                return

            tokens = q_obj.get('tokens') or []
            current_answer = ''.join(tokens)
            current_sources = q_obj.get('sources') or []

            answer_delta = current_answer[last_len:] if len(current_answer) > last_len else ''
            sources_changed = current_sources != last_sources

            if answer_delta or (current_answer and sources_changed):
                payload = {
                    'delta': answer_delta,
                    'answer': current_answer,
                    'sources': current_sources,
                    'doc_count': len(current_sources),
                    'question': question,
                }
                yield f"event: message\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                last_len = len(current_answer)
                last_sources = list(current_sources)

            if q_obj.get('answer'):
                yield "event: done\ndata: {}\n\n"
                return

            if not t.is_alive() and not tokens and not q_obj.get('answer') and not error_box.get('error'):
                payload = {'msg': '服务未返回结果，请稍后重试'}
                yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                return

            if time.time() - start > timeout:
                payload = {'msg': '请求超时，请稍后重试'}
                yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                return
            time.sleep(0.03)

    response = Response(stream_with_context(generate()), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response
