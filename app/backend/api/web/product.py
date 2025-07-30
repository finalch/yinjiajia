from flask import Blueprint, jsonify, request
from models import db, Product, Category, Merchant
from datetime import datetime
from sqlalchemy import func

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
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'video_url': product.video_url,
        'category': product.category,
        'category_id': product.category_id,
        'category_name': category.name if category else '',
        'merchant_id': product.merchant_id,
        'merchant_name': merchant.name if merchant else '',
        'status': product.status,
        'status_text': get_status_text(product.status),
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({
        "code": 200,
        "message": "获取商品详情成功",
        "data": data
    }), 200

@web_product_api.route('/upload-image', methods=['POST'])
def upload_image():
    # Mock实现，实际存储逻辑后续补充
    return jsonify({"url": "https://mock.cdn.com/your-image.jpg"})

@web_product_api.route('/', methods=['POST'])
def create_product():
    """WEB端-创建商品"""
    data = request.json
    
    required_fields = ['name', 'price', 'stock', 'category_id', 'merchant_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"code": 400, "message": f"{field} 不能为空"}), 400
    
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
    
    # 校验分类和商家是否存在
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({"code": 404, "message": "分类不存在"}), 404
    
    merchant = Merchant.query.get(data['merchant_id'])
    if not merchant:
        return jsonify({"code": 404, "message": "商家不存在"}), 404
    
    # 创建商品，status 默认为 'pending'
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=price,
        stock=stock,
        image_url=data.get('image_url', ''),
        video_url=data.get('video_url', ''),
        category_id=data['category_id'],
        merchant_id=data['merchant_id'],
        status='pending'  # 新商品默认为待审核状态
    )
    
    try:
        db.session.add(product)
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
    
    # 更新商品信息
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
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
    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({"code": 404, "message": "分类不存在"}), 404
        product.category_id = data['category_id']
    if 'image_url' in data:
        product.image_url = data['image_url']
    if 'video_url' in data:
        product.video_url = data['video_url']
    
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
