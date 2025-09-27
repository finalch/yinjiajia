from flask import Blueprint, jsonify, request, g
from datetime import datetime
from models import db, Review, OrderItem, Order, Product, User
from config.log import get_logger

logger = get_logger(__name__)

app_review_api = Blueprint('app_review_api', __name__, url_prefix='/api/app/review')


@app_review_api.route('/', methods=['POST'])
def add_review():
    """APP端-用户添加评价接口"""
    data = request.json or {}
    user_id = g.user_id
    
    order_item_id = data.get('order_item_id')
    rating = data.get('rating')
    content = data.get('content', '')
    
    # 参数验证
    if not order_item_id:
        return jsonify({'code': 400, 'message': '订单项ID不能为空'}), 400
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'code': 400, 'message': '评分必须在1-5之间'}), 400
    
    try:
        # 检查订单项是否存在且属于当前用户
        order_item = OrderItem.query.join(Order).filter(
            OrderItem.id == order_item_id,
            Order.user_id == user_id
        ).first()
        
        if not order_item:
            return jsonify({'code': 404, 'message': '订单项不存在'}), 404
        
        # 检查订单是否已完成
        if order_item.order.status != 'completed':
            return jsonify({'code': 400, 'message': '只有已完成的订单才能评价'}), 400
        
        # 检查是否已经评价过
        existing_review = Review.query.filter_by(
            order_item_id=order_item_id,
            user_id=user_id
        ).first()
        
        if existing_review:
            return jsonify({'code': 400, 'message': '该商品已经评价过了'}), 400
        
        # 创建评价
        review = Review(
            user_id=user_id,
            order_item_id=order_item_id,
            product_id=order_item.product_id,
            rating=rating,
            content=content.strip() if content else None
        )
        
        # 更新订单项的评价状态
        now = datetime.utcnow()
        order_item.is_reviewed = True
        order_item.reviewed_at = now
        
        db.session.add(review)
        db.session.commit()
        
        logger.info(f"用户评价成功: user_id={user_id}, order_item_id={order_item_id}, rating={rating}")
        
        return jsonify({
            'code': 200,
            'message': '评价成功',
            'data': {
                'review_id': review.id,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"添加评价失败: {str(e)}, user_id={user_id}, order_item_id={order_item_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'添加评价失败: {str(e)}'
        }), 500


@app_review_api.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """APP端-获取商品评价列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        # 检查商品是否存在
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'code': 404, 'message': '商品不存在'}), 404
        
        # 获取评价列表
        reviews_query = Review.query.join(OrderItem).filter(OrderItem.product_id == product_id).order_by(Review.created_at.desc())
        
        pagination = reviews_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        reviews = []
        for review in pagination.items:
            reviews.append({
                'id': review.id,
                'user_name': review.user.username if review.user else '匿名用户',
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.isoformat(),
                'image_url': review.image_url,
                'video_url': review.video_url
            })
        
        # 计算平均评分和总评价数
        from sqlalchemy import func
        rating_stats = db.session.query(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('total_count')
        ).join(OrderItem).filter(OrderItem.product_id == product_id).first()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'reviews': reviews,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next
                },
                'stats': {
                    'avg_rating': round(float(rating_stats.avg_rating or 0), 1),
                    'total_count': rating_stats.total_count or 0
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取商品评价失败: {str(e)}, product_id={product_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'获取商品评价失败: {str(e)}'
        }), 500


@app_review_api.route('/check/<int:order_item_id>', methods=['GET'])
def check_review_status(order_item_id):
    """APP端-检查订单项是否已评价"""
    user_id = g.user_id
    
    try:
        # 检查订单项是否存在且属于当前用户
        order_item = OrderItem.query.join(Order).filter(
            OrderItem.id == order_item_id,
            Order.user_id == user_id
        ).first()
        
        if not order_item:
            return jsonify({'code': 404, 'message': '订单项不存在'}), 404
        
        # 检查是否已评价（优先使用order_item的is_reviewed字段）
        has_reviewed = order_item.is_reviewed
        existing_review = None
        
        if has_reviewed:
            # 如果已评价，获取评价详情
            existing_review = Review.query.filter_by(
                order_item_id=order_item_id,
                user_id=user_id
            ).first()
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'order_item_id': order_item_id,
                'product_id': order_item.product_id,
                'product_name': order_item.product.name if order_item.product else '未知商品',
                'can_review': order_item.order.status == 'completed' and not has_reviewed,
                'has_reviewed': has_reviewed,
                'review_id': existing_review.id if existing_review else None,
                'review_rating': existing_review.rating if existing_review else None,
                'review_content': existing_review.content if existing_review else None,
                'review_created_at': existing_review.created_at.isoformat() if existing_review else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"检查评价状态失败: {str(e)}, user_id={user_id}, order_item_id={order_item_id}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': f'检查评价状态失败: {str(e)}'
        }), 500
