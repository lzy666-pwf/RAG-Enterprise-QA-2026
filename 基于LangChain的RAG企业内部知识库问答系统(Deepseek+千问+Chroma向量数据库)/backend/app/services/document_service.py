"""
文档处理服务模块
负责文档上传、解析、向量入库等操作
"""
import os
import uuid
import PyPDF2
from docx import Document
from config import Config
from app.models import db, Document as DocModel
from app.services.rag_service import rag_service
from app.utils.chroma_client import add_document_vectors, delete_document_vectors


class DocumentService:
    """
    文档服务类
    处理文档的上传、解析、内容提取和向量存储
    """

    def __init__(self):
        """初始化文档服务，设置上传目录"""
        self.upload_folder = Config.UPLOAD_FOLDER
        # 确保上传目录存在
        os.makedirs(self.upload_folder, exist_ok=True)

    def allowed_file(self, filename):
        """
        检查文件扩展名是否允许

        Args:
            filename: 文件名

        Returns:
            bool: 允许返回True，否则返回False
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    def save_file(self, file, user_id):
        """
        保存上传的文件到服务器

        Args:
            file: 上传的文件对象
            user_id: 上传用户ID

        Returns:
            tuple: (保存路径, 文件名) 或 (None, 错误信息)
        """
        if not file or not file.filename:
            return None, "未提供文件"

        if not self.allowed_file(file.filename):
            return None, "不支持的文件类型，仅支持: txt, pdf, docx"

        try:
            # 生成唯一文件名避免冲突
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{ext}"

            # 按用户ID组织目录
            user_folder = os.path.join(self.upload_folder, str(user_id))
            os.makedirs(user_folder, exist_ok=True)

            file_path = os.path.join(user_folder, unique_filename)
            file.save(file_path)

            return file_path, file.filename
        except Exception as e:
            return None, f"保存文件失败: {str(e)}"

    def parse_document(self, file_path, file_type):
        """
        解析文档内容

        Args:
            file_path: 文件路径
            file_type: 文件类型

        Returns:
            str: 提取的文本内容，失败返回None
        """
        try:
            if file_type == 'txt':
                return self._parse_txt(file_path)
            elif file_type == 'pdf':
                return self._parse_pdf(file_path)
            elif file_type == 'docx':
                return self._parse_docx(file_path)
            elif file_type == 'doc':
                return self._parse_doc_legacy(file_path)
            else:
                return None
        except Exception as e:
            print(f"解析文档失败: {e}")
            return None

    def _parse_txt(self, file_path):
        """解析TXT文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_pdf(self, file_path):
        """解析PDF文件"""
        text = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)

    def _parse_docx(self, file_path):
        """解析Word文档"""
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

    def _parse_doc_legacy(self, file_path):
        """解析老版本 Word 文档 (.doc)"""
        try:
            import textract
            text = textract.process(file_path, method='antiword')
            return text.decode('utf-8', errors='ignore')
        except ImportError:
            print("textract 未安装，尝试用 doc2txt...")
            try:
                import doc2txt
                text = doc2txt.process(file_path)
                return text
            except ImportError:
                print("doc2txt 也未安装，请安装: pip install textract 或 pip install antiword")
                return None
        except Exception as e:
            print(f"解析 .doc 文件失败: {e}")
            return None

    def split_text(self, text, chunk_size=500, overlap=50):
        """
        将长文本分割成小块

        Args:
            text: 原始文本
            chunk_size: 每块的最大字符数
            overlap: 块之间的重叠字符数

        Returns:
            list: 文本块列表
        """
        if not text:
            return []

        # 按段落分割
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para_length = len(para)

            if current_length + para_length > chunk_size and current_chunk:
                # 保存当前块
                chunks.append('\n'.join(current_chunk))
                # 保留最后几个段落作为重叠
                overlap_count = 1
                current_chunk = current_chunk[-overlap_count:] if len(current_chunk) > overlap_count else []
                current_length = sum(len(p) for p in current_chunk)

            current_chunk.append(para)
            current_length += para_length

        # 添加最后一个块
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks

    def process_document(self, file, user_id, title=None):
        """
        处理文档的完整流程：保存、解析、分割、入库

        Args:
            file: 上传的文件对象
            user_id: 上传用户ID
            title: 文档标题（可选）

        Returns:
            tuple: (文档对象, 错误信息)
        """
        # 1. 保存文件
        file_path, original_name = self.save_file(file, user_id)
        if not file_path:
            return None, original_name

        # 2. 获取文件类型
        file_type = original_name.rsplit('.', 1)[1].lower()

        # 3. 解析文档内容
        content = self.parse_document(file_path, file_type)
        if not content:
            return None, "无法解析文档内容"

        # 4. 创建文档记录
        doc = DocModel(
            title=title or original_name,
            file_path=file_path,
            file_type=file_type,
            content=content[:5000],  # 保存摘要
            user_id=user_id,
            status=1
        )
        db.session.add(doc)
        db.session.commit()

        # 5. 分割文本并获取向量
        chunks = self.split_text(content)
        if not chunks:
            return doc, None

        # 6. 获取所有文本块的向量
        try:
            embeddings = rag_service.get_embeddings(chunks)
            if embeddings is None:
                print("警告: 无法获取嵌入向量，跳过向量入库")
                return doc, None
        except Exception as e:
            print(f"警告: 获取嵌入向量失败: {e}，跳过向量入库")
            return doc, None

        # 7. 存入向量数据库
        try:
            add_document_vectors(
                doc_id=doc.id,
                texts=chunks,
                embeddings=embeddings,
                metadata={'title': doc.title, 'uploader_id': user_id}
            )
        except Exception as e:
            print(f"向量入库失败: {e}")

        return doc, None

    def _vectorize_document(self, doc_id, content, original_name, user_id):
        """
        向量入库（供异步调用）
        """
        chunks = self.split_text(content)
        if not chunks:
            return

        try:
            embeddings = rag_service.get_embeddings(chunks)
            if embeddings is None:
                print("警告: 无法获取嵌入向量，跳过向量入库")
                return
        except Exception as e:
            print(f"警告: 获取嵌入向量失败: {e}，跳过向量入库")
            return

        try:
            add_document_vectors(
                doc_id=doc_id,
                texts=chunks,
                embeddings=embeddings,
                metadata={'title': original_name, 'uploader_id': user_id}
            )
            print(f"文档 {doc_id} 向量入库成功")
        except Exception as e:
            print(f"向量入库失败: {e}")

    def delete_document(self, doc_id):
        """
        删除文档及其向量

        Args:
            doc_id: 文档ID

        Returns:
            tuple: (是否成功, 错误信息)
        """
        doc = DocModel.query.get(doc_id)
        if not doc:
            return False, "文档不存在"

        # 删除物理文件
        try:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
        except Exception as e:
            print(f"删除文件失败: {e}")

        # 删除向量数据
        try:
            delete_document_vectors(doc_id)
        except Exception as e:
            print(f"删除向量失败: {e}")

        # 删除数据库记录
        db.session.delete(doc)
        db.session.commit()

        return True, None


# 创建文档服务全局实例
document_service = DocumentService()
