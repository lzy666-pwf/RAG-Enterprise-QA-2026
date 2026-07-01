"""
API路由包初始化文件
包含所有API端点的蓝图注册
"""
from flask import Blueprint

# 创建蓝图实例
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入并注册各个模块的路由
from . import auth, document, chat, admin
