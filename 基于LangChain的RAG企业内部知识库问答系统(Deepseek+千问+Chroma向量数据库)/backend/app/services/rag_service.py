"""
RAG（检索增强生成）服务模块
核心问答逻辑：向量检索 + LLM生成回答
LLM使用DeepSeek API，嵌入模型使用阿里通义千问text-embedding-v3
"""
import json
import requests
from config import Config
from app.utils.chroma_client import search_similar_documents


class RAGService:
    """
    RAG服务类
    封装向量检索和LLM生成的核心逻辑
    """

    def __init__(self):
        """初始化RAG服务，加载API配置"""
        self.deepseek_api_key = Config.DEEPSEEK_API_KEY
        self.deepseek_api_url = Config.DEEPSEEK_API_URL
        self.deepseek_model = Config.DEEPSEEK_MODEL

        self.qwen_api_key = Config.QWEN_API_KEY
        self.qwen_api_url = Config.QWEN_API_URL
        self.qwen_embedding_model = Config.QWEN_EMBEDDING_MODEL

    # ─────────────────────────────────────────
    # 向量嵌入（阿里通义千问）
    # ─────────────────────────────────────────

    def get_embedding(self, text):
        """
        获取单条文本的向量嵌入
        """
        emb = self._get_qwen_embedding([text])
        if emb:
            return emb[0]
        raise RuntimeError(
            "无法获取文本向量嵌入，请检查 QWEN_API_KEY 是否配置正确。"
        )

    def get_embeddings(self, texts):
        """
        批量获取文本的向量嵌入，自动分批避免单次请求过大
        """
        if not texts:
            return []

        batch_size = 10  # DashScope embedding 单次限制不超过 10 条
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                emb = self._get_qwen_embedding(batch)
            except Exception as e:
                raise RuntimeError(
                    f"向量嵌入第 {i // batch_size + 1} 批失败: {e}"
                ) from e

            if emb is None:
                raise RuntimeError(
                    "无法批量获取向量嵌入，请检查 QWEN_API_KEY 是否配置正确。"
                )
            all_embeddings.extend(emb)

        return all_embeddings

    def _get_qwen_embedding(self, texts):
        """
        调用阿里通义千问 API 获取 embeddings
        """
        if not self.qwen_api_key:
            raise ValueError(
                "QWEN_API_KEY 未配置，无法获取向量嵌入。"
                "请在 .env 文件中配置 QWEN_API_KEY（从阿里云DashScope获取）"
            )

        # 阿里 OpenAI 兼容的 embeddings 端点：/compatible-mode/v1/embeddings
        # 注意：不能直接用 /api/v1/embeddings，会 404
        base = (self.qwen_api_url or "").rstrip("/")
        # 兼容用户配置的可能是 https://dashscope.aliyuncs.com/api/v1
        # 自动替换为 https://dashscope.aliyuncs.com/compatible-mode/v1
        if base.endswith("/api/v1"):
            base = base[: -len("/api/v1")] + "/compatible-mode/v1"
        url = f"{base}/embeddings"
        headers = {
            'Authorization': f'Bearer {self.qwen_api_key}',
            'Content-Type': 'application/json'
        }
        # OpenAI 兼容端点要求 input 为字符串数组
        payload = {
            'model': self.qwen_embedding_model,
            'input': texts
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code >= 400:
                # 打印阿里云返回的真实错误原因
                try:
                    err = resp.json()
                except Exception:
                    err = resp.text[:500]
                raise RuntimeError(
                    f"DashScope 返回 {resp.status_code}: {err}"
                ) from None
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"连接 DashScope 失败（网络/代理问题）: {e}") from e

        result = resp.json()

        # 兼容两种返回格式：
        # 1. OpenAI 兼容格式: {"data": [{"embedding": [...], "index": 0}, ...]}
        # 2. 阿里旧格式: {"output": {"embeddings": [{"embedding": [...]}, ...]}}
        if 'data' in result:
            raw = result['data']
            if raw and isinstance(raw[0], dict) and 'embedding' in raw[0]:
                return [item['embedding'] for item in raw]
            return raw
        if 'output' in result and 'embeddings' in result['output']:
            raw = result['output']['embeddings']
            if raw and isinstance(raw[0], dict) and 'embedding' in raw[0]:
                return [item['embedding'] for item in raw]
            return raw
        raise RuntimeError(f"通义千问返回格式异常: {result}")

    # ─────────────────────────────────────────
    # 查询扩展（DeepSeek）
    # ─────────────────────────────────────────

    def expand_query(self, query):
        """
        查询扩展：生成多个查询变体，提升检索召回率
        """
        if not self.deepseek_api_key:
            return [query]

        prompt = f"""你是一个查询扩展助手。对于用户的问题，请生成2个不同的搜索查询变体，
以便从知识库中检索到更多相关内容。
要求：
1. 保持原意，但使用不同的表述方式
2. 可以包含同义词、专业术语、简称/全称
3. 简短精炼，每个不超过20字
4. 只输出查询，不要其他解释

用户问题：{query}

输出格式（一行一个）："""

        try:
            url = f"{self.deepseek_api_url}/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.deepseek_api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': self.deepseek_model,
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.3,
                'max_tokens': 200
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if 'choices' in result and len(result['choices']) > 0:
                raw = result['choices'][0]['message']['content']
                lines = [l.strip() for l in raw.split('\n') if l.strip()]
                queries = [l for l in lines if len(l) > 3][:3]
                if queries:
                    return [query] + queries
            return [query]
        except Exception as e:
            print(f"[DeepSeek] 查询扩展失败: {e}")
            return [query]

    # ─────────────────────────────────────────
    # 文档检索
    # ─────────────────────────────────────────

    def retrieve_documents(self, query, top_k=3):
        """
        从向量库检索相关文档
        """
        queries = self.expand_query(query)

        all_docs = []
        seen_contents = set()

        for q in queries:
            emb = self.get_embedding(q)
            docs = search_similar_documents(emb, top_k=2)
            for doc in docs:
                content_key = doc['content'][:50]
                if content_key not in seen_contents:
                    seen_contents.add(content_key)
                    all_docs.append(doc)
                if len(all_docs) >= top_k:
                    break
            if len(all_docs) >= top_k:
                break

        return all_docs[:top_k]

    # ─────────────────────────────────────────
    # LLM 生成回答（DeepSeek）
    # ─────────────────────────────────────────

    def generate_answer(self, query, context_docs, conversation_history=None):
        """
        使用 DeepSeek LLM 生成回答（非流式）
        """
        return self._call_deepseek(query, context_docs, conversation_history, stream=False)[0]

    def stream_answer(self, query, conversation_history=None, on_token=None):
        """
        流式调用 DeepSeek，逐 token 回调 on_token。
        返回 (完整回答, 来源列表)。
        """
        docs = self.retrieve_documents(query, 3)
        full_answer, _ = self._call_deepseek(query, docs, conversation_history, stream=True, on_token=on_token)
        sources = [
            {
                'content': doc['content'][:120] + '...' if len(doc['content']) > 120 else doc['content'],
                'similarity': round(1 - doc['distance'], 4) if doc.get('distance') else 0,
                'metadata': doc.get('metadata', {})
            }
            for doc in docs
        ]
        return full_answer, sources

    def _call_deepseek(self, query, context_docs, conversation_history=None, stream=False, on_token=None):
        """
        调用 DeepSeek chat completions。
        stream=True 时逐 chunk 调用 on_token 并拼出完整回答。
        """
        if not self.deepseek_api_key:
            return ("抱歉，LLM服务未配置，请联系管理员配置 DeepSeek API密钥。", [])

        context = "\n\n".join([
            f"【文档{i+1}】{doc['content']}" for i, doc in enumerate(context_docs)
        ])

        history_block = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-6:]:
                role = "用户" if msg.get('role') == 'user' else "助手"
                history_lines.append(f"{role}：{msg.get('content', '')}")
            history_block = "【对话历史】\n" + "\n".join(history_lines) + "\n\n"

        prompt = f"""【角色】你是一个专业、耐心的企业内部知识库助手，名称叫"小知"。

【能力】
- 基于企业提供的信息库回答员工问题
- 可以联系上下文进行多轮对话
- 用清晰简洁的语言回答，必要时举例说明

【要求】
- 只根据【知识库文档】回答，不要编造信息
- 如果知识库没有相关内容，直接说明"知识库中暂未收录该信息，建议联系HR或相关部门确认"
- 回答要专业、准确、友好
- 如果用户追问，优先联系之前的对话上下文
- 回答控制在200字以内，分点作答更佳
- 遇到模糊问题时，主动提供最相关的几个方向

{history_block}【知识库文档】
{context}

【当前问题】
{query}

请以"小知"的身份回答："""

        url = f"{self.deepseek_api_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.deepseek_model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.5,
            'max_tokens': 1000,
            'stream': bool(stream),
        }

        full_answer = ''
        try:
            if stream:
                resp = requests.post(url, headers=headers, json=payload, timeout=60, stream=True)
                resp.raise_for_status()
                for line in resp.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    line = line.strip()
                    if not line.startswith('data:'):
                        continue
                    data = line[5:].strip()
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                    except Exception:
                        continue
                    choices = chunk.get('choices') or []
                    if not choices:
                        continue
                    delta = choices[0].get('delta') or {}
                    piece = delta.get('content')
                    if piece:
                        full_answer += piece
                        if on_token:
                            try:
                                on_token(piece)
                            except Exception:
                                pass
                return (full_answer, [])
            else:
                resp = requests.post(url, headers=headers, json=payload, timeout=45)
                resp.raise_for_status()
                result = resp.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return (result['choices'][0]['message']['content'], [])
                return ("生成回答失败，请稍后重试。", [])
        except Exception as e:
            print(f"[DeepSeek] LLM调用失败: {e}")
            return (f"抱歉，LLM服务出现错误：{str(e)}。请稍后重试。", [])

    def answer_question(self, question, top_k=3, conversation_history=None):
        """
        完整的问答流程：检索 + 生成（支持多轮对话）

        Returns:
            dict: 包含回答和来源信息的字典
        """
        docs = self.retrieve_documents(question, top_k)
        answer = self.generate_answer(question, docs, conversation_history)

        sources = [
            {
                'content': doc['content'][:120] + '...' if len(doc['content']) > 120 else doc['content'],
                'similarity': round(1 - doc['distance'], 4) if doc.get('distance') else 0,
                'metadata': doc.get('metadata', {})
            }
            for doc in docs
        ]

        return {
            'answer': answer,
            'sources': sources,
            'doc_count': len(docs)
        }


rag_service = RAGService()
