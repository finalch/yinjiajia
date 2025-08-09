import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
import time
from flask import Flask, request, g
from config import Config
from config.log import get_logger
from models import db
from flask_cors import CORS

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
    from api.app.product import app_product_api
    from api.app.cart import app_cart_api
    from api.app.address import app_address_api
    from api.app.auth import app_auth_api
    from api.web.product import web_product_api
    from api.app.order import app_order_api
    from api.web.order import web_order_api
    from api.app.review import app_review_api
    from api.web.review import web_review_api
    from api.web.category import category_bp
    from api.web.analytics import web_analytics_api
    from api.web.finance import web_finance_api
    from api.web.customer_service import web_customer_service_api
    from api.web.media import web_media_api

    app.register_blueprint(app_product_api)
    app.register_blueprint(app_cart_api)
    app.register_blueprint(app_address_api)
    app.register_blueprint(app_auth_api)
    app.register_blueprint(web_product_api)
    app.register_blueprint(app_order_api)
    app.register_blueprint(web_order_api)
    app.register_blueprint(app_review_api)
    app.register_blueprint(web_review_api)
    app.register_blueprint(category_bp)
    app.register_blueprint(web_analytics_api)
    app.register_blueprint(web_finance_api)
    app.register_blueprint(web_customer_service_api)
    app.register_blueprint(web_media_api)

    logger.info("All blueprints registered successfully")
    return app, logger, Config.LOG_PATH

if __name__ == '__main__':
    app, logger, LOG_PATH = create_app()
    logger.info(f"Starting Flask app, log file: {LOG_PATH}")
    app.run(debug=True)
