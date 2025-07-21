from flask import Blueprint, jsonify, request

app_order_api = Blueprint('app_order_api', __name__, url_prefix='/api/app/order')

@app_order_api.route('/', methods=['POST'])
def create_order():
    """APP端-用户下单接口"""
    # TODO: 创建订单
    return jsonify({'message': 'APP端-下单接口'}), 201
