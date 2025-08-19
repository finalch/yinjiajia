from flask import Blueprint, jsonify, request, g
from order_service import OrderService
from models import Order, OrderItem, Product, db, ProductSpecCombination
from datetime import datetime
from config.log import get_logger

app_order_api = Blueprint('app_order_api', __name__, url_prefix='/api/app/order')
logger = get_logger(__name__)

def get_order_status_text(status):
    """获取订单状态文本"""
    status_map = {
        'pending': '待付款',
        'paid': '已付款',
        'shipped': '已发货',
        'delivered': '已送达',
        'completed': '已完成',
        'cancelled': '已取消',
        'refunded': '已退款'
    }
    return status_map.get(status, status)

def get_logistics_status_text(status):
    """获取物流状态文本"""
    status_map = {
        'pending': '待发货',
        'shipped': '已发货',
        'in_transit': '运输中',
        'delivered': '已送达',
        'failed': '配送失败'
    }
    return status_map.get(status, status)

def calculate_order_status(order_items):
    """根据订单项状态计算订单整体状态"""
    if not order_items:
        return 'pending'
    
    # 统计各状态的数量
    status_counts = {}
    for item in order_items:
        status = item.item_status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    total_items = len(order_items)
    
    # 如果所有商品都已送达，订单状态为已送达
    if status_counts.get('delivered', 0) == total_items:
        return 'delivered'
    
    # 如果有任何商品已发货，订单状态为已发货
    if status_counts.get('shipped', 0) > 0 or status_counts.get('delivered', 0) > 0:
        return 'shipped'
    
    # 所有商品都是待处理，保持为待付款
    if status_counts.get('pending', 0) == total_items:
        return 'pending'
    
    # 默认：未发货/未送达，保持待付款
    return 'pending'

@app_order_api.route('/', methods=['GET'])
def get_orders():
    """APP端-获取用户订单列表"""
    user_id = g.user_id
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        orders_data = OrderService.get_user_orders(
            user_id=user_id,
            status=status,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'code': 200,
            'message': '获取订单列表成功',
            'data': orders_data
        }), 200
    except Exception as e:
        logger.error(f"获取订单列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取订单列表失败: {str(e)}'
        }), 500

@app_order_api.route('/checkout', methods=['GET'])
def get_checkout_info():
    """APP端-获取下单页面信息"""
    user_id = g.user_id
    cart_item_ids = request.args.get('cart_items', '').split(',') if request.args.get('cart_items') else []
    product_id = request.args.get('product_id', type=int)
    quantity = request.args.get('quantity', 1, type=int)
    spec_combination_id = request.args.get('spec_combination_id', type=int)
    
    logger.info(f"获取下单信息: user_id={user_id}, cart_items={cart_item_ids}, product_id={product_id}, quantity={quantity}, spec_combination_id={spec_combination_id}")
    
    try:
        checkout_data = OrderService.get_checkout_products(
            user_id=user_id,
            cart_item_ids=cart_item_ids,
            product_id=product_id,
            quantity=quantity,
            spec_combination_id=spec_combination_id
        )
        
        return jsonify({
            'code': 200,
            'message': '获取下单信息成功',
            'data': checkout_data
        }), 200
    except Exception as e:
        logger.error(f"获取下单信息失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取下单信息失败: {str(e)}'
        }), 500

@app_order_api.route('/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """APP端-获取订单详情"""
    user_id = g.user_id
    
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
            'subtotal': float(item.subtotal),
            'spec_combination_id': item.spec_combination_id,
            'merchant_id': item.merchant_id,
            'merchant_name': (product.merchant.name if getattr(product, 'merchant', None) else '')
        })
    
    # 从OrderItem中获取物流信息
    logistics_info = None
    shipped_items = [item for item in order_items if item.shipping_company and item.tracking_number]
    
    if shipped_items:
        # 使用第一个有物流信息的商品作为主要物流信息
        main_item = shipped_items[0]
        logistics_info = {
            'tracking_number': main_item.tracking_number,
            'carrier': main_item.shipping_company,
            'status': main_item.item_status,
            'status_text': get_logistics_status_text(main_item.item_status),
            'updated_at': main_item.shipped_at.isoformat() if main_item.shipped_at else None
        }
    
    # 计算物流驱动的状态
    derived_status = calculate_order_status(order_items)
    # 订单自身状态作为真值，除非物流推进到了更后阶段
    order_status = order.status
    if order_status not in ('cancelled', 'refunded', 'completed') and derived_status in ('shipped', 'delivered'):
        order_status = derived_status
    
    data = {
        'id': order.id,
        'order_number': order.order_number,
        'status': order_status,
        'status_text': get_order_status_text(order_status),
        'total_amount': float(order.total_amount),
        'created_at': order.created_at.isoformat(),
        'items': items,
        'logistics': logistics_info
    }
    
    return jsonify({
        'code': 200,
        'message': '获取订单详情成功',
        'data': data
    }), 200

