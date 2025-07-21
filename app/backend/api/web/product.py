from flask import Blueprint, jsonify, request
from models import db, Product

web_product_api = Blueprint('web_product_api', __name__, url_prefix='/api/web/product')

@web_product_api.route('/', methods=['GET'])
def get_products():
    """WEB端-获取商品列表"""
    products = Product.query.all()
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
            'merchant_id': p.merchant_id,
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

@web_product_api.route('/', methods=['POST'])
def create_product():
    """WEB端-新增商品"""
    data = request.json
    product = Product(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        image_url=data.get('image_url'),
        video_url=data.get('video_url'),
        category=data.get('category'),
        merchant_id=data.get('merchant_id')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': '商品创建成功', 'product_id': product.id}), 201
