from flask import Blueprint, jsonify, request
from models import db, Product

web_product_api = Blueprint('web_product_api', __name__, url_prefix='/api/web/product')

@web_product_api.route('/', methods=['GET'])
def get_products():
    """WEB端-获取商品列表，支持条件筛选"""
    query = Product.query
    name = request.args.get('name', type=str)
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=str)
    merchant_id = request.args.get('merchant_id', type=int)

    if name:
        query = query.filter(Product.name.like(f"%{name}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if merchant_id:
        query = query.filter(Product.merchant_id == merchant_id)
    if status:
        query = query.filter(Product.status == status)

    products = query.order_by(Product.created_at.desc()).all()
    data = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'stock': p.stock,
            'image_url': p.image_url,
            'video_url': p.video_url,
            'category': p.category,
            'category_id': p.category_id,
            'merchant_id': p.merchant_id,
            'status': p.status,
            'created_at': p.created_at,
            'updated_at': p.updated_at
        } for p in products
    ]
    return jsonify({'products': data}), 200

@web_product_api.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """WEB端-获取商品详情"""
    product = Product.query.get_or_404(product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,
        'video_url': product.video_url,
        'category': product.category,
        'merchant_id': product.merchant_id,
        'created_at': product.created_at,
        'updated_at': product.updated_at
    }
    return jsonify({'product': data}), 200

@web_product_api.route('/upload-image', methods=['POST'])
def upload_image():
    # Mock实现，实际存储逻辑后续补充
    return jsonify({"url": "https://mock.cdn.com/your-image.jpg"})

@web_product_api.route('/', methods=['POST'])
def create_product():
    data = request.json
    data['image_url'] = 'http://gips2.baidu.com/it/u=1674525583,3037683813&fm=3028&app=3028&f=JPEG&fmt=auto?w=1024&h=1024';
    required_fields = ['name', 'price', 'stock', 'category_id', 'image_url', 'merchant_id']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"code": 400, "msg": f"{field} 不能为空"}), 400
    # 校验价格
    try:
        price = float(data['price'])
        if price <= 0:
            return jsonify({"code": 400, "msg": "价格必须为大于0的数字"}), 400
    except Exception:
        return jsonify({"code": 400, "msg": "价格必须为数字"}), 400
    # 校验库存
    try:
        stock = int(data['stock'])
        if stock < 0:
            return jsonify({"code": 400, "msg": "库存必须为不小于0的整数"}), 400
    except Exception:
        return jsonify({"code": 400, "msg": "库存必须为整数"}), 400
    # 校验分类和商家是否存在
    from models import Category, Merchant
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({"code": 404, "msg": "分类不存在"}), 404
    merchant = Merchant.query.get(data['merchant_id'])
    if not merchant:
        return jsonify({"code": 404, "msg": "商家不存在"}), 404
    # 创建商品，status 默认为 'pending'
    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=price,
        stock=stock,
        image_url=data['image_url'],
        category_id=data['category_id'],
        merchant_id=data['merchant_id'],
        status='pending'
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"code": 200, "msg": "商品发布成功", "product_id": product.id})
