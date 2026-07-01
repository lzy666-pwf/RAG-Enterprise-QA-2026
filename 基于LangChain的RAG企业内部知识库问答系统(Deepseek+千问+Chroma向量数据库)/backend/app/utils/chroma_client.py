"""
Chroma向量数据库客户端模块
提供向量存储、检索等功能封装
"""
import os
import chromadb
from chromadb.config import Settings
from config import Config

# 全局Chroma客户端实例
_chroma_client = None


def get_chroma_client():
    """
    获取Chroma客户端单例

    Returns:
        chromadb.PersistentClient: Chroma持久化客户端实例
    """
    global _chroma_client
    if _chroma_client is None:
        # 确保存储目录存在
        persist_dir = Config.CHROMA_PERSIST_DIRECTORY
        os.makedirs(persist_dir, exist_ok=True)

        # 创建持久化客户端
        _chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client


def init_vector_store():
    """
    初始化向量存储集合
    创建或获取名为'documents'的向量集合用于存储文档向量
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name='documents',
        metadata={'description': '企业内部知识库文档向量存储'}
    )
    return collection


def add_document_vectors(doc_id, texts, embeddings, metadata=None):
    """
    向向量库添加文档

    Args:
        doc_id: 文档ID
        texts: 文档文本列表
        embeddings: 对应的向量嵌入列表
        metadata: 元数据字典

    Returns:
        bool: 添加成功返回True
    """
    collection = init_vector_store()

    # 生成唯一的ID列表
    ids = [f"doc_{doc_id}_{i}" for i in range(len(texts))]

    # 添加元数据
    metadatas = []
    for i in range(len(texts)):
        meta = {'doc_id': doc_id}
        if metadata:
            meta.update(metadata)
        metadatas.append(meta)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    return True


def search_similar_documents(query_embedding, top_k=5):
    """
    搜索相似文档

    Args:
        query_embedding: 查询向量嵌入
        top_k: 返回的最相似文档数量

    Returns:
        list: 包含文档内容和元数据的列表
    """
    collection = init_vector_store()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # 格式化返回结果
    documents = []
    if results['documents'] and len(results['documents']) > 0:
        for i, doc in enumerate(results['documents'][0]):
            documents.append({
                'content': doc,
                'distance': results['distances'][0][i] if results['distances'] else 0,
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
            })

    return documents


def delete_document_vectors(doc_id):
    """
    删除指定文档的所有向量

    Args:
        doc_id: 文档ID

    Returns:
        bool: 删除成功返回True
    """
    collection = init_vector_store()

    try:
        # 查询该文档的所有向量ID（兼容新版 Chroma 过滤写法）
        result = collection.get(where={'doc_id': {'$eq': doc_id}})
    except Exception:
        result = {'ids': []}

    if result.get('ids'):
        collection.delete(ids=result['ids'])

    return True


def clear_all_vectors():
    """
    清空所有向量数据（谨慎使用）
    """
    client = get_chroma_client()
    try:
        client.delete_collection('documents')
        init_vector_store()
    except:
        pass