@app_order_api.route('/<int:order_id>/confirm-receipt', methods=['POST'])
def confirm_receipt(order_id):
    """APP端-确认收货：将订单项标记为已送达，并将订单状态置为已完成"""
    data = request.json or {}
    user_id = g.user_id

    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({'code': 404, 'message': '订单不存在'}), 404

    # 仅允许在已发货/已送达但未完成的订单上进行确认
    # 订单的对外展示状态是由订单项推导的，这里放宽判断，以订单项是否存在已发货为依据
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    if not order_items:
        return jsonify({'code': 400, 'message': '订单无商品，无法确认收货'}), 400

    try:
        now = datetime.utcnow()
        has_shipped_or_delivered = False
        for item in order_items:
            if item.item_status in ('shipped', 'in_transit', 'delivered'):
                has_shipped_or_delivered = True
                item.item_status = 'delivered'
                if not item.delivered_at:
                    item.delivered_at = now

        if not has_shipped_or_delivered:
            return jsonify({'code': 400, 'message': '订单尚未发货，无法确认收货'}), 400

        # 标记订单完成
        order.status = 'completed'
        order.updated_at = now

        db.session.commit()

        logger.info(f"确认收货成功: order_id={order_id}, user_id={user_id}")
        return jsonify({
            'code': 200,
            'message': '确认收货成功',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'status_text': get_order_status_text(order.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"确认收货失败: {str(e)}, order_id={order_id}, user_id={user_id}", exc_info=True)
        return jsonify({'code': 500, 'message': f'确认收货失败: {str(e)}'}), 500

@app_order_api.route('/', methods=['POST'])
def create_order():
    """APP端-创建订单"""
    data = request.json
    logger.info(f"创建订单请求: {data}")
    
    user_id = g.user_id
    address_id = data.get('address_id')
    
    # 验证收货地址
    if not address_id:
        logger.warning(f"创建订单失败: 收货地址为空, user_id={user_id}")
        return jsonify({
            'code': 400,
            'message': '收货地址不能为空'
        }), 400
    
    # 支持两种下单方式：购物车商品和直接购买
    cart_items = data.get('cart_items', [])
    direct_buy = data.get('direct_buy', {})  # 直接购买的商品信息
    
    if not cart_items and not direct_buy:
        logger.warning(f"创建订单失败: 商品信息为空, user_id={user_id}")
        return jsonify({
            'code': 400,
            'message': '商品信息不能为空'
        }), 400
    
    try:
        # 使用服务层创建订单
        order_result = OrderService.create_order(
            user_id=user_id,
            address_id=address_id,
            cart_item_ids=cart_items,
            direct_buy=direct_buy
        )
        
        # logger.info(f"订单创建成功: order_id={order_result['order_id']}, user_id={user_id}")
        
        return jsonify({
            'code': 200,
            'message': '创建订单成功',
            'data': order_result
        }), 200
    except ValueError as e:
        logger.warning(f"创建订单失败(业务错误): {str(e)}, user_id={user_id}")
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"创建订单失败(系统错误): {str(e)}, user_id={user_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'创建订单失败: {str(e)}'
        }), 500

@app_order_api.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """APP端-取消订单
    - 待付款订单：取消 => cancelled
    - 已付款未发货订单：取消并退款 => refunded
    """
    user_id = g.user_id
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({
            'code': 404,
            'message': '订单不存在'
        }), 404
    
    if order.status not in ('pending', 'paid'):
        return jsonify({
            'code': 400,
            'message': '仅待付款或已付款的订单可取消'
        }), 400
    
    try:
        now = datetime.utcnow()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.updated_at = now
        elif order.status == 'paid':
            # 已付款：按未发货处理退款，恢复库存并标记为 refunded
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            for item in order_items:
                # 恢复库存
                product = Product.query.get(item.product_id)
                if item.spec_combination_id:
                    spec_combo = ProductSpecCombination.query.get(item.spec_combination_id)
                    if spec_combo:
                        spec_combo.stock += item.quantity
                elif product:
                    product.stock += item.quantity
                # 标记订单项退款
                item.item_status = 'refunded'
                item.refunded_at = now
            order.status = 'refunded'
            order.updated_at = now
        db.session.commit()
        
        logger.info(f"订单取消成功: order_id={order_id}, user_id={user_id}, status={order.status}")
        
        return jsonify({
            'code': 200,
            'message': '取消订单成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"取消订单失败: {str(e)}, order_id={order_id}, user_id={user_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'取消订单失败: {str(e)}'
        }), 500

@app_order_api.route('/<order_number>/pay-success', methods=['POST'])
def payment_success(order_number):
    """APP端-支付成功回调"""
    data = request.json
    logger.info(f"支付成功回调: order_number={order_number}, data={data}")
    
    user_id = g.user_id
    payment_method = data.get('payment_method', 'unknown')
    
    order = Order.query.filter_by(order_number=order_number, user_id=user_id).first()
    if not order:
        logger.error(f"订单不存在: order_id={order_number}, user_id={user_id}")
        return jsonify({
            'code': 404,
            'message': '订单不存在'
        }), 404
    
    if order.status != 'pending':
        logger.warning(f"订单状态不是待付款: order_id={order_number}, status={order.status}")
        return jsonify({
            'code': 400,
            'message': '订单状态不正确'
        }), 400
    
    try:
        # 更新订单状态为已付款
        order.status = 'paid'
        order.updated_at = datetime.utcnow()
        
        # 这里可以添加支付记录等其他逻辑
        # 例如：记录支付方式、支付时间等
        
        db.session.commit()
        
        logger.info(f"支付成功，订单状态更新: order_id={order_number}, user_id={user_id}, payment_method={payment_method}")
        
        return jsonify({
            'code': 200,
            'message': '支付成功',
            'data': {
                'order_number': order.order_number,
                'status': order.status,
                'status_text': get_order_status_text(order.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"支付成功回调处理失败: {str(e)}, order_number={order_number}, user_id={user_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'支付成功回调处理失败: {str(e)}'
        }), 500


