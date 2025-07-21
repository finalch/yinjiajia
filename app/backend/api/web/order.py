from flask import Blueprint, jsonify, request

web_order_api = Blueprint('web_order_api', __name__, url_prefix='/api/web/order')

@web_order_api.route('/', methods=['GET'])
def get_orders():
    """WEB端-订单管理接口"""
    # TODO: 查询订单
    return jsonify({'message': 'WEB端-订单管理接口'}), 200
