from flask import Blueprint, jsonify, request
from models import db, Order, Product, User, Merchant, Logistics
from datetime import datetime, timedelta
from sqlalchemy import func

web_order_api = Blueprint('web_order_api', __name__, url_prefix='/api/web/order')

@web_order_api.route('/', methods=['GET'])
def get_orders():
    """WEB端-获取订单列表，支持条件筛选"""
    merchant_id = request.args.get('merchant_id', type=int)
    status = request.args.get('status', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    query = Order.query.filter(Order.merchant_id == merchant_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    # 分页
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    orders_data = []
    for order in pagination.items:
        # 获取用户信息
        user = User.query.get(order.user_id)
        # 获取物流信息
        logistics = Logistics.query.filter_by(order_id=order.id).first()
        
        order_data = {
            'id': order.id,
            'user_id': order.user_id,
            'user_name': user.username if user else '未知用户',
            'user_phone': user.phone if user else '',
            'total_amount': order.total_amount,
            'status': order.status,
            'status_text': get_status_text(order.status),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'logistics': {
                'company': logistics.company if logistics else '',
                'tracking_number': logistics.tracking_number if logistics else '',
                'status': logistics.status if logistics else ''
            } if logistics else None
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

@web_order_api.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """WEB端-获取订单详情"""
    order = Order.query.get_or_404(order_id)
    user = User.query.get(order.user_id)
    logistics = Logistics.query.filter_by(order_id=order.id).first()
    
    order_data = {
        'id': order.id,
        'user_id': order.user_id,
        'user_name': user.username if user else '未知用户',
        'user_phone': user.phone if user else '',
        'user_email': user.email if user else '',
        'total_amount': order.total_amount,
        'status': order.status,
        'status_text': get_status_text(order.status),
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'logistics': {
            'company': logistics.company if logistics else '',
            'tracking_number': logistics.tracking_number if logistics else '',
            'status': logistics.status if logistics else '',
            'updated_at': logistics.updated_at.strftime('%Y-%m-%d %H:%M:%S') if logistics else ''
        } if logistics else None
    }
    
    return jsonify({
        "code": 200,
        "message": "获取订单详情成功",
        "data": order_data
    }), 200

@web_order_api.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """WEB端-更新订单状态"""
    order = Order.query.get_or_404(order_id)
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({"code": 400, "message": "状态不能为空"}), 400
    
    new_status = data['status']
    valid_statuses = ['pending', 'paid', 'shipped', 'delivered', 'cancelled', 'refunded']
    
    if new_status not in valid_statuses:
        return jsonify({"code": 400, "message": "无效的订单状态"}), 400
    
    order.status = new_status
    order.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "订单状态更新成功",
            "data": {
                "id": order.id,
                "status": order.status,
                "status_text": get_status_text(order.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500

@web_order_api.route('/<int:order_id>/logistics', methods=['POST'])
def add_logistics_info(order_id):
    """WEB端-添加物流信息"""
    order = Order.query.get_or_404(order_id)
    data = request.json
    
    if not data:
        return jsonify({"code": 400, "message": "物流信息不能为空"}), 400
    
    required_fields = ['company', 'tracking_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"code": 400, "message": f"{field}不能为空"}), 400
    
    # 检查是否已存在物流信息
    existing_logistics = Logistics.query.filter_by(order_id=order_id).first()
    
    if existing_logistics:
        # 更新现有物流信息
        existing_logistics.company = data['company']
        existing_logistics.tracking_number = data['tracking_number']
        existing_logistics.status = data.get('status', '已发货')
        existing_logistics.updated_at = datetime.utcnow()
        logistics = existing_logistics
    else:
        # 创建新的物流信息
        logistics = Logistics(
            order_id=order_id,
            company=data['company'],
            tracking_number=data['tracking_number'],
            status=data.get('status', '已发货')
        )
        db.session.add(logistics)
    
    # 更新订单状态为已发货
    order.status = 'shipped'
    order.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "物流信息添加成功",
            "data": {
                "id": logistics.id,
                "company": logistics.company,
                "tracking_number": logistics.tracking_number,
                "status": logistics.status
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"添加失败: {str(e)}"}), 500

@web_order_api.route('/statistics', methods=['GET'])
def get_order_statistics():
    """WEB端-获取订单统计数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 今日订单统计
    today = datetime.utcnow().date()
    today_orders = Order.query.filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today
    ).count()
    
    # 今日销售额
    today_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 各状态订单数量
    status_counts = db.session.query(
        Order.status,
        func.count(Order.id)
    ).filter(
        Order.merchant_id == merchant_id
    ).group_by(Order.status).all()
    
    status_data = {}
    for status, count in status_counts:
        status_data[status] = count
    
    # 最近7天订单趋势
    seven_days_ago = today - timedelta(days=7)
    daily_orders = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('count')
    ).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= seven_days_ago
    ).group_by(func.date(Order.created_at)).all()
    
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
