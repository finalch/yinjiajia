from flask import Blueprint, jsonify, request
from models import db, Order, Product, Review, Category
from datetime import datetime, timedelta
from sqlalchemy import func, and_

web_analytics_api = Blueprint('web_analytics_api', __name__, url_prefix='/api/web/analytics')

@web_analytics_api.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """WEB端-获取仪表板数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # 今日数据
    today_orders = Order.query.filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today
    ).count()
    
    today_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    today_products = Product.query.filter(
        Product.merchant_id == merchant_id,
        func.date(Product.created_at) == today
    ).count()
    
    # 昨日数据
    yesterday_orders = Order.query.filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == yesterday
    ).count()
    
    yesterday_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == yesterday,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 本月数据
    this_month_orders = Order.query.filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= this_month_start
    ).count()
    
    this_month_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= this_month_start,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 总商品数
    total_products = Product.query.filter(Product.merchant_id == merchant_id).count()
    
    # 总订单数
    total_orders = Order.query.filter(Order.merchant_id == merchant_id).count()
    
    # 总销售额
    total_sales = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 平均评分
    avg_rating = db.session.query(func.avg(Review.rating)).join(
        Product, Review.product_id == Product.id
    ).filter(Product.merchant_id == merchant_id).scalar() or 0
    
    return jsonify({
        "code": 200,
        "message": "获取仪表板数据成功",
        "data": {
            "today": {
                "orders": today_orders,
                "sales": float(today_sales),
                "products": today_products
            },
            "yesterday": {
                "orders": yesterday_orders,
                "sales": float(yesterday_sales)
            },
            "this_month": {
                "orders": this_month_orders,
                "sales": float(this_month_sales)
            },
            "total": {
                "products": total_products,
                "orders": total_orders,
                "sales": float(total_sales),
                "avg_rating": float(avg_rating)
            }
        }
    }), 200

@web_analytics_api.route('/sales', methods=['GET'])
def get_sales_analytics():
    """WEB端-获取销售分析数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    period = request.args.get('period', '7d')  # 7d, 30d, 90d
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    today = datetime.utcnow().date()
    
    if period == '7d':
        days = 7
    elif period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    else:
        days = 7
    
    start_date = today - timedelta(days=days)
    
    # 每日销售数据
    daily_sales = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(Order.id).label('orders'),
        func.sum(Order.total_amount).label('sales')
    ).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= start_date,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(func.date(Order.created_at)).all()
    
    # 填充缺失的日期
    sales_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        daily_data = next((item for item in daily_sales if item.date == date), None)
        
        if daily_data:
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'orders': daily_data.orders,
                'sales': float(daily_data.sales or 0)
            })
        else:
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'orders': 0,
                'sales': 0.0
            })
    
    # 销售统计
    total_sales = sum(item['sales'] for item in sales_data)
    total_orders = sum(item['orders'] for item in sales_data)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    return jsonify({
        "code": 200,
        "message": "获取销售分析成功",
        "data": {
            "period": period,
            "total_sales": total_sales,
            "total_orders": total_orders,
            "avg_order_value": avg_order_value,
            "daily_data": sales_data
        }
    }), 200

@web_analytics_api.route('/products', methods=['GET'])
def get_product_analytics():
    """WEB端-获取商品分析数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 商品销量排行
    product_sales = db.session.query(
        Product.id,
        Product.name,
        Product.image_url,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_sales')
    ).join(
        Order, Product.id == Order.id  # 这里需要根据实际订单商品关联关系调整
    ).filter(
        Product.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(Product.id).order_by(
        func.count(Order.id).desc()
    ).limit(limit).all()
    
    # 商品评价排行
    product_reviews = db.session.query(
        Product.id,
        Product.name,
        Product.image_url,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(
        Review, Product.id == Review.product_id
    ).filter(
        Product.merchant_id == merchant_id
    ).group_by(Product.id).order_by(
        func.avg(Review.rating).desc()
    ).limit(limit).all()
    
    # 分类销售统计
    category_sales = db.session.query(
        Category.name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_sales')
    ).join(
        Product, Category.id == Product.category_id
    ).join(
        Order, Product.id == Order.id  # 需要根据实际关联关系调整
    ).filter(
        Category.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(Category.id).all()
    
    return jsonify({
        "code": 200,
        "message": "获取商品分析成功",
        "data": {
            "top_selling_products": [
                {
                    'id': item.id,
                    'name': item.name,
                    'image_url': item.image_url,
                    'order_count': item.order_count,
                    'total_sales': float(item.total_sales or 0)
                } for item in product_sales
            ],
            "top_rated_products": [
                {
                    'id': item.id,
                    'name': item.name,
                    'image_url': item.image_url,
                    'avg_rating': float(item.avg_rating or 0),
                    'review_count': item.review_count
                } for item in product_reviews
            ],
            "category_sales": [
                {
                    'name': item.name,
                    'order_count': item.order_count,
                    'total_sales': float(item.total_sales or 0)
                } for item in category_sales
            ]
        }
    }), 200

@web_analytics_api.route('/revenue', methods=['GET'])
def get_revenue_analytics():
    """WEB端-获取收入分析数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # 本月收入
    this_month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= this_month_start,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 上月收入
    last_month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= last_month_start,
        Order.created_at < this_month_start,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 收入增长率
    growth_rate = 0
    if last_month_revenue > 0:
        growth_rate = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    # 每日收入趋势（最近30天）
    thirty_days_ago = today - timedelta(days=30)
    daily_revenue = db.session.query(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= thirty_days_ago,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(func.date(Order.created_at)).all()
    
    # 填充缺失的日期
    revenue_data = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        daily_data = next((item for item in daily_revenue if item.date == date), None)
        
        if daily_data:
            revenue_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': float(daily_data.revenue or 0)
            })
        else:
            revenue_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'revenue': 0.0
            })
    
    return jsonify({
        "code": 200,
        "message": "获取收入分析成功",
        "data": {
            "this_month_revenue": float(this_month_revenue),
            "last_month_revenue": float(last_month_revenue),
            "growth_rate": round(growth_rate, 2),
            "daily_revenue": revenue_data
        }
    }), 200 