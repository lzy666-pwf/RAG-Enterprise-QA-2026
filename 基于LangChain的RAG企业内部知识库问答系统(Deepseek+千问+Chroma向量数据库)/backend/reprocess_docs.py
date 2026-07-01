"""
重新向量化脚本
用于清空数据库后重新处理上传的文档
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.document_service import document_service
from app.models import db, Document as DocModel
from app.utils.chroma_client import init_vector_store, delete_document_vectors

def reprocess_all_documents():
    app = create_app()

    with app.app_context():
        # 清空向量数据库
        print("正在清空向量数据库...")
        try:
            collection = init_vector_store()
            collection.delete(where={})  # 删除所有记录
            print("✓ 向量数据库已清空")
        except Exception as e:
            print(f"清空向量数据库: {e}")

        # 清空数据库中的文档记录
        print("正在清空文档记录...")
        db.session.query(DocModel).delete()
        db.session.commit()
        print("✓ 文档记录已清空")

        # 获取上传目录下的所有文件
        upload_folder = "F:\\Python\\.vscode\\VSCODE\\基于LangChain的RAG企业内部知识库问答系统(Deepseek+千问+Chroma向量数据库)\\backend\\uploads"

        user_folder = os.path.join(upload_folder, "5")  # 用户ID为5
        if not os.path.exists(user_folder):
            print("没有找到上传文件")
            return

        files = [f for f in os.listdir(user_folder) if os.path.isfile(os.path.join(user_folder, f))]
        print(f"找到 {len(files)} 个文件待处理...")

        success_count = 0
        fail_count = 0

        for filename in files:
            file_path = os.path.join(user_folder, filename)
            print(f"\n正在处理: {filename}")

            try:
                with open(file_path, 'rb') as f:
                    from werkzeug.datastructures import FileStorage
                    file_storage = FileStorage(
                        stream=open(file_path, 'rb'),
                        filename=filename,
                        content_type='application/octet-stream'
                    )

                    # 处理文档
                    doc, error = document_service.process_document(
                        file=file_storage,
                        user_id=5,
                        title=filename
                    )

                    if error:
                        print(f"  ✗ 失败: {error}")
                        fail_count += 1
                    else:
                        print(f"  ✓ 成功: {doc.title}")
                        success_count += 1
            except Exception as e:
                print(f"  ✗ 异常: {e}")
                fail_count += 1

        print(f"\n========== 完成 ==========")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")

if __name__ == "__main__":
    reprocess_all_documents()
