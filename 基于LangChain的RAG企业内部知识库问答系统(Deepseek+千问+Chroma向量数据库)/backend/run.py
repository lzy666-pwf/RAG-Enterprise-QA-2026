"""
Flask应用入口文件
启动Flask开发服务器
"""
from app import create_app

# 创建应用实例
app = create_app('development')

if __name__ == '__main__':
    # 启动Flask开发服务器
    # host='0.0.0.0' 允许外部访问
    # debug=True 开启调试模式
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
