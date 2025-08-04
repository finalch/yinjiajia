from flask import Blueprint, jsonify, request
from models import db, Product, Category, Merchant, ProductSpec, ProductSpecCombination
from datetime import datetime
from sqlalchemy import func
import json

web_product_api = Blueprint('web_product_api', __name__, url_prefix='/api/web/product')

@web_product_api.route('/', methods=['GET'])
def get_products():
    """WEB端-获取商品列表，支持条件筛选"""
    query = Product.query
    name = request.args.get('name', type=str)
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=str)
    merchant_id = request.args.get('merchant_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if name:
        query = query.filter(Product.name.like(f"%{name}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if merchant_id:
        query = query.filter(Product.merchant_id == merchant_id)
    if status:
        query = query.filter(Product.status == status)

    # 分页
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    products_data = []
    for product in pagination.items:
        # 获取分类信息
        category = Category.query.get(product.category_id)
        # 获取商家信息
        merchant = Merchant.query.get(product.merchant_id)
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'image_url': product.image_url,
            'video_url': product.video_url,
            'category': product.category,
            'category_id': product.category_id,
            'category_name': category.name if category else '',
            'merchant_id': product.merchant_id,
            'merchant_name': merchant.name if merchant else '',
            'has_specs': product.has_specs,  # 是否有规格
            'status': product.status,
            'status_text': get_status_text(product.status),
            'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        products_data.append(product_data)
    
    return jsonify({
        "code": 200,
        "message": "获取商品列表成功",
        "data": {
            "list": products_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200

@web_product_api.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """WEB端-获取商品详情"""
    product = Product.query.get_or_404(product_id)
    
    # 获取分类信息
    category = Category.query.get(product.category_id)
    # 获取商家信息
    merchant = Merchant.query.get(product.merchant_id)
    
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'detail': product.detail,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'video_url': product.video_url,
        'category': product.category,
        'category_id': product.category_id,
        'category_name': category.name if category else '',
        'merchant_id': product.merchant_id,
        'merchant_name': merchant.name if merchant else '',
        'has_specs': product.has_specs,  # 是否有规格
        'status': product.status,
        'status_text': get_status_text(product.status),
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 如果是多规格商品，添加规格信息
    if product.has_specs:
        # 获取规格信息
        specs = ProductSpec.query.filter(ProductSpec.product_id == product.id).order_by(ProductSpec.sort_order).all()
        specs_data = []
        for spec in specs:
            try:
                values = json.loads(spec.values)
                specs_data.append({
                    'id': spec.id,
                    'name': spec.name,
                    'values': values,
                    'sort_order': spec.sort_order
                })
            except json.JSONDecodeError:
                continue
        
        # 获取规格组合信息
        combinations = ProductSpecCombination.query.filter(
            ProductSpecCombination.product_id == product.id,
            ProductSpecCombination.status == 'active'
        ).all()
        combinations_data = []
        for combo in combinations:
            try:
                spec_values = json.loads(combo.spec_values)
                combinations_data.append({
                    'id': combo.id,
                    'spec_values': spec_values,
                    'price': float(combo.price),
                    'stock': combo.stock,
                    'image_url': combo.image_url,
                    'status': combo.status
                })
            except json.JSONDecodeError:
                continue
        
        data['specs'] = specs_data
        data['spec_combinations'] = combinations_data
    return jsonify({
        "code": 200,
        "message": "获取商品详情成功",
        "data": data
    }), 200

@web_product_api.route('/', methods=['POST'])
def create_product():
    """WEB端-创建商品"""
    data = request.json
    
    required_fields = ['name', 'category_id', 'merchant_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"code": 400, "message": f"{field} 不能为空"}), 400
    
    # 校验分类和商家是否存在
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({"code": 404, "message": "分类不存在"}), 404
    
    merchant = Merchant.query.get(data['merchant_id'])
    if not merchant:
        return jsonify({"code": 404, "message": "商家不存在"}), 404
    
    # 检查是否是多规格商品
    has_specs = data.get('has_specs', False)
    
    if not has_specs:
        # 无规格商品验证
        if not data.get('price'):
            return jsonify({"code": 400, "message": "价格不能为空"}), 400
        if not data.get('stock'):
            return jsonify({"code": 400, "message": "库存不能为空"}), 400
        
        # 校验价格
        try:
            price = float(data['price'])
            if price <= 0:
                return jsonify({"code": 400, "message": "价格必须为大于0的数字"}), 400
        except Exception:
            return jsonify({"code": 400, "message": "价格必须为数字"}), 400
        
        # 校验库存
        try:
            stock = int(data['stock'])
            if stock < 0:
                return jsonify({"code": 400, "message": "库存必须为不小于0的整数"}), 400
        except Exception:
            return jsonify({"code": 400, "message": "库存必须为整数"}), 400
        
        # 处理图片和视频
        main_image = data.get('main_image', '')
        images = data.get('images', [])
        videos = data.get('videos', [])
        
        # 合并所有图片URL
        all_images = [main_image] + images if main_image else images
        image_url = '$%%$'.join(all_images) if all_images else ''
        
        # 处理视频URL
        video_url = videos[0] if videos else ''
        
        # 创建无规格商品
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            detail=data.get('detail', ''),
            price=price,
            stock=stock,
            image_url=image_url,
            video_url=video_url,
            category_id=data['category_id'],
            merchant_id=data['merchant_id'],
            has_specs=False,
            status='pending'  # 新商品默认为待审核状态
        )
    else:
        # 多规格商品验证
        if not data.get('specs') or not isinstance(data['specs'], list):
            return jsonify({"code": 400, "message": "多规格商品必须包含规格信息"}), 400
        
        if not data.get('spec_combinations') or not isinstance(data['spec_combinations'], list):
            return jsonify({"code": 400, "message": "多规格商品必须包含规格组合信息"}), 400
        
        # 验证规格信息
        for spec in data['specs']:
            if not spec.get('name') or not spec.get('values'):
                return jsonify({"code": 400, "message": "规格信息不完整"}), 400
        
        # 验证规格组合信息
        for combo in data['spec_combinations']:
            if not combo.get('price') or not combo.get('stock'):
                return jsonify({"code": 400, "message": "规格组合信息不完整"}), 400
            
            try:
                price = float(combo['price'])
                if price <= 0:
                    return jsonify({"code": 400, "message": "规格组合价格必须为大于0的数字"}), 400
            except Exception:
                return jsonify({"code": 400, "message": "规格组合价格必须为数字"}), 400
            
            try:
                stock = int(combo['stock'])
                if stock < 0:
                    return jsonify({"code": 400, "message": "规格组合库存必须为不小于0的整数"}), 400
            except Exception:
                return jsonify({"code": 400, "message": "规格组合库存必须为整数"}), 400
        
        # 计算最低价格和总库存
        min_price = min(float(combo['price']) for combo in data['spec_combinations'])
        total_stock = sum(int(combo['stock']) for combo in data['spec_combinations'])
        
        # 处理图片和视频
        main_image = data.get('main_image', '')
        images = data.get('images', [])
        videos = data.get('videos', [])
        
        # 合并所有图片URL
        all_images = [main_image] + images if main_image else images
        image_url = '$%%$'.join(all_images) if all_images else ''
        
        # 处理视频URL
        video_url = videos[0] if videos else ''
        
        # 创建多规格商品
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            detail=data.get('detail', ''),
            price=min_price,  # 使用最低价格作为基础价格
            stock=total_stock,  # 使用总库存
            image_url=image_url,
            video_url=video_url,
            category_id=data['category_id'],
            merchant_id=data['merchant_id'],
            has_specs=True,
            status='pending'  # 新商品默认为待审核状态
        )
    
    try:
        db.session.add(product)
        db.session.flush()  # 获取product.id
        
        # 如果是多规格商品，创建规格和规格组合
        if has_specs:
            # 创建规格
            for spec_data in data['specs']:
                spec = ProductSpec(
                    product_id=product.id,
                    name=spec_data['name'],
                    values=spec_data['values'],  # 已经是JSON字符串
                    sort_order=spec_data.get('sort_order', 0)
                )
                db.session.add(spec)
            
            # 创建规格组合
            for combo_data in data['spec_combinations']:
                combo = ProductSpecCombination(
                    product_id=product.id,
                    spec_values=combo_data['spec_values'],  # 已经是JSON字符串
                    price=float(combo_data['price']),
                    stock=int(combo_data['stock']),
                    image_url=combo_data.get('image_url', ''),
                    status='active'
                )
                db.session.add(combo)
        
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "商品发布成功，等待审核",
            "data": {
                "product_id": product.id,
                "status": product.status,
                "status_text": get_status_text(product.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"创建失败: {str(e)}"}), 500

@web_product_api.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """WEB端-更新商品信息"""
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    if not data:
        return jsonify({"code": 400, "message": "更新数据不能为空"}), 400
    
    # 检查是否是多规格商品
    has_specs = data.get('has_specs', product.has_specs)
    
    # 更新基本信息
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'detail' in data:
        product.detail = data['detail']
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({"code": 404, "message": "分类不存在"}), 404
        product.category_id = data['category_id']
    if 'main_image' in data or 'images' in data or 'videos' in data:
        # 处理图片和视频
        main_image = data.get('main_image', '')
        images = data.get('images', [])
        videos = data.get('videos', [])
        
        # 合并所有图片URL
        all_images = [main_image] + images if main_image else images
        image_url = '$%%$'.join(all_images) if all_images else ''
        
        # 处理视频URL
        video_url = videos[0] if videos else ''
        
        product.image_url = image_url
        product.video_url = video_url
    
    # 处理规格相关更新
    if not has_specs:
        # 无规格商品更新
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({"code": 400, "message": "价格必须为大于0的数字"}), 400
                product.price = price
            except Exception:
                return jsonify({"code": 400, "message": "价格必须为数字"}), 400
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({"code": 400, "message": "库存必须为不小于0的整数"}), 400
                product.stock = stock
            except Exception:
                return jsonify({"code": 400, "message": "库存必须为整数"}), 400
        
        # 如果从多规格改为无规格，删除相关规格数据
        if product.has_specs and not has_specs:
            ProductSpec.query.filter(ProductSpec.product_id == product.id).delete()
            ProductSpecCombination.query.filter(ProductSpecCombination.product_id == product.id).delete()
        
        product.has_specs = False
    else:
        # 多规格商品更新
        if not data.get('specs') or not isinstance(data['specs'], list):
            return jsonify({"code": 400, "message": "多规格商品必须包含规格信息"}), 400
        
        if not data.get('spec_combinations') or not isinstance(data['spec_combinations'], list):
            return jsonify({"code": 400, "message": "多规格商品必须包含规格组合信息"}), 400
        
        # 验证规格信息
        for spec in data['specs']:
            if not spec.get('name') or not spec.get('values'):
                return jsonify({"code": 400, "message": "规格信息不完整"}), 400
        
        # 验证规格组合信息
        for combo in data['spec_combinations']:
            if not combo.get('price') or not combo.get('stock'):
                return jsonify({"code": 400, "message": "规格组合信息不完整"}), 400
            
            try:
                price = float(combo['price'])
                if price <= 0:
                    return jsonify({"code": 400, "message": "规格组合价格必须为大于0的数字"}), 400
            except Exception:
                return jsonify({"code": 400, "message": "规格组合价格必须为数字"}), 400
            
            try:
                stock = int(combo['stock'])
                if stock < 0:
                    return jsonify({"code": 400, "message": "规格组合库存必须为不小于0的整数"}), 400
            except Exception:
                return jsonify({"code": 400, "message": "规格组合库存必须为整数"}), 400
        
        # 计算最低价格和总库存
        min_price = min(float(combo['price']) for combo in data['spec_combinations'])
        total_stock = sum(int(combo['stock']) for combo in data['spec_combinations'])
        
        product.price = min_price
        product.stock = total_stock
        product.has_specs = True
        
        # 删除旧的规格数据
        ProductSpec.query.filter(ProductSpec.product_id == product.id).delete()
        ProductSpecCombination.query.filter(ProductSpecCombination.product_id == product.id).delete()
        
        # 创建新的规格数据
        for spec_data in data['specs']:
            spec = ProductSpec(
                product_id=product.id,
                name=spec_data['name'],
                values=spec_data['values'],  # 已经是JSON字符串
                sort_order=spec_data.get('sort_order', 0)
            )
            db.session.add(spec)
        
        # 创建新的规格组合数据
        for combo_data in data['spec_combinations']:
            combo = ProductSpecCombination(
                product_id=product.id,
                spec_values=combo_data['spec_values'],  # 已经是JSON字符串
                price=float(combo_data['price']),
                stock=int(combo_data['stock']),
                image_url=combo_data.get('image_url', ''),
                status='active'
            )
            db.session.add(combo)
    
    product.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "商品更新成功",
            "data": {
                "product_id": product.id,
                "status": product.status,
                "status_text": get_status_text(product.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500

@web_product_api.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """WEB端-删除商品"""
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "商品删除成功"
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"删除失败: {str(e)}"}), 500

@web_product_api.route('/<int:product_id>/audit', methods=['POST'])
def audit_product(product_id):
    """WEB端-审核商品"""
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({"code": 400, "message": "审核状态不能为空"}), 400
    
    new_status = data['status']
    valid_statuses = ['approved', 'rejected']
    
    if new_status not in valid_statuses:
        return jsonify({"code": 400, "message": "无效的审核状态"}), 400
    
    # 更新商品状态
    product.status = new_status
    product.updated_at = datetime.utcnow()
    
    # 记录审核信息
    audit_reason = data.get('reason', '')
    audit_note = data.get('note', '')
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "商品审核成功",
            "data": {
                "product_id": product.id,
                "status": product.status,
                "status_text": get_status_text(product.status),
                "audit_reason": audit_reason,
                "audit_note": audit_note
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"审核失败: {str(e)}"}), 500

@web_product_api.route('/batch-audit', methods=['POST'])
def batch_audit_products():
    """WEB端-批量审核商品"""
    data = request.json
    
    if not data or 'product_ids' not in data or 'status' not in data:
        return jsonify({"code": 400, "message": "商品ID列表和审核状态不能为空"}), 400
    
    product_ids = data['product_ids']
    new_status = data['status']
    valid_statuses = ['approved', 'rejected']
    
    if new_status not in valid_statuses:
        return jsonify({"code": 400, "message": "无效的审核状态"}), 400
    
    if not isinstance(product_ids, list) or len(product_ids) == 0:
        return jsonify({"code": 400, "message": "商品ID列表不能为空"}), 400
    
    # 批量更新商品状态
    updated_count = 0
    failed_count = 0
    
    for product_id in product_ids:
        product = Product.query.get(product_id)
        if product:
            product.status = new_status
            product.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            failed_count += 1
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "批量审核完成",
            "data": {
                "updated_count": updated_count,
                "failed_count": failed_count,
                "status": new_status,
                "status_text": get_status_text(new_status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"批量审核失败: {str(e)}"}), 500

@web_product_api.route('/audit-statistics', methods=['GET'])
def get_audit_statistics():
    """WEB端-获取审核统计数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 统计各状态商品数量
    status_counts = db.session.query(
        Product.status,
        func.count(Product.id)
    ).filter(
        Product.merchant_id == merchant_id
    ).group_by(Product.status).all()
    
    status_data = {}
    for status, count in status_counts:
        status_data[status] = count
    
    # 今日新增待审核商品
    today = datetime.utcnow().date()
    today_pending = Product.query.filter(
        Product.merchant_id == merchant_id,
        Product.status == 'pending',
        func.date(Product.created_at) == today
    ).count()
    
    # 今日审核通过商品
    today_approved = Product.query.filter(
        Product.merchant_id == merchant_id,
        Product.status == 'approved',
        func.date(Product.updated_at) == today
    ).count()
    
    # 今日审核拒绝商品
    today_rejected = Product.query.filter(
        Product.merchant_id == merchant_id,
        Product.status == 'rejected',
        func.date(Product.updated_at) == today
    ).count()
    
    return jsonify({
        "code": 200,
        "message": "获取审核统计成功",
        "data": {
            "status_counts": status_data,
            "today_pending": today_pending,
            "today_approved": today_approved,
            "today_rejected": today_rejected
        }
    }), 200

@web_product_api.route('/pending-audit', methods=['GET'])
def get_pending_audit_products():
    """WEB端-获取待审核商品列表"""
    merchant_id = request.args.get('merchant_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    query = Product.query.filter(
        Product.merchant_id == merchant_id,
        Product.status == 'pending'
    )
    
    # 分页
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    products_data = []
    for product in pagination.items:
        # 获取分类信息
        category = Category.query.get(product.category_id)
        # 获取商家信息
        merchant = Merchant.query.get(product.merchant_id)
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'image_url': product.image_url,
            'video_url': product.video_url,
            'category_name': category.name if category else '',
            'merchant_name': merchant.name if merchant else '',
            'status': product.status,
            'status_text': get_status_text(product.status),
            'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        products_data.append(product_data)
    
    return jsonify({
        "code": 200,
        "message": "获取待审核商品成功",
        "data": {
            "list": products_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200

@web_product_api.route('/<int:product_id>/toggle-status', methods=['POST'])
def toggle_product_status(product_id):
    """WEB端-切换商品上架/下架状态"""
    product = Product.query.get_or_404(product_id)
    data = request.json
    
    if not data or 'status' not in data:
        return jsonify({"code": 400, "message": "状态不能为空"}), 400
    
    new_status = data['status']
    valid_statuses = ['on_sale', 'off_sale']
    
    if new_status not in valid_statuses:
        return jsonify({"code": 400, "message": "无效的状态"}), 400
    
    # 只有审核通过的商品才能上架/下架
    if product.status != 'approved' and new_status == 'on_sale':
        return jsonify({"code": 400, "message": "只有审核通过的商品才能上架"}), 400
    
    # 更新商品状态
    product.status = new_status
    product.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": f"商品{'上架' if new_status == 'on_sale' else '下架'}成功",
            "data": {
                "product_id": product.id,
                "status": product.status,
                "status_text": get_status_text(product.status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"操作失败: {str(e)}"}), 500

@web_product_api.route('/batch-toggle-status', methods=['POST'])
def batch_toggle_product_status():
    """WEB端-批量切换商品上架/下架状态"""
    data = request.json
    
    if not data or 'product_ids' not in data or 'status' not in data:
        return jsonify({"code": 400, "message": "商品ID列表和状态不能为空"}), 400
    
    product_ids = data['product_ids']
    new_status = data['status']
    valid_statuses = ['on_sale', 'off_sale']
    
    if new_status not in valid_statuses:
        return jsonify({"code": 400, "message": "无效的状态"}), 400
    
    if not isinstance(product_ids, list) or len(product_ids) == 0:
        return jsonify({"code": 400, "message": "商品ID列表不能为空"}), 400
    
    # 批量更新商品状态
    updated_count = 0
    failed_count = 0
    
    for product_id in product_ids:
        product = Product.query.get(product_id)
        if product:
            # 只有审核通过的商品才能上架
            if new_status == 'on_sale' and product.status != 'approved':
                failed_count += 1
                continue
                
            product.status = new_status
            product.updated_at = datetime.utcnow()
            updated_count += 1
        else:
            failed_count += 1
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": f"批量{'上架' if new_status == 'on_sale' else '下架'}完成",
            "data": {
                "updated_count": updated_count,
                "failed_count": failed_count,
                "status": new_status,
                "status_text": get_status_text(new_status)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"批量操作失败: {str(e)}"}), 500

def get_status_text(status):
    """获取商品状态的中文描述"""
    status_map = {
        'pending': '待审核',
        'approved': '审核通过',
        'rejected': '审核拒绝',
        'on_sale': '已上架',
        'off_sale': '已下架'
    }
    return status_map.get(status, status)
