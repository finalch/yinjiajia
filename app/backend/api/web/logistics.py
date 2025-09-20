import json
from datetime import datetime

from flask import Blueprint, jsonify, request, g

from config.log import get_logger
from models import db, Order, OrderItem, Merchant, Warehouse
from services.logistics import LogisticsFactory, LogisticsOrder

web_logistics_api = Blueprint('web_logistics_api', __name__, url_prefix='/api/web/logistics')
logger = get_logger(__name__)


@web_logistics_api.route('/shipping', methods=['POST'])
def ship_order():
    """WEB端-发货"""
    merchant_id = g.merchant_id
    order_id = request.json.get('order_id')
    company = request.json.get('company')
    warehouse_id = request.json.get('warehouse_id')

    if not merchant_id:
        return jsonify(code=1, message='请先登录'), 400
    if not company:
        return jsonify(code=1, message='物流公司不能为空'), 400
    if not order_id:
        return jsonify(code=1, message='订单号不能为空'), 400
    if not warehouse_id:
        return jsonify(code=1, message='仓库不能为空'), 400
    try:
        # 检查是否支持该物流公司
        if not LogisticsFactory.is_supported(company):
            return jsonify(code=500, message='暂不支持该物流公司'), 400

        # 获取商家信息
        merchant = Merchant.query.get(merchant_id)
        if not merchant:
            return jsonify(code=1, message='商户不存在'), 400
        order = Order.query.get(order_id)
        if not order:
            return jsonify(code=1, message='订单不存在'), 400
        # 获取仓库信息
        warehouse = Warehouse.query.filter_by(
            id=warehouse_id,
            merchant_id=merchant_id
        ).first()
        if not warehouse:
            return jsonify(code=1, message='仓库不存在'), 400

        order_snapshot = json.loads(order.snapshot)
        address = order_snapshot.get('address')
        items = OrderItem.query.filter_by(order_id=order_id, merchant_id=merchant_id)

        if not items:
            return jsonify(code=1, message='订单不存在'), 400

        # 检查订单状态
        # for item in items:
        #     if item.item_status != 'pending':
        #         return jsonify(code=1, message='订单状态不是待处理'), 400

        # 创建物流客户端
        logistics_client = LogisticsFactory.create_client(company)

        # 生成跟踪号
        tracking_number = logistics_client._create_tracking_number()

        # 构建货物详情
        cargo_details = []
        for item in items:
            snapshot = item.snapshot
            name = "-"
            if snapshot:
                snapshot = json.loads(snapshot)
                name = snapshot['product']['name']
            cargo_details.append({'name': name})

        # 构建物流订单
        logistics_order = LogisticsOrder(
            order_id=str(order_id),
            tracking_number=tracking_number,
            sender_name=merchant.name,
            sender_phone=merchant.phone,
            sender_province=warehouse.province,
            sender_city=warehouse.city,
            sender_district=warehouse.district,
            sender_address=warehouse.detail_address,
            receiver_name=address["receiver_name"],
            receiver_phone=address["phone"],
            receiver_province=address["province"],
            receiver_city=address["city"],
            receiver_district=address.get("district", ""),
            receiver_address=address.get("detail_address", ""),
            cargo_details=cargo_details
        )

        # 创建物流订单
        response = logistics_client.create_order(logistics_order)

        if not response.success:
            return jsonify(code=500, message=f'创建{company.upper()}运单失败: {response.error_message}'), 500

        # 更新订单项状态
        shipped_at = datetime.utcnow()
        # for item in items:
        #     item.shipping_no = response.shipping_no
        #     item.logistics_ext_info = response.logistics_ext_info
        #     item.tracking_number = response.tracking_number
        #     item.shipping_company = company
        #     item.shipped_at = shipped_at
        #     item.item_status = 'shipped'
        order.ship_status = 'shipped'
        order.shipping_no = response.shipping_no
        order.logistics_ext_info = response.logistics_ext_info
        order.tracking_number = response.tracking_number
        order.shipping_company = company
        order.shipped_at = shipped_at
        db.session.commit()

        logger.info(f'创建{company.upper()}运单成功, 运单号: {response.shipping_no}')

        return jsonify(code=200, data={
            "shipping_no": response.shipping_no,
            "company": company,
            "shipped_at": shipped_at
        }), 200

    except Exception as e:
        logger.error(f'发货失败: {str(e)}')
        return jsonify(code=1, message='发货失败: {}'.format(str(e))), 500


@web_logistics_api.route('/query/route', methods=['POST'])
def query_logistics_route():
    try:
        shipping_no = request.json.get('shipping_no')
        company = request.json.get('company')

        if not shipping_no:
            return jsonify(code=1, message='请输入正确的运单号'), 400
        if not company:
            return jsonify(code=1, message='请选择正确的物流公司'), 400

        client = LogisticsFactory.create_client(company)
        routes = client.query_order(shipping_no)

        return jsonify(code=200, data={
            "routes": routes
        }), 200

    except Exception as e:
        logger.error(f'查询物流路由失败: {str(e)}')
        return jsonify(code=1, message='查询物流路由失败: {}'.format(str(e))), 500
