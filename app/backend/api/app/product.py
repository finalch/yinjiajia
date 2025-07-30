from flask import Blueprint, jsonify, request
from models import db, Product, Category
from sqlalchemy import or_

app_product_api = Blueprint('app_product_api', __name__, url_prefix='/api/app/product')

@app_product_api.route('/', methods=['GET'])
def get_products():
    """APP端-获取商品列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, sales
    sort_order = request.args.get('sort_order', 'desc')  # asc, desc
    
    # 构建查询
    query = Product.query.filter(Product.status == 'on_sale')  # 只显示已上架商品
    
    # 分类筛选
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                Product.name.contains(search),
                Product.description.contains(search)
            )
        )
    
    # 价格筛选
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # 排序
    if sort_by == 'price':
        order_column = Product.price
    elif sort_by == 'sales':
        # 这里可以添加销量字段，暂时用创建时间
        order_column = Product.created_at
    else:
        order_column = Product.created_at
    
    if sort_order == 'asc':
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    # 分页
    pagination = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    # 构建返回数据
    products = []
    for product in pagination.items:
        # 处理图片数组，如果有多个图片用逗号分隔
        images = []
        if product.image_url:
            images = [img.strip() for img in product.image_url.split(',') if img.strip()]
        
        # 如果没有图片，添加默认图片
        if not images:
            images = ['https://via.placeholder.com/400x300?text=商品图片']
        
        products.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'original_price': float(product.original_price) if product.original_price else None,
            'stock': product.stock,
            'images': images,  # 改为images数组
            'image_url': product.image_url,  # 保留原字段
            'video_url': product.video_url,
            'category_id': product.category_id,
            'category_name': product.category.name if product.category else '',
            'merchant_id': product.merchant_id,
            'merchant_name': product.merchant.name if product.merchant else '',
            'sales_count': 0,  # TODO: 添加销量统计
            'rating': 4.5,  # TODO: 添加评分统计
            'review_count': 0,  # TODO: 添加评价数量统计
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取商品列表成功',
        'data': {
            'list': products,
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

@app_product_api.route('/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """APP端-获取商品详情"""
    product = Product.query.get_or_404(product_id)
    
    # 检查商品是否上架
    if product.status != 'on_sale':
        return jsonify({
            'code': 404,
            'message': '商品不存在或已下架'
        }), 404
    
    # 获取相关商品（同分类）
    related_products = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.status == 'on_sale'
    ).limit(6).all()
    
    related_data = []
    for p in related_products:
        related_data.append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image_url': p.image_url
        })
    
    # 处理图片数组，如果有多个图片用逗号分隔
    images = []
    if product.image_url:
        images = [img.strip() for img in product.image_url.split(',') if img.strip()]
    
    # 如果没有图片，添加默认图片
    if not images:
        images = ['https://via.placeholder.com/400x300?text=商品图片']
    
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price),
        'original_price': float(product.original_price) if product.original_price else None,
        'stock': product.stock,
        'images': images,  # 改为images数组
        'image_url': product.image_url,  # 保留原字段
        'video_url': product.video_url,
        'category_id': product.category_id,
        'category_name': product.category.name if product.category else '',
        'merchant_id': product.merchant_id,
        'merchant_name': product.merchant.name if product.merchant else '',
        'sales_count': 0,  # TODO: 添加销量统计
        'rating': 4.5,  # TODO: 添加评分统计
        'review_count': 0,  # TODO: 添加评价数量统计
        'created_at': product.created_at.isoformat() if product.created_at else None,
        'updated_at': product.updated_at.isoformat() if product.updated_at else None,
        'related_products': related_data
    }
    
    return jsonify({
        'code': 200,
        'message': '获取商品详情成功',
        'data': data
    }), 200

@app_product_api.route('/categories', methods=['GET'])
def get_categories():
    """APP端-获取商品分类"""
    categories = Category.query.all()
    
    data = []
    for category in categories:
        # 统计该分类下的商品数量
        product_count = Product.query.filter(
            Product.category_id == category.id,
            Product.status == 'on_sale'
        ).count()
        
        data.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'icon_url': category.icon_url,
            'product_count': product_count,
            'created_at': category.created_at.isoformat() if category.created_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取分类列表成功',
        'data': data
    }), 200
