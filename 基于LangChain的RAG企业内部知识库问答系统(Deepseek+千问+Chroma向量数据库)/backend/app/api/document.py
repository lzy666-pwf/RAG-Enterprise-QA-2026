"""
文档管理API模块
处理文档上传、列表查询、删除等接口
"""
from flask import request, jsonify
from . import api_bp
from app.models import db, Document, User
from app.utils.auth import verify_token
from app.services.document_service import document_service
from app.services.rag_service import rag_service
from app.utils.chroma_client import add_document_vectors


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


@api_bp.route('/documents', methods=['GET'])
def get_documents():
    """
    获取文档列表接口
    支持分页和条件筛选

    Query参数:
        page: 页码（默认1）
        page_size: 每页数量（默认10）
        status: 状态筛选（可选）
        keyword: 标题关键词搜索（可选）

    Returns:
        JSON: 文档列表和分页信息
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')

    # 构建查询
    query = Document.query

    # 管理员可以看所有文档，普通用户只看自己的
    if user.role != 'admin':
        query = query.filter_by(user_id=user.id)

    # 状态筛选
    if status is not None:
        query = query.filter_by(status=status)

    # 关键词搜索
    if keyword:
        query = query.filter(Document.title.like(f'%{keyword}%'))

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


@api_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    """
    上传文档接口
    支持TXT、PDF、DOCX格式，自动解析并入库向量库

    Form参数:
        file: 上传的文件
        title: 文档标题（可选）

    Returns:
        JSON: 上传结果和文档信息
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'code': 400, 'msg': '请选择要上传的文件'})

    file = request.files['file']
    title = request.form.get('title', '').strip()

    if file.filename == '':
        return jsonify({'code': 400, 'msg': '请选择文件'})

    # 先保存文件获取doc_id
    file_path, original_name = document_service.save_file(file, user.id)
    if not file_path:
        return jsonify({'code': 400, 'msg': original_name})

    # 获取文件类型
    file_type = original_name.rsplit('.', 1)[1].lower()

    # 解析文档内容
    content = document_service.parse_document(file_path, file_type)
    if not content:
        return jsonify({'code': 400, 'msg': '无法解析文档内容'})

    # 创建文档记录
    doc = Document(
        title=title or original_name,
        file_path=file_path,
        file_type=file_type,
        content=content[:5000],
        user_id=user.id,
        status=0
    )
    db.session.add(doc)
    db.session.commit()

    # 文本分块
    chunks = document_service.split_text(content)
    if not chunks or len(chunks) == 0:
        doc.status = 1
        db.session.commit()
        return jsonify({
            'code': 200,
            'msg': '上传成功',
            'data': doc.to_dict()
        })

    # 向量入库
    try:
        embeddings = rag_service.get_embeddings(chunks)
        if not embeddings:
            doc.status = 2
            db.session.commit()
            return jsonify({
                'code': 500,
                'msg': '向量嵌入失败，请稍后重试',
                'data': doc.to_dict()
            })

        add_document_vectors(
            doc_id=doc.id,
            texts=chunks,
            embeddings=embeddings,
            metadata={'title': doc.title, 'uploader_id': user.id}
        )
        doc.status = 1
        db.session.commit()
    except Exception as e:
        doc.status = 2
        db.session.commit()
        return jsonify({
            'code': 500,
            'msg': f'向量入库失败: {str(e)}',
            'data': doc.to_dict()
        })

    return jsonify({
        'code': 200,
        'msg': '上传成功',
        'data': doc.to_dict()
    })


@api_bp.route('/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    获取单个文档详情

    Args:
        doc_id: 文档ID

    Returns:
        JSON: 文档详细信息
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'code': 404, 'msg': '文档不存在'})

    # 普通用户只能查看自己的文档
    if user.role != 'admin' and doc.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限查看此文档'})

    return jsonify({
        'code': 200,
        'msg': '获取成功',
        'data': doc.to_dict()
    })


@api_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    删除文档接口
    管理员可删除任何文档，普通用户只能删除自己的

    Args:
        doc_id: 文档ID

    Returns:
        JSON: 操作结果
    """
    user = get_current_user_from_token()
    if not user:
        return jsonify({'code': 401, 'msg': '请先登录'})

    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'code': 404, 'msg': '文档不存在'})

    # 权限检查
    if user.role != 'admin' and doc.user_id != user.id:
        return jsonify({'code': 403, 'msg': '无权限删除此文档'})

    # 执行删除
    success, error = document_service.delete_document(doc_id)

    if success:
        return jsonify({'code': 200, 'msg': '删除成功'})
    else:
        return jsonify({'code': 500, 'msg': error or '删除失败'})
