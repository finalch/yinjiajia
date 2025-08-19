from flask import Blueprint, jsonify, request, g
from models import db, Order, OrderItem, Product, User, Merchant, Logistics
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
web_order_api = Blueprint('web_order_api', __name__, url_prefix='/api/web/order')

@web_order_api.route('/', methods=['GET'])
def get_orders():
    """WEB端-获取商家订单列表，支持条件筛选"""
    merchant_id = g.merchant_id
    status = request.args.get('status', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    try:
        # 从OrderItem表查询该商家的订单项
        query = OrderItem.query.filter(OrderItem.merchant_id == merchant_id)
        
        if status:
            query = query.filter(OrderItem.item_status == status)
        
        # 分页
        pagination = query.order_by(OrderItem.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders_data = []
        processed_orders = set()  # 避免重复订单
        
        for order_item in pagination.items:
            order_id = order_item.order_id
            
            # 如果这个订单已经处理过，跳过
            if order_id in processed_orders:
                continue
            processed_orders.add(order_id)
            
            # 获取订单信息
            order = Order.query.get(order_id)
            if not order:
                continue
                
            # 获取用户信息
            user = User.query.get(order.user_id)
            
            # 获取该订单下该商家的所有商品
            merchant_items = OrderItem.query.filter(
                OrderItem.order_id == order_id,
                OrderItem.merchant_id == merchant_id
            ).all()
            
            # 计算该商家在这个订单中的总金额
            merchant_total = sum(item.subtotal for item in merchant_items)
            
            # 获取商品信息
            items_data = []
            for item in merchant_items:
                product = Product.query.get(item.product_id)
                items_data.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': product.name if product else '未知商品',
                    'product_image': product.image_url if product else '',
                    'spec_combination_id': item.spec_combination_id,
                    'price': item.price,
                    'quantity': item.quantity,
                    'subtotal': item.subtotal,
                    'item_status': item.item_status,
                    'shipping_company': item.shipping_company,
                    'tracking_number': item.tracking_number,
                    'shipped_at': item.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if item.shipped_at else None,
                    'delivered_at': item.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if item.delivered_at else None
                })
            
            order_data = {
                'id': order.id,
                'order_number': order.order_number,
                'user_id': order.user_id,
                'user_name': user.username if user else '未知用户',
                'user_phone': user.phone if user else '',
                'total_amount': merchant_total,  # 该商家在这个订单中的总金额
                'order_total_amount': order.total_amount,  # 整个订单的总金额
                'ship_status': order.ship_status,
                'shipping_company': order.shipping_company,
                'tracking_number': order.tracking_number,
                'shipped_at': order.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if order.shipped_at else None,
                'delivered_at': order.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if order.delivered_at else None,
                'status': order.status,
                'status_text': get_status_text(order.status),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'items': items_data
            }
            orders_data.append(order_data)
        
        return jsonify({
            "code": 200,
            "message": "获取订单列表成功",
            "data": {
                "list": orders_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": pagination.total,
                    "pages": pagination.pages
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取商家订单列表失败: {str(e)}")
        return jsonify({"code": 500, "message": f"获取订单列表失败: {str(e)}"}), 500

@web_order_api.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """WEB端-获取订单详情"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    try:
        order = Order.query.get_or_404(order_id)
        user = User.query.get(order.user_id)
        
        # 获取该订单下该商家的所有商品
        merchant_items = OrderItem.query.filter(
            OrderItem.order_id == order_id,
            OrderItem.merchant_id == merchant_id
        ).all()
        
        if not merchant_items:
            return jsonify({"code": 404, "message": "未找到该商家的订单项"}), 404
        
        # 计算该商家在这个订单中的总金额
        merchant_total = sum(item.subtotal for item in merchant_items)
        
        # 获取商品信息
        items_data = []
        for item in merchant_items:
            product = Product.query.get(item.product_id)
            items_data.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product.name if product else '未知商品',
                'product_image': product.image_url if product else '',
                'spec_combination_id': item.spec_combination_id,
                'price': item.price,
                'quantity': item.quantity,
                'subtotal': item.subtotal,
                'item_status': item.item_status,
                'shipping_company': item.shipping_company,
                'tracking_number': item.tracking_number,
                'shipped_at': item.shipped_at.strftime('%Y-%m-%d %H:%M:%S') if item.shipped_at else None,
                'delivered_at': item.delivered_at.strftime('%Y-%m-%d %H:%M:%S') if item.delivered_at else None
            })
        
        order_data = {
            'id': order.id,
            'order_number': order.order_number,
            'user_id': order.user_id,
            'user_name': user.username if user else '未知用户',
            'user_phone': user.phone if user else '',
            'user_email': user.email if user else '',
            'total_amount': merchant_total,  # 该商家在这个订单中的总金额
            'order_total_amount': order.total_amount,  # 整个订单的总金额
            'status': order.status,
            'status_text': get_status_text(order.status),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_data
        }
        
        return jsonify({
            "code": 200,
            "message": "获取订单详情成功",
            "data": order_data
        }), 200
        
    except Exception as e:
        logger.error(f"获取订单详情失败: {str(e)}")
        return jsonify({"code": 500, "message": f"获取订单详情失败: {str(e)}"}), 500

@web_order_api.route('/<int:order_id>/ship', methods=['POST'])
def ship_order(order_id):
    """WEB端-发货订单项"""
    data = request.json
    
    if not data:
        return jsonify({"code": 400, "message": "物流信息不能为空"}), 400
    
    required_fields = ['company', 'tracking_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"code": 400, "message": f"{field}不能为空"}), 400
    
    try:
        order = Order.query.get_or_404(order_id)
        
        # 更新订单项状态
        order.item_status = 'shipped'
        order.shipping_company = data['company']
        order.tracking_number = data['tracking_number']
        order.shipped_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "发货成功",
            "data": {
                "id": order.id,
                "item_status": order.item_status,
                "shipping_company": order.shipping_company,
                "tracking_number": order.tracking_number,
                "shipped_at": order.shipped_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"发货失败: {str(e)}")
        return jsonify({"code": 500, "message": f"发货失败: {str(e)}"}), 500

@web_order_api.route('/<int:order_id>/deliver', methods=['POST'])
def deliver_order(order_id):
    """WEB端-确认送达订单项"""
    try:
        order = Order.query.get_or_404(order_id)
        
        # 更新订单项状态
        order.item_status = 'delivered'
        order.delivered_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "code": 200,
            "message": "确认送达成功",
            "data": {
                "id": order.id,
                "item_status": order.item_status,
                "delivered_at": order.delivered_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"确认送达失败: {str(e)}")
        return jsonify({"code": 500, "message": f"确认送达失败: {str(e)}"}), 500



@web_order_api.route('/statistics', methods=['GET'])
def get_order_statistics():
    """WEB端-获取商家订单统计数据"""
    merchant_id = g.merchant_id
    
    try:
        # 今日订单统计
        today = datetime.utcnow().date()
        today_orders = OrderItem.query.filter(
            OrderItem.merchant_id == merchant_id,
            func.date(OrderItem.created_at) == today
        ).count()
        
        # 今日销售额
        today_sales = db.session.query(func.sum(OrderItem.subtotal)).filter(
            OrderItem.merchant_id == merchant_id,
            func.date(OrderItem.created_at) == today,
            OrderItem.item_status.in_(['paid', 'shipped', 'delivered'])
        ).scalar() or 0
        
        # 各状态订单数量
        status_counts = db.session.query(
            OrderItem.item_status,
            func.count(OrderItem.id)
        ).filter(
            OrderItem.merchant_id == merchant_id
        ).group_by(OrderItem.item_status).all()
        
        status_data = {}
        for status, count in status_counts:
            status_data[status] = count
        
        # 最近7天订单趋势
        seven_days_ago = today - timedelta(days=7)
        daily_orders = db.session.query(
            func.date(OrderItem.created_at).label('date'),
            func.count(OrderItem.id).label('count')
        ).filter(
            OrderItem.merchant_id == merchant_id,
            OrderItem.created_at >= seven_days_ago
        ).group_by(func.date(OrderItem.created_at)).all()
        
        trend_data = []
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            count = next((item.count for item in daily_orders if item.date == date), 0)
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return jsonify({
            "code": 200,
            "message": "获取订单统计成功",
            "data": {
                "today_orders": today_orders,
                "today_sales": float(today_sales),
                "status_counts": status_data,
                "trend_data": trend_data
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取订单统计失败: {str(e)}")
        return jsonify({"code": 500, "message": f"获取订单统计失败: {str(e)}"}), 500

def get_status_text(status):
    """获取订单状态的中文描述"""
    status_map = {
        'pending': '待付款',
        'paid': '已付款',
        'shipped': '已发货',
        'delivered': '已送达',
        'cancelled': '已取消',
        'refunded': '已退款'
    }
    return status_map.get(status, status)
