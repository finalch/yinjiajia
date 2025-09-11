import json
import uuid as uuid
from datetime import datetime

from flask import Blueprint, jsonify, request, g

from config.log import get_logger
from models import db, Order, OrderItem, Merchant
from services.logistics import LogisticsFactory, LogisticsOrder

web_logistics_api = Blueprint('web_logistics_api', __name__, url_prefix='/api/web/logistics')
logger = get_logger(__name__)


@web_logistics_api.route('/shipping', methods=['POST'])
def ship_order():
    """WEB端-发货"""
    merchant_id = g.merchant_id
    order_id = request.json.get('order_id')
    company = request.json.get('company')

    if not merchant_id:
        return jsonify(code=1, message='请先登录'), 400
    if not company:
        return jsonify(code=1, message='物流公司不能为空'), 400
    if not order_id:
        return jsonify(code=1, message='订单号不能为空'), 400
    
    try:
        # 检查是否支持该物流公司
        if not LogisticsFactory.is_supported(company):
            return jsonify(code=500, message='暂不支持该物流公司'), 400
        
        # 获取订单和商家信息
        merchant = Merchant.query.filter_by(id=merchant_id).first()
        order = Order.query.filter_by(id=order_id).first()
        order_snapshot = json.loads(order.snapshot)
        user = order_snapshot.get('user')
        address = user.get('address')
        items = OrderItem.query.filter_by(order_id=order_id, merchant_id=merchant_id)
        
        if not items:
            return jsonify(code=1, message='订单不存在'), 400
        
        # 检查订单状态
        for item in items:
            if item.item_status != 'pending':
                return jsonify(code=1, message='订单状态不是待处理'), 400
        
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
            sender_province='北京',
            sender_city='北京市',
            sender_district='朝阳区',
            sender_address='xxx路xxx小区',
            receiver_name=address["receiver_name"],
            receiver_phone=address["phone"],
            receiver_province=address["province"],
            receiver_city=address["city"],
            receiver_district=address.get("distinct", ""),
            receiver_address=address["detail_address"],
            cargo_details=cargo_details
        )
        
        # 创建物流订单
        response = logistics_client.create_order(logistics_order)
        
        if not response.success:
            return jsonify(code=500, message=f'创建{company.upper()}运单失败: {response.error_message}'), 500
        
        # 更新订单项状态
        shipped_at = datetime.utcnow()
        for item in items:
            item.shipping_no = response.shipping_no
            item.logistics_ext_info = response.logistics_ext_info
            item.tracking_number = response.tracking_number
            item.shipping_company = company
            item.shipped_at = shipped_at
            item.item_status = 'shipped'
        
        db.session.commit()
        
        logger.info(f'创建{company.upper()}运单成功, 运单号: {response.shipping_no}')
        
        return jsonify(code=0, data={
            "shipping_no": response.shipping_no,
            "company": company,
            "shipped_at": shipped_at
        }), 200
        
    except Exception as e:
        logger.error(f'发货失败: {str(e)}')
        return jsonify(code=1, message='发货失败: {}'.format(str(e))), 500
