from flask import Blueprint, jsonify, request, g
from models import db, Order, OrderItem, Product, Review, Group
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from config.log import get_logger

web_analytics_api = Blueprint('web_analytics_api', __name__, url_prefix='/api/web/analytics')
logger = get_logger(__name__)
@web_analytics_api.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """WEB端-获取仪表板数据"""
    # merchant_id = request.args.get('merchant_id', type=int)
            # logger.error(f"merchant_id:", type(g.merchant_id))
    merchant_id = g.merchant_id
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    revenue_statuses = ['paid', 'shipped', 'delivered', 'completed']

    # 今日数据（按商家维度去重订单 + 订单项小计）
    today_orders = db.session.query(func.count(func.distinct(Order.id))) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            func.date(Order.created_at) == today
        ).scalar() or 0

    today_sales = db.session.query(func.sum(OrderItem.subtotal)) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            func.date(Order.created_at) == today,
            Order.status.in_(revenue_statuses)
        ).scalar() or 0

    today_products = Product.query.filter(
        Product.merchant_id == merchant_id,
        func.date(Product.created_at) == today
    ).count()

    # 昨日数据
    yesterday_orders = db.session.query(func.count(func.distinct(Order.id))) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            func.date(Order.created_at) == yesterday
        ).scalar() or 0

    yesterday_sales = db.session.query(func.sum(OrderItem.subtotal)) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            func.date(Order.created_at) == yesterday,
            Order.status.in_(revenue_statuses)
        ).scalar() or 0

    # 本月数据
    this_month_orders = db.session.query(func.count(func.distinct(Order.id))) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            Order.created_at >= this_month_start
        ).scalar() or 0

    this_month_sales = db.session.query(func.sum(OrderItem.subtotal)) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            Order.created_at >= this_month_start,
            Order.status.in_(revenue_statuses)
        ).scalar() or 0

    # 总商品数
    total_products = Product.query.filter(Product.merchant_id == merchant_id).count()

    # 总订单数（去重）
    total_orders = db.session.query(func.count(func.distinct(Order.id))) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(OrderItem.merchant_id == merchant_id).scalar() or 0

    # 总销售额（订单项小计）
    total_sales = db.session.query(func.sum(OrderItem.subtotal)) \
        .select_from(OrderItem) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(
            OrderItem.merchant_id == merchant_id,
            Order.status.in_(revenue_statuses)
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

    # 分组销售统计
    group_sales = db.session.query(
        Group.name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total_amount).label('total_sales')
    ).join(
        Product, Group.id == Product.group_id
    ).join(
        Order, Product.id == Order.id  # 需要根据实际关联关系调整
    ).filter(
        Group.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).group_by(Group.id).all()

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
            "group_sales": [
                {
                    'name': item.name,
                    'order_count': item.order_count,
                    'total_sales': float(item.total_sales or 0)
                } for item in group_sales
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

@web_analytics_api.route('/trends', methods=['GET'])
def get_trends_analytics():
    """WEB端-获取趋势分析数据（销售额、订单数）"""
    merchant_id = g.merchant_id
    period = request.args.get('period', '7d')  # 7d, 30d, 90d
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400

    today = datetime.utcnow().date()
    
    # 根据period确定天数
    if period == '7d':
        days = 7
    elif period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    else:
        days = 7
    
    start_date = today - timedelta(days=days-1)  # 包含今天，所以减days-1
    
    # 定义有效的订单状态
    valid_statuses = ['paid', 'shipped', 'delivered', 'completed']
    
    # 查询每日的销售额和订单数
    daily_stats = db.session.query(
        func.date(Order.created_at).label('date'),
        func.count(func.distinct(Order.id)).label('order_count'),
        func.sum(OrderItem.subtotal).label('sales_amount')
    ).select_from(OrderItem).join(
        Order, Order.id == OrderItem.order_id
    ).filter(
        OrderItem.merchant_id == merchant_id,
        Order.created_at >= start_date,
        Order.status.in_(valid_statuses)
    ).group_by(
        func.date(Order.created_at)
    ).all()
    
    # 创建日期到数据的映射
    stats_map = {item.date: {'orders': item.order_count, 'sales': item.sales_amount or 0} for item in daily_stats}
    
    # 填充完整的日期范围数据
    trends_data = []
    total_orders = 0
    total_sales = 0.0
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')
        
        if current_date in stats_map:
            daily_orders = stats_map[current_date]['orders']
            daily_sales = float(stats_map[current_date]['sales'])
        else:
            daily_orders = 0
            daily_sales = 0.0
        
        trends_data.append({
            'date': date_str,
            'orders': daily_orders,
            'sales': daily_sales
        })
        
        total_orders += daily_orders
        total_sales += daily_sales
    
    # # 计算平均值
    # avg_orders = total_orders / days if days > 0 else 0
    # avg_sales = total_sales / days if days > 0 else 0
    
    # # 计算增长率（与上一个周期比较）
    # if period == '7d':
    #     prev_period_days = 7
    # elif period == '30d':
    #     prev_period_days = 30
    # elif period == '90d':
    #     prev_period_days = 90
    # else:
    #     prev_period_days = 7
    
    # prev_start_date = start_date - timedelta(days=prev_period_days)
    
    # # 查询上一个周期的数据
    # prev_period_stats = db.session.query(
    #     func.count(func.distinct(Order.id)).label('order_count'),
    #     func.sum(OrderItem.subtotal).label('sales_amount')
    # ).select_from(OrderItem).join(
    #     Order, Order.id == OrderItem.order_id
    # ).filter(
    #     OrderItem.merchant_id == merchant_id,
    #     Order.created_at >= prev_start_date,
    #     Order.created_at < start_date,
    #     Order.status.in_(valid_statuses)
    # ).first()
    
    # prev_orders = prev_period_stats.order_count or 0
    # prev_sales = float(prev_period_stats.sales_amount or 0)
    
    # # 计算增长率
    # order_growth_rate = 0
    # sales_growth_rate = 0
    
    # if prev_orders > 0:
    #     order_growth_rate = ((total_orders - prev_orders) / prev_orders) * 100
    
    # if prev_sales > 0:
    #     sales_growth_rate = ((total_sales - prev_sales) / prev_sales) * 100
    
    return jsonify({
        "code": 200,
        "message": "获取趋势分析数据成功",
        "data": {
            "period": period,
            # "summary": {
            #     "total_orders": total_orders,
            #     "total_sales": round(total_sales, 2),
            #     "avg_orders": round(avg_orders, 2),
            #     "avg_sales": round(avg_sales, 2),
            #     "order_growth_rate": round(order_growth_rate, 2),
            #     "sales_growth_rate": round(sales_growth_rate, 2)
            # },
            "trends": trends_data
        }
    }), 200

@web_analytics_api.route('/trends/compare', methods=['GET'])
def get_trends_comparison():
    """WEB端-获取多周期趋势对比数据"""
    merchant_id = g.merchant_id
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400

    today = datetime.utcnow().date()
    valid_statuses = ['paid', 'shipped', 'delivered', 'completed']
    
    # 定义要比较的周期
    periods = [
        {'name': '7d', 'days': 7},
        {'name': '30d', 'days': 30},
        {'name': '90d', 'days': 90}
    ]
    
    comparison_data = {}
    
    for period in periods:
        days = period['days']
        start_date = today - timedelta(days=days-1)
        
        # 查询该周期的统计数据
        stats = db.session.query(
            func.count(func.distinct(Order.id)).label('order_count'),
            func.sum(OrderItem.subtotal).label('sales_amount')
        ).select_from(OrderItem).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            OrderItem.merchant_id == merchant_id,
            Order.created_at >= start_date,
            Order.status.in_(valid_statuses)
        ).first()
        
        comparison_data[period['name']] = {
            'orders': stats.order_count or 0,
            'sales': float(stats.sales_amount or 0),
            'avg_orders': round((stats.order_count or 0) / days, 2),
            'avg_sales': round(float(stats.sales_amount or 0) / days, 2)
        }
    
    return jsonify({
        "code": 200,
        "message": "获取趋势对比数据成功",
        "data": comparison_data
    }), 200