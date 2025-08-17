import logging

from flask import Blueprint, jsonify

from models import Category

category_api = Blueprint('group_api', __name__, url_prefix='/api/g/category')
logger = logging.getLogger(__name__)


@category_api.route('/', methods=['GET'])
def get_categories():
    logger.info("get_categories")
    try:
        categories = Category.query.all()
        return jsonify({
            'code': 200,
            'message': '获取品类列表成功',
            'data': {
                'list': [{
                    'id': cat.id,
                    'uuid': cat.uuid,
                    'name': cat.name,
                    'description': cat.description,
                    'icon_url': cat.icon_url,
                    'sort_order': cat.sort_order,
                } for cat in categories]
            }
        })
    except Exception as e:
        logger.error(f"获取品类列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取品类列表失败: {str(e)}',
            'data': None
        }), 500
