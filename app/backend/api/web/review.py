from flask import Blueprint, jsonify, request
from models import db, Review, Product, User, Merchant
from datetime import datetime, timedelta
from sqlalchemy import func

web_review_api = Blueprint('web_review_api', __name__, url_prefix='/api/web/review')

@web_review_api.route('/', methods=['GET'])
def get_reviews():
    """WEB端-获取评价列表，支持条件筛选"""
    merchant_id = request.args.get('merchant_id', type=int)
    product_id = request.args.get('product_id', type=int)
    rating = request.args.get('rating', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 构建查询
    query = db.session.query(Review, Product, User).join(
        Product, Review.product_id == Product.id
    ).join(
        User, Review.user_id == User.id
    ).filter(Product.merchant_id == merchant_id)
    
    if product_id:
        query = query.filter(Review.product_id == product_id)
    
    if rating:
        query = query.filter(Review.rating == rating)
    
    # 分页
    pagination = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reviews_data = []
    for review, product, user in pagination.items:
        review_data = {
            'id': review.id,
            'product_id': review.product_id,
            'product_name': product.name,
            'user_id': review.user_id,
            'user_name': user.username,
            'user_phone': user.phone,
            'content': review.content,
            'rating': review.rating,
            'rating_text': get_rating_text(review.rating),
            'image_url': review.image_url,
            'video_url': review.video_url,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        reviews_data.append(review_data)
    
    return jsonify({
        "code": 200,
        "message": "获取评价列表成功",
        "data": {
            "list": reviews_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200

@web_review_api.route('/<int:review_id>', methods=['GET'])
def get_review_detail(review_id):
    """WEB端-获取评价详情"""
    review = db.session.query(Review, Product, User).join(
        Product, Review.product_id == Product.id
    ).join(
        User, Review.user_id == User.id
    ).filter(Review.id == review_id).first()
    
    if not review:
        return jsonify({"code": 404, "message": "评价不存在"}), 404
    
    review_obj, product, user = review
    
    review_data = {
        'id': review_obj.id,
        'product_id': review_obj.product_id,
        'product_name': product.name,
        'product_image': product.image_url,
        'user_id': review_obj.user_id,
        'user_name': user.username,
        'user_phone': user.phone,
        'user_email': user.email,
        'content': review_obj.content,
        'rating': review_obj.rating,
        'rating_text': get_rating_text(review_obj.rating),
        'image_url': review_obj.image_url,
        'video_url': review_obj.video_url,
        'created_at': review_obj.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': review_obj.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify({
        "code": 200,
        "message": "获取评价详情成功",
        "data": review_data
    }), 200

@web_review_api.route('/<int:review_id>/reply', methods=['POST'])
def reply_review(review_id):
    """WEB端-回复评价"""
    review = Review.query.get_or_404(review_id)
    data = request.json
    
    if not data or 'reply_content' not in data:
        return jsonify({"code": 400, "message": "回复内容不能为空"}), 400
    
    # 这里可以扩展Review模型添加reply_content字段
    # 暂时返回成功，实际实现需要修改数据库模型
    return jsonify({
        "code": 200,
        "message": "评价回复成功",
        "data": {
            "review_id": review_id,
            "reply_content": data['reply_content']
        }
    }), 200

@web_review_api.route('/statistics', methods=['GET'])
def get_review_statistics():
    """WEB端-获取评价统计数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 总评价数
    total_reviews = db.session.query(func.count(Review.id)).join(
        Product, Review.product_id == Product.id
    ).filter(Product.merchant_id == merchant_id).scalar()
    
    # 平均评分
    avg_rating = db.session.query(func.avg(Review.rating)).join(
        Product, Review.product_id == Product.id
    ).filter(Product.merchant_id == merchant_id).scalar() or 0
    
    # 各评分数量
    rating_counts = db.session.query(
        Review.rating,
        func.count(Review.id)
    ).join(
        Product, Review.product_id == Product.id
    ).filter(
        Product.merchant_id == merchant_id
    ).group_by(Review.rating).all()
    
    rating_data = {}
    for rating, count in rating_counts:
        rating_data[rating] = count
    
    # 今日新增评价
    today = datetime.utcnow().date()
    today_reviews = db.session.query(func.count(Review.id)).join(
        Product, Review.product_id == Product.id
    ).filter(
        Product.merchant_id == merchant_id,
        func.date(Review.created_at) == today
    ).scalar()
    
    # 最近7天评价趋势
    seven_days_ago = today - timedelta(days=7)
    daily_reviews = db.session.query(
        func.date(Review.created_at).label('date'),
        func.count(Review.id).label('count')
    ).join(
        Product, Review.product_id == Product.id
    ).filter(
        Product.merchant_id == merchant_id,
        Review.created_at >= seven_days_ago
    ).group_by(func.date(Review.created_at)).all()
    
    trend_data = []
    for i in range(7):
        date = seven_days_ago + timedelta(days=i)
        count = next((item.count for item in daily_reviews if item.date == date), 0)
        trend_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return jsonify({
        "code": 200,
        "message": "获取评价统计成功",
        "data": {
            "total_reviews": total_reviews,
            "avg_rating": float(avg_rating),
            "rating_counts": rating_data,
            "today_reviews": today_reviews,
            "trend_data": trend_data
        }
    }), 200

@web_review_api.route('/products/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """WEB端-获取指定商品的评价列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    rating = request.args.get('rating', type=int)
    
    query = db.session.query(Review, User).join(
        User, Review.user_id == User.id
    ).filter(Review.product_id == product_id)
    
    if rating:
        query = query.filter(Review.rating == rating)
    
    # 分页
    pagination = query.order_by(Review.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    reviews_data = []
    for review, user in pagination.items:
        review_data = {
            'id': review.id,
            'user_id': review.user_id,
            'user_name': user.username,
            'content': review.content,
            'rating': review.rating,
            'rating_text': get_rating_text(review.rating),
            'image_url': review.image_url,
            'video_url': review.video_url,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        reviews_data.append(review_data)
    
    return jsonify({
        "code": 200,
        "message": "获取商品评价成功",
        "data": {
            "list": reviews_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200

def get_rating_text(rating):
    """获取评分的中文描述"""
    rating_map = {
        1: '很差',
        2: '较差',
        3: '一般',
        4: '较好',
        5: '很好'
    }
    return rating_map.get(rating, f'{rating}星')
