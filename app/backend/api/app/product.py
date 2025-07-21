from flask import Blueprint, jsonify, request
from models import db, Product

app_product_api = Blueprint('app_product_api', __name__, url_prefix='/api/app/product')

@app_product_api.route('/', methods=['GET'])
def get_products():
    """APP端-获取商品列表"""
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

@app_product_api.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """APP端-获取商品详情"""
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
