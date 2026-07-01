"""
Flask应用初始化模块
创建和配置Flask应用实例，注册蓝图和扩展
"""
from flask import Flask
from flask_cors import CORS
from config import config
from app.models import db


def create_app(config_name='default'):
    """
    创建并配置Flask应用实例

    Args:
        config_name: 配置名称（development/production/default）

    Returns:
        Flask: 配置好的Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化CORS（允许跨域请求）
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.api import api_bp
    app.register_blueprint(api_bp)

    # 创建数据库表（开发环境自动创建）
    with app.app_context():
        db.create_all()

    # 注册错误处理器
    @app.errorhandler(404)
    def not_found(error):
        return {'code': 404, 'msg': '资源不存在'}, 404

    @app.errorhandler(500)
    def server_error(error):
        return {'code': 500, 'msg': '服务器内部错误'}, 500

    # 健康检查接口
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': '服务运行正常'}

    return app
