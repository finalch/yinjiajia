from flask import Blueprint, jsonify, request
from models import db, Product, Order, OrderItem, Cart, Logistics
from datetime import datetime
import uuid

app_order_api = Blueprint('app_order_api', __name__, url_prefix='/api/app/order')

@app_order_api.route('/', methods=['GET'])
def get_orders():
    """APP端-获取用户订单列表"""
    user_id = request.args.get('user_id', 1, type=int)
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Order.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Order.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    orders = []
    for order in pagination.items:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        items = []
        for item in order_items:
            product = Product.query.get(item.product_id)
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product.name if product else '',
                'product_image': product.image_url if product else '',
                'price': float(item.price),
                'quantity': item.quantity,
                'subtotal': float(item.subtotal)
            })
        
        logistics = Logistics.query.filter_by(order_id=order.id).first()
        logistics_info = None
        if logistics:
            logistics_info = {
                'id': logistics.id,
                'tracking_number': logistics.tracking_number,
                'carrier': logistics.carrier,
                'status': logistics.status,
                'updated_at': logistics.updated_at.isoformat() if logistics.updated_at else None
            }
        
        orders.append({
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'status_text': get_order_status_text(order.status),
            'total_amount': float(order.total_amount),
            'items': items,
            'logistics': logistics_info,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取订单列表成功',
        'data': {
            'list': orders,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }
    }), 200

@app_order_api.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """APP端-获取订单详情"""
    user_id = request.args.get('user_id', 1, type=int)
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({
            'code': 404,
            'message': '订单不存在'
        }), 404
    
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    items = []
    for item in order_items:
        product = Product.query.get(item.product_id)
        items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': product.name if product else '',
            'product_image': product.image_url if product else '',
            'price': float(item.price),
            'quantity': item.quantity,
            'subtotal': float(item.subtotal)
        })
    
    logistics = Logistics.query.filter_by(order_id=order.id).first()
    logistics_info = None
    if logistics:
        logistics_info = {
            'id': logistics.id,
            'tracking_number': logistics.tracking_number,
            'carrier': logistics.carrier,
            'status': logistics.status,
            'status_text': get_logistics_status_text(logistics.status),
            'updated_at': logistics.updated_at.isoformat() if logistics.updated_at else None
        }
    
    data = {
        'id': order.id,
        'order_number': order.order_number,
        'status': order.status,
        'status_text': get_order_status_text(order.status),
        'total_amount': float(order.total_amount),
        'items': items,
        'logistics': logistics_info,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'updated_at': order.updated_at.isoformat() if order.updated_at else None
    }
    
    return jsonify({
        'code': 200,
        'message': '获取订单详情成功',
        'data': data
    }), 200

@app_order_api.route('/', methods=['POST'])
def create_order():
    """APP端-创建订单"""
    data = request.json
    
    if not data or 'cart_items' not in data:
        return jsonify({
            'code': 400,
            'message': '购物车商品不能为空'
        }), 400
    
    cart_items = data['cart_items']
    user_id = data.get('user_id', 1)
    
    if not cart_items:
        return jsonify({
            'code': 400,
            'message': '购物车商品不能为空'
        }), 400
    
    cart_products = []
    total_amount = 0
    
    for cart_item_id in cart_items:
        cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({
                'code': 400,
                'message': f'购物车商品ID {cart_item_id} 不存在'
            }), 400
        
        product = Product.query.get(cart_item.product_id)
        if not product:
            return jsonify({
                'code': 400,
                'message': f'商品ID {cart_item.product_id} 不存在'
            }), 400
        
        if product.status != 'on_sale':
            return jsonify({
                'code': 400,
                'message': f'商品 {product.name} 已下架'
            }), 400
        
        if product.stock < cart_item.quantity:
            return jsonify({
                'code': 400,
                'message': f'商品 {product.name} 库存不足'
            }), 400
        
        item_total = float(product.price) * cart_item.quantity
        total_amount += item_total
        
        cart_products.append({
            'cart_item': cart_item,
            'product': product,
            'quantity': cart_item.quantity,
            'price': float(product.price),
            'subtotal': item_total
        })
    
    order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    order = Order(
        user_id=user_id,
        order_number=order_number,
        status='pending',
        total_amount=total_amount
    )
    
    try:
        db.session.add(order)
        db.session.flush()
        
        for item_data in cart_products:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                price=item_data['price'],
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
            
            item_data['product'].stock -= item_data['quantity']
            db.session.delete(item_data['cart_item'])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '订单创建成功',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'订单创建失败: {str(e)}'
        }), 500

@app_order_api.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """APP端-取消订单"""
    user_id = request.args.get('user_id', 1, type=int)
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({
            'code': 404,
            'message': '订单不存在'
        }), 404
    
    if order.status not in ['pending', 'paid']:
        return jsonify({
            'code': 400,
            'message': '订单状态不允许取消'
        }), 400
    
    try:
        order.status = 'cancelled'
        order.updated_at = datetime.utcnow()
        
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        for item in order_items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '订单取消成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'订单取消失败: {str(e)}'
        }), 500

def get_order_status_text(status):
    """获取订单状态的中文描述"""
    status_map = {
        'pending': '待付款',
        'paid': '已付款',
        'shipped': '已发货',
        'delivered': '已送达',
        'completed': '已完成',
        'cancelled': '已取消',
        'refunded': '已退款'
    }
    return status_map.get(status, '未知')

def get_logistics_status_text(status):
    """获取物流状态的中文描述"""
    status_map = {
        'pending': '待发货',
        'shipped': '已发货',
        'in_transit': '运输中',
        'delivered': '已送达',
        'failed': '配送失败'
    }
    return status_map.get(status, '未知')
