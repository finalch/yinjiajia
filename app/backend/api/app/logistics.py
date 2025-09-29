from flask import Blueprint, jsonify, request, g

from config.log import get_logger
from models import OrderItem
from services.logistics import LogisticsFactory

app_logistics_api = Blueprint('app_logistics_api', __name__, url_prefix='/api/app/logistics')
logger = get_logger(__name__)


@app_logistics_api.route('/query/route', methods=['POST'])
def query_logistics_route():
    """APP端-查询物流路由信息"""
    try:
        user_id = g.user_id
        tracking_number = request.json.get('tracking_number')
        company = request.json.get('company')
        shipping_no = request.json.get('shipping_no')

        if not tracking_number:
            return jsonify(code=1, message='请输入正确的运单号'), 400
        if not company:
            return jsonify(code=1, message='请选择正确的物流公司'), 400

        # 验证用户是否有权限查询此物流信息
        # 通过tracking_number或shipping_no查找对应的订单
        # order_item = None
        # if shipping_no:
        #     order_item = OrderItem.query.filter_by(
        #         shipping_no=shipping_no,
        #         user_id=user_id
        #     ).first()
        # elif tracking_number:
        #     order_item = OrderItem.query.filter_by(
        #         tracking_number=tracking_number,
        #         user_id=user_id
        #     ).first()
        #
        # if not order_item:
        #     return jsonify(code=403, message='无权限查询此物流信息'), 403

        # 创建物流客户端并查询
        client = LogisticsFactory.create_client(company)
        routes = client.query_order(shipping_no)

        return jsonify(code=200, data={
            "routes": routes
        }), 200

    except Exception as e:
        logger.error(f'查询物流路由失败: {str(e)}')
        return jsonify(code=1, message='查询物流路由失败: {}'.format(str(e))), 500
