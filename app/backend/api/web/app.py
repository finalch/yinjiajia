import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time
from flask import Flask, request, g
from flask_cors import CORS
from flask_socketio import SocketIO
from config.log import get_logger
from config import Config
from models import db
from utils.TokenUtils import validate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # 启用CORS，允许所有来源访问
    CORS(app,
         supports_credentials=True,
         origins="*",
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type", "Authorization"])

    # 初始化SocketIO
    socketio = SocketIO(app,
                        cors_allowed_origins="*",
                        logger=True,
                        engineio_logger=True,
                        path='/socket.io/')

    # 获取logger
    logger = get_logger(__name__)

    # 请求日志中间件
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.path} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            logger.debug(f"Request Body: {request.get_json(silent=True)}")

        # OPTIONS请求不需要token验证（CORS预检请求）
        if request.method == 'OPTIONS':
            return None

        if (request.path == '/api/web/auth/login'
                or request.path == '/api/web/auth/register'
                or request.path == '/api/app/auth/login'
                or request.path == '/api/app/auth/register'
                or request.path == '/api/web/media/get_post_signature_for_oss_upload'
                or request.path == '/api/web/media/create-oss-bucket'):
            return None
        authorization = request.headers.get('authorization')
        if authorization is None:
            return {"code": 401, "message": "Missing Authorization header"}, 401
        merchant_id = validate(authorization)
        if merchant_id is None:
            return {"code": 401, "message": "Invalid token"}, 401
        g.merchant_id = merchant_id
        logger.error(f"----------Merchant ID: {merchant_id}")

    @app.after_request
    def log_response_info(response):
        duration = time.time() - g.start_time
        logger.info(f"Response: {request.method} {request.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
        return response

    @app.errorhandler(Exception)
    def log_exception(error):
        logger.error(f"Unhandled Exception: {request.method} {request.path} - Error: {str(error)}", exc_info=True)
        return {"code": 500, "message": "Internal Server Error"}, 500

    # Blueprint 延迟导入，避免循环引用
    # from api.app.product import app_product_api
    # from api.app.cart import app_cart_api
    # from api.app.address import app_address_api
    # from api.app.auth import app_auth_api
    from product import web_product_api
    # from order import app_order_api
    from order import web_order_api
    # from review import app_review_api
    from review import web_review_api
    from group import web_group_api
    from analytics import web_analytics_api
    from finance import web_finance_api
    from customer_service import web_customer_service_api
    from media import web_media_api
    from auth import web_auth_api
    from health import web_health_api
    from logistics import web_logistics_api
    from warehouse import web_warehouse_api

    # 全局接口
    from category import category_api
    app.register_blueprint(category_api)

    app.register_blueprint(web_order_api)
    app.register_blueprint(web_product_api)
    app.register_blueprint(web_review_api)
    app.register_blueprint(web_group_api)
    app.register_blueprint(web_analytics_api)
    app.register_blueprint(web_finance_api)
    app.register_blueprint(web_customer_service_api)
    app.register_blueprint(web_media_api)
    app.register_blueprint(web_auth_api)
    app.register_blueprint(web_health_api)
    app.register_blueprint(web_logistics_api)
    app.register_blueprint(web_warehouse_api)

    # 初始化WebSocket事件处理器
    from websocket_chat import init_websocket
    init_websocket(socketio)

    # 启动原生WebSocket服务器
    from websocket_native import websocket_handler
    websocket_handler.start_server(host='0.0.0.0', port=8002)

    logger.info("All blueprints registered successfully")
    return app, socketio, logger, Config.LOG_PATH


if __name__ == '__main__':
    app, socketio, logger, LOG_PATH = create_app()
    logger.info(f"Starting Flask app with WebSocket support, log file: {LOG_PATH}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
