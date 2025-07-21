import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import logging
from flask import Flask
from config import Config
from models import db
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # 启用CORS，允许所有来源访问
    CORS(app, supports_credentials=True)

    # 日志配置
    LOG_PATH = Config.LOG_PATH
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(module)s] %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    # Blueprint 延迟导入，避免循环引用
    from api.app.product import app_product_api
    from api.web.product import web_product_api
    from api.app.order import app_order_api
    from api.web.order import web_order_api
    from api.app.review import app_review_api
    from api.web.review import web_review_api
    from api.web.category import category_bp

    app.register_blueprint(app_product_api)
    app.register_blueprint(web_product_api)
    app.register_blueprint(app_order_api)
    app.register_blueprint(web_order_api)
    app.register_blueprint(app_review_api)
    app.register_blueprint(web_review_api)
    app.register_blueprint(category_bp)

    return app, logger, LOG_PATH

if __name__ == '__main__':
    app, logger, LOG_PATH = create_app()
    logger.info(f"Starting Flask app, log file: {LOG_PATH}")
    app.run(debug=True)
