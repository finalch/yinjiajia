from flask import Blueprint, jsonify, request
from models import db, Product, Group, ProductSpec, ProductSpecCombination, Order, OrderItem, Review
from sqlalchemy import or_, func
import json

app_product_api = Blueprint('app_product_api', __name__, url_prefix='/api/app/product')

@app_product_api.route('/', methods=['GET'])
def get_products():
    """APP端-获取商品列表"""
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    group_id = request.args.get('group_id', type=int)
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, sales
    sort_order = request.args.get('sort_order', 'desc')  # asc, desc
    
    # 构建查询
    query = Product.query.filter(Product.status == 'on_sale')  # 只显示已上架商品
    
    # 分组筛选
    if group_id:
        query = query.filter(Product.group_id == group_id)
    
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
            images = [img.strip() for img in product.image_url.split('$%%$') if img.strip()]
        
        # 如果没有图片，添加默认图片
        # if not images:
        #     images = ['https://via.placeholder.com/400x300?text=商品图片']
        
        # 真实销量：统计已付款及之后状态的订单项数量
        sales_count = db.session.query(func.coalesce(func.sum(OrderItem.quantity), 0)) \
            .join(Order, Order.id == OrderItem.order_id) \
            .filter(
                OrderItem.product_id == product.id,
                Order.status.in_(['paid', 'shipped', 'delivered', 'completed'])
            ).scalar() or 0

        # 评分与评价数
        rating_avg, review_count = db.session.query(
            func.coalesce(func.avg(Review.rating), 0.0),
            func.count(Review.id)
        ).filter(Review.product_id == product.id).first()

        # 默认规格组合ID（若有规格则取第一个有效规格组合）
        default_spec_combination_id = None
        if product.has_specs:
            first_combo = ProductSpecCombination.query \
                .filter_by(product_id=product.id, status='active') \
                .order_by(ProductSpecCombination.id.asc()) \
                .first()
            if first_combo:
                default_spec_combination_id = first_combo.id

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
            'group_id': product.group_id,
            'group_name': product.group.name if product.group else '',
            'merchant_id': product.merchant_id,
            'merchant_name': product.merchant.name if product.merchant else '',
            'has_specs': product.has_specs,  # 是否有规格
            'sales_count': int(sales_count),
            'rating': float(rating_avg) if rating_avg else 0.0,
            'review_count': int(review_count) if review_count else 0,
            'default_spec_combination_id': default_spec_combination_id,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取商品列表成功',
        'data': {
            'list': products,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
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
    
    # 获取相关商品（同分组）
    related_products = Product.query.filter(
        Product.group_id == product.group_id,
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
        images = [img.strip() for img in product.image_url.split('$%%$') if img.strip()]
    
    # 如果没有图片，添加默认图片
    if not images:
        images = ['https://via.placeholder.com/400x300?text=商品图片']
    
    # 获取规格信息
    specs = []
    spec_combinations = []
    
    if product.has_specs:
        # 获取商品规格
        product_specs = ProductSpec.query.filter(
            ProductSpec.product_id == product.id
        ).order_by(ProductSpec.sort_order).all()
        
        for spec in product_specs:
            try:
                values = json.loads(spec.values)
                specs.append({
                    'id': spec.id,
                    'name': spec.name,
                    'values': values,
                    'sort_order': spec.sort_order
                })
            except json.JSONDecodeError:
                continue
        
        # 获取规格组合
        combinations = ProductSpecCombination.query.filter(
            ProductSpecCombination.product_id == product.id,
            ProductSpecCombination.status == 'active'
        ).all()
        
        for combo in combinations:
            try:
                spec_values = json.loads(combo.spec_values)
                spec_combinations.append({
                    'id': combo.id,
                    'spec_values': spec_values,
                    'price': float(combo.price),
                    'stock': combo.stock,
                    'image_url': combo.image_url,
                    'status': combo.status
                })
            except json.JSONDecodeError:
                continue
    
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'detail': product.detail,  # 商品详情（富文本）
        'price': float(product.price),
        'original_price': float(product.original_price) if product.original_price else None,
        'stock': product.stock,
        'images': images,  # 改为images数组
        'image_url': product.image_url,  # 保留原字段
        'video_url': product.video_url,
        'group_id': product.group_id,
        'group_name': product.group.name if product.group else '',
        'merchant_id': product.merchant_id,
        'merchant_name': product.merchant.name if product.merchant else '',
        'has_specs': product.has_specs,  # 是否有规格
        'specs': specs,  # 规格信息
        'spec_combinations': spec_combinations,  # 规格组合
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

@app_product_api.route('/groups', methods=['GET'])
def get_groups():
    """APP端-获取商品分组"""
    groups = Group.query.all()
    
    data = []
    for group in groups:
        # 统计该分组下的商品数量
        product_count = Product.query.filter(
            Product.group_id == group.id,
            Product.status == 'on_sale'
        ).count()
        
        data.append({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'icon_url': group.icon_url,
            'product_count': product_count,
            'created_at': group.created_at.isoformat() if group.created_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取分组列表成功',
        'data': data
    }), 200
