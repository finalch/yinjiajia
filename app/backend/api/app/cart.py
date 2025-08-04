from flask import Blueprint, jsonify, request
from models import db, Product, Cart, ProductSpecCombination
from datetime import datetime

app_cart_api = Blueprint('app_cart_api', __name__, url_prefix='/api/app/cart')

@app_cart_api.route('/', methods=['GET'])
def get_cart():
    """APP端-获取购物车列表"""
    # TODO: 这里应该根据用户ID获取，暂时用固定用户ID
    user_id = request.args.get('user_id', 1, type=int)
    
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    
    data = []
    total_amount = 0
    
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product and product.status == 'on_sale':
            # 获取价格和库存信息
            price = float(product.price)
            stock = product.stock
            
            # 如果有规格组合，使用规格组合的价格和库存
            if item.spec_combination_id:
                spec_combo = ProductSpecCombination.query.get(item.spec_combination_id)
                if spec_combo and spec_combo.status == 'active':
                    price = float(spec_combo.price)
                    stock = spec_combo.stock
            
            item_total = price * item.quantity
            total_amount += item_total
            
            data.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': product.name,
                'product_image': product.image_url,
                'price': price,
                'original_price': float(product.original_price) if product.original_price else None,
                'quantity': item.quantity,
                'stock': stock,
                'spec_combination_id': item.spec_combination_id,
                'item_total': item_total,
                'created_at': item.created_at.isoformat() if item.created_at else None
            })
    
    return jsonify({
        'code': 200,
        'message': '获取购物车成功',
        'data': {
            'items': data,
            'total_amount': total_amount,
            'item_count': len(data)
        }
    }), 200

@app_cart_api.route('/', methods=['POST'])
def add_to_cart():
    """APP端-添加商品到购物车"""
    data = request.json
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({
            'code': 400,
            'message': '商品ID和数量不能为空'
        }), 400
    
    product_id = data['product_id']
    quantity = data['quantity']
    spec_combination_id = data.get('spec_combination_id')
    user_id = data.get('user_id', 1)  # TODO: 从用户认证获取
    
    # 检查商品是否存在且上架
    product = Product.query.get(product_id)
    if not product:
        return jsonify({
            'code': 404,
            'message': '商品不存在'
        }), 404
    
    if product.status != 'on_sale':
        return jsonify({
            'code': 400,
            'message': '商品已下架'
        }), 400
    
    # 检查规格组合
    if spec_combination_id:
        spec_combo = ProductSpecCombination.query.get(spec_combination_id)
        if not spec_combo or spec_combo.product_id != product_id or spec_combo.status != 'active':
            return jsonify({
                'code': 400,
                'message': '规格组合不存在或已下架'
            }), 400
        
        # 检查规格组合库存
        if spec_combo.stock < quantity:
            return jsonify({
                'code': 400,
                'message': '商品库存不足'
            }), 400
    else:
        # 检查商品总库存
        if product.stock < quantity:
            return jsonify({
                'code': 400,
                'message': '商品库存不足'
            }), 400
    
    # 检查购物车是否已有该商品（相同规格组合）
    existing_item = Cart.query.filter_by(
        user_id=user_id, 
        product_id=product_id,
        spec_combination_id=spec_combination_id
    ).first()
    
    if existing_item:
        # 更新数量
        new_quantity = existing_item.quantity + quantity
        max_stock = spec_combo.stock if spec_combo else product.stock
        
        if new_quantity > max_stock:
            return jsonify({
                'code': 400,
                'message': '商品库存不足'
            }), 400
        
        existing_item.quantity = new_quantity
        existing_item.updated_at = datetime.utcnow()
    else:
        # 新增购物车项
        cart_item = Cart(
            user_id=user_id,
            product_id=product_id,
            spec_combination_id=spec_combination_id,
            quantity=quantity
        )
        db.session.add(cart_item)
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '添加购物车成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'添加失败: {str(e)}'
        }), 500

@app_cart_api.route('/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """APP端-更新购物车商品数量"""
    data = request.json
    
    if not data or 'quantity' not in data:
        return jsonify({
            'code': 400,
            'message': '数量不能为空'
        }), 400
    
    quantity = data['quantity']
    user_id = data.get('user_id', 1)  # TODO: 从用户认证获取
    
    cart_item = Cart.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({
            'code': 404,
            'message': '购物车商品不存在'
        }), 404
    
    # 检查商品库存
    product = Product.query.get(cart_item.product_id)
    if not product or product.status != 'on_sale':
        return jsonify({
            'code': 400,
            'message': '商品已下架'
        }), 400
    
    if product.stock < quantity:
        return jsonify({
            'code': 400,
            'message': '商品库存不足'
        }), 400
    
    cart_item.quantity = quantity
    cart_item.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新失败: {str(e)}'
        }), 500

@app_cart_api.route('/<int:item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    """APP端-删除购物车商品"""
    user_id = request.args.get('user_id', 1, type=int)  # TODO: 从用户认证获取
    
    cart_item = Cart.query.filter_by(id=item_id, user_id=user_id).first()
    if not cart_item:
        return jsonify({
            'code': 404,
            'message': '购物车商品不存在'
        }), 404
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除失败: {str(e)}'
        }), 500

@app_cart_api.route('/clear', methods=['DELETE'])
def clear_cart():
    """APP端-清空购物车"""
    user_id = request.args.get('user_id', 1, type=int)  # TODO: 从用户认证获取
    
    try:
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '清空购物车成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'清空失败: {str(e)}'
        }), 500 