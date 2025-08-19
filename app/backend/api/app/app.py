# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import time

from flask import Flask, request, g
from flask_cors import CORS

from config import Config
from config.log import get_logger
from models import db
from utils.TokenUtils import validate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # 启用CORS，允许所有来源访问
    CORS(app, supports_credentials=True)

    # 获取logger
    logger = get_logger(__name__)

    # 请求日志中间件
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.path} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        if request.method in ['POST', 'PUT', 'PATCH']:
            logger.debug(f"Request Body: {request.get_json(silent=True)}")
        if request.path == '/api/web/auth/login' or request.path == '/api/web/auth/register' or request.path == '/api/app/auth/login' or request.path == '/api/app/auth/register':
            return None
        authorization = request.headers.get('authorization')
        if authorization is None:
            return {"code": 401, "message": "Missing Authorization header"}, 401
        user_id = validate(authorization)
        if user_id is False:
            return {"code": 401, "message": "Invalid token"}, 401
        g.user_id = user_id
        logger.error(f"----------user_id: {user_id}")

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
    from product import app_product_api
    from cart import app_cart_api
    from address import app_address_api
    from auth import app_auth_api
    from order import app_order_api
    from review import app_review_api

    # 全局接口
    from category import category_api
    app.register_blueprint(category_api)

    app.register_blueprint(app_product_api)
    app.register_blueprint(app_cart_api)
    app.register_blueprint(app_address_api)
    app.register_blueprint(app_auth_api)
    app.register_blueprint(app_order_api)

    app.register_blueprint(app_review_api)


    logger.info("All blueprints registered successfully")
    return app, logger, Config.LOG_PATH


if __name__ == '__main__':
    app, logger, LOG_PATH = create_app()
    logger.info(f"Starting Flask app, log file: {LOG_PATH}")
    app.run(host='0.0.0.0', port=6000, debug=True)
