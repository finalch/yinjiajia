from flask import Blueprint, jsonify, request
from models import db, Product, Order, OrderItem, Cart, Logistics, Address, ProductSpecCombination
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
                'subtotal': float(item.subtotal),
                'spec_combination_id': item.spec_combination_id
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

@app_order_api.route('/checkout', methods=['GET'])
def get_checkout_info():
    """APP端-获取下单页面信息"""
    user_id = request.args.get('user_id', 1, type=int)
    cart_item_ids = request.args.get('cart_items', '').split(',') if request.args.get('cart_items') else []
    product_id = request.args.get('product_id', type=int)
    quantity = request.args.get('quantity', 1, type=int)
    spec_combination_id = request.args.get('spec_combination_id', type=int)
    
    # 获取用户默认收货地址
    default_address = Address.query.filter_by(user_id=user_id, is_default=True).first()
    addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    
    address_list = []
    for addr in addresses:
        address_list.append({
            'id': addr.id,
            'receiver_name': addr.receiver_name,
            'phone': addr.phone,
            'province': addr.province,
            'city': addr.city,
            'district': addr.district,
            'detail_address': addr.detail_address,
            'is_default': addr.is_default,
            'full_address': f"{addr.province}{addr.city}{addr.district}{addr.detail_address}"
        })
    
    # 获取商品信息
    products = []
    total_amount = 0
    
    # 处理购物车商品
    if cart_item_ids and cart_item_ids[0]:
        for cart_item_id in cart_item_ids:
            cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user_id).first()
            if cart_item:
                product = Product.query.get(cart_item.product_id)
                if product and product.status == 'on_sale':
                    # 获取价格和库存信息
                    price = float(product.price)
                    stock = product.stock
                    
                    # 如果有规格组合，使用规格组合的价格和库存
                    if cart_item.spec_combination_id:
                        spec_combo = ProductSpecCombination.query.get(cart_item.spec_combination_id)
                        if spec_combo and spec_combo.status == 'active':
                            price = float(spec_combo.price)
                            stock = spec_combo.stock
                    
                    item_total = price * cart_item.quantity
                    total_amount += item_total
                    products.append({
                        'cart_item_id': cart_item.id,
                        'product_id': product.id,
                        'product_name': product.name,
                        'product_image': product.image_url,
                        'price': price,
                        'quantity': cart_item.quantity,
                        'subtotal': item_total,
                        'spec_combination_id': cart_item.spec_combination_id
                    })
    
    # 处理直接购买商品
    if product_id:
        product = Product.query.get(product_id)
        if product and product.status == 'on_sale':
            # 获取价格和库存信息
            price = float(product.price)
            stock = product.stock
            
            # 如果有规格组合，使用规格组合的价格和库存
            if spec_combination_id:
                spec_combo = ProductSpecCombination.query.get(spec_combination_id)
                if spec_combo and spec_combo.product_id == product_id and spec_combo.status == 'active':
                    price = float(spec_combo.price)
                    stock = spec_combo.stock
            
            item_total = price * quantity
            total_amount += item_total
            products.append({
                'cart_item_id': None,
                'product_id': product.id,
                'product_name': product.name,
                'product_image': product.image_url,
                'price': price,
                'quantity': quantity,
                'subtotal': item_total,
                'spec_combination_id': spec_combination_id
            })
    
    return jsonify({
        'code': 200,
        'message': '获取下单信息成功',
        'data': {
            'addresses': address_list,
            'default_address': address_list[0] if address_list else None,
            'products': products,
            'total_amount': total_amount,
            'product_count': len(products)
        }
    })

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
    
    user_id = data.get('user_id', 1)
    address_id = data.get('address_id')
    
    # 验证收货地址
    if not address_id:
        return jsonify({
            'code': 400,
            'message': '收货地址不能为空'
        }), 400
    
    address = Address.query.filter_by(id=address_id, user_id=user_id).first()
    if not address:
        return jsonify({
            'code': 400,
            'message': '收货地址不存在'
        }), 400
    
    # 支持两种下单方式：购物车商品和直接购买
    cart_items = data.get('cart_items', [])
    direct_buy = data.get('direct_buy', {})  # 直接购买的商品信息
    
    if not cart_items and not direct_buy:
        return jsonify({
            'code': 400,
            'message': '商品信息不能为空'
        }), 400
    
    cart_products = []
    total_amount = 0
    
    # 处理购物车商品
    if cart_items:
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
            
            # 检查规格组合
            price = float(product.price)
            stock = product.stock
            spec_combination = None
            
            if cart_item.spec_combination_id:
                spec_combination = ProductSpecCombination.query.get(cart_item.spec_combination_id)
                if not spec_combination or spec_combination.product_id != product.id or spec_combination.status != 'active':
                    return jsonify({
                        'code': 400,
                        'message': f'商品 {product.name} 规格组合不存在或已下架'
                    }), 400
                price = float(spec_combination.price)
                stock = spec_combination.stock
            
            if stock < cart_item.quantity:
                return jsonify({
                    'code': 400,
                    'message': f'商品 {product.name} 库存不足'
                }), 400
            
            item_total = price * cart_item.quantity
            total_amount += item_total
            
            cart_products.append({
                'cart_item': cart_item,
                'product': product,
                'quantity': cart_item.quantity,
                'price': price,
                'subtotal': item_total,
                'spec_combination': spec_combination
            })
    
    # 处理直接购买商品
    if direct_buy:
        product_id = direct_buy.get('product_id')
        quantity = direct_buy.get('quantity', 1)
        spec_combination_id = direct_buy.get('spec_combination_id')
        
        if not product_id:
            return jsonify({
                'code': 400,
                'message': '直接购买商品ID不能为空'
            }), 400
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'code': 400,
                'message': f'商品ID {product_id} 不存在'
            }), 400
        
        if product.status != 'on_sale':
            return jsonify({
                'code': 400,
                'message': f'商品 {product.name} 已下架'
            }), 400
        
        # 检查规格组合
        price = float(product.price)
        stock = product.stock
        spec_combination = None
        
        if spec_combination_id:
            spec_combination = ProductSpecCombination.query.get(spec_combination_id)
            if not spec_combination or spec_combination.product_id != product.id or spec_combination.status != 'active':
                return jsonify({
                    'code': 400,
                    'message': f'商品 {product.name} 规格组合不存在或已下架'
                }), 400
            price = float(spec_combination.price)
            stock = spec_combination.stock
        
        if stock < quantity:
            return jsonify({
                'code': 400,
                'message': f'商品 {product.name} 库存不足'
            }), 400
        
        item_total = price * quantity
        total_amount += item_total
        
        cart_products.append({
            'cart_item': None,  # 直接购买没有购物车项
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': item_total,
            'spec_combination': spec_combination
        })
    
    order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    order = Order(
        user_id=user_id,
        merchant_id=cart_products[0]['product'].merchant_id,  # 使用第一个商品的商家ID
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
                spec_combination_id=item_data['spec_combination'].id if item_data['spec_combination'] else None,
                price=item_data['price'],
                quantity=item_data['quantity'],
                subtotal=item_data['subtotal']
            )
            db.session.add(order_item)
            
            # 更新库存
            if item_data['spec_combination']:
                item_data['spec_combination'].stock -= item_data['quantity']
            else:
                item_data['product'].stock -= item_data['quantity']
            
            # 只删除购物车商品，直接购买的不删除购物车
            if item_data['cart_item']:
                db.session.delete(item_data['cart_item'])
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '订单创建成功',
            'data': {
                'order_id': order.id,
                'order_number': order.order_number,
                'total_amount': float(order.total_amount),
                'address': {
                    'id': address.id,
                    'receiver_name': address.receiver_name,
                    'phone': address.phone,
                    'province': address.province,
                    'city': address.city,
                    'district': address.district,
                    'detail_address': address.detail_address,
                    'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}"
                }
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
