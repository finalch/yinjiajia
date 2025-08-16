from flask import Blueprint, jsonify, request
from models import db, User, Merchant, Product
from datetime import datetime, timedelta
from sqlalchemy import func

web_customer_service_api = Blueprint('web_customer_service_api', __name__, url_prefix='/api/web/customer_service')

# 模拟客服消息数据（实际应该创建数据库表）
customer_messages = []
quick_replies = [
    {"id": 1, "content": "您好，请问有什么可以帮助您的吗？", "group": "greeting"},
    {"id": 2, "content": "感谢您的咨询，我们会尽快为您处理。", "group": "thanks"},
    {"id": 3, "content": "关于发货时间，我们会在24小时内发出。", "group": "shipping"},
    {"id": 4, "content": "如果商品有质量问题，我们支持7天无理由退换。", "group": "return"},
    {"id": 5, "content": "您可以通过订单号查询物流信息。", "group": "logistics"}
]

@web_customer_service_api.route('/messages', methods=['GET'])
def get_customer_messages():
    """WEB端-获取客服消息列表"""
    merchant_id = request.args.get('merchant_id', type=int)
    status = request.args.get('status', type=str)  # pending, replied, closed
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 模拟消息数据（实际应该从数据库查询）
    messages = [
        {
            'id': 1,
            'user_id': 1,
            'user_name': '张三',
            'user_phone': '13800138001',
            'message': '请问这个商品什么时候发货？',
            'status': 'pending',
            'created_at': '2024-01-15 10:30:00',
            'replied_at': None,
            'reply_content': None
        },
        {
            'id': 2,
            'user_id': 2,
            'user_name': '李四',
            'user_phone': '13800138002',
            'message': '商品质量有问题，可以退换吗？',
            'status': 'replied',
            'created_at': '2024-01-15 09:15:00',
            'replied_at': '2024-01-15 09:30:00',
            'reply_content': '您好，我们支持7天无理由退换，请提供订单号，我们会尽快为您处理。'
        }
    ]
    
    # 筛选
    if status:
        messages = [msg for msg in messages if msg['status'] == status]
    
    # 分页
    total = len(messages)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_messages = messages[start:end]
    
    return jsonify({
        "code": 200,
        "message": "获取客服消息成功",
        "data": {
            "list": paginated_messages,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }
    }), 200

@web_customer_service_api.route('/messages/<int:message_id>', methods=['GET'])
def get_message_detail(message_id):
    """WEB端-获取消息详情"""
    # 模拟消息详情
    message_detail = {
        'id': message_id,
        'user_id': 1,
        'user_name': '张三',
        'user_phone': '13800138001',
        'user_email': 'zhangsan@example.com',
        'message': '请问这个商品什么时候发货？',
        'status': 'pending',
        'created_at': '2024-01-15 10:30:00',
        'replied_at': None,
        'reply_content': None,
        'product_info': {
            'id': 1,
            'name': 'iPhone 15 Pro',
            'image_url': 'https://example.com/iphone.jpg'
        }
    }
    
    return jsonify({
        "code": 200,
        "message": "获取消息详情成功",
        "data": message_detail
    }), 200

@web_customer_service_api.route('/messages/<int:message_id>/reply', methods=['POST'])
def reply_message(message_id):
    """WEB端-回复消息"""
    data = request.json
    
    if not data or 'reply_content' not in data:
        return jsonify({"code": 400, "message": "回复内容不能为空"}), 400
    
    # 模拟回复操作
    reply_data = {
        'message_id': message_id,
        'reply_content': data['reply_content'],
        'replied_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'replied'
    }
    
    return jsonify({
        "code": 200,
        "message": "回复成功",
        "data": reply_data
    }), 200

@web_customer_service_api.route('/quick-replies', methods=['GET'])
def get_quick_replies():
    """WEB端-获取快捷回复列表"""
    group = request.args.get('group', type=str)
    
    if group:
        filtered_replies = [reply for reply in quick_replies if reply['group'] == group]
    else:
        filtered_replies = quick_replies
    
    return jsonify({
        "code": 200,
        "message": "获取快捷回复成功",
        "data": filtered_replies
    }), 200

@web_customer_service_api.route('/quick-replies', methods=['POST'])
def add_quick_reply():
    """WEB端-添加快捷回复"""
    data = request.json
    
    if not data or 'content' not in data:
        return jsonify({"code": 400, "message": "回复内容不能为空"}), 400
    
    new_reply = {
        'id': len(quick_replies) + 1,
        'content': data['content'],
        'group': data.get('group', 'custom')
    }
    
    quick_replies.append(new_reply)
    
    return jsonify({
        "code": 200,
        "message": "添加快捷回复成功",
        "data": new_reply
    }), 200

@web_customer_service_api.route('/auto-reply', methods=['GET'])
def get_auto_reply_settings():
    """WEB端-获取自动回复设置"""
    # 模拟自动回复设置
    auto_reply_settings = {
        'enabled': True,
        'greeting_message': '您好，欢迎咨询我们的客服，我们会尽快为您解答问题。',
        'offline_message': '抱歉，客服暂时不在线，请留言，我们会尽快回复您。',
        'working_hours': {
            'start': '09:00',
            'end': '18:00'
        }
    }
    
    return jsonify({
        "code": 200,
        "message": "获取自动回复设置成功",
        "data": auto_reply_settings
    }), 200

@web_customer_service_api.route('/auto-reply', methods=['PUT'])
def update_auto_reply_settings():
    """WEB端-更新自动回复设置"""
    data = request.json
    
    if not data:
        return jsonify({"code": 400, "message": "设置数据不能为空"}), 400
    
    # 模拟更新设置
    updated_settings = {
        'enabled': data.get('enabled', True),
        'greeting_message': data.get('greeting_message', ''),
        'offline_message': data.get('offline_message', ''),
        'working_hours': data.get('working_hours', {})
    }
    
    return jsonify({
        "code": 200,
        "message": "自动回复设置更新成功",
        "data": updated_settings
    }), 200

@web_customer_service_api.route('/statistics', methods=['GET'])
def get_customer_service_statistics():
    """WEB端-获取客服统计数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    today = datetime.utcnow().date()
    
    # 模拟统计数据
    statistics = {
        'today_messages': 15,
        'pending_messages': 3,
        'replied_messages': 12,
        'avg_response_time': '2.5小时',
        'customer_satisfaction': 4.8,
        'total_messages': 156,
        'monthly_trend': [
            {'date': '2024-01-01', 'count': 5},
            {'date': '2024-01-02', 'count': 8},
            {'date': '2024-01-03', 'count': 12},
            {'date': '2024-01-04', 'count': 6},
            {'date': '2024-01-05', 'count': 9},
            {'date': '2024-01-06', 'count': 11},
            {'date': '2024-01-07', 'count': 7}
        ]
    }
    
    return jsonify({
        "code": 200,
        "message": "获取客服统计成功",
        "data": statistics
    }), 200

@web_customer_service_api.route('/common-questions', methods=['GET'])
def get_common_questions():
    """WEB端-获取常见问题"""
    common_questions = [
        {
            'id': 1,
            'question': '如何查询订单物流？',
            'answer': '您可以在订单详情页面查看物流信息，或者联系客服提供订单号查询。',
            'group': 'order'
        },
        {
            'id': 2,
            'question': '支持哪些支付方式？',
            'answer': '我们支持微信支付、支付宝、银行卡等多种支付方式。',
            'group': 'payment'
        },
        {
            'id': 3,
            'question': '退换货政策是什么？',
            'answer': '我们支持7天无理由退换货，商品质量问题支持15天退换。',
            'group': 'return'
        },
        {
            'id': 4,
            'question': '发货时间是多长？',
            'answer': '正常情况下，我们会在24小时内发货，偏远地区可能需要2-3天。',
            'group': 'shipping'
        }
    ]
    
    return jsonify({
        "code": 200,
        "message": "获取常见问题成功",
        "data": common_questions
    }), 200

@web_customer_service_api.route('/common-questions', methods=['POST'])
def add_common_question():
    """WEB端-添加常见问题"""
    data = request.json
    
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({"code": 400, "message": "问题和答案不能为空"}), 400
    
    new_question = {
        'id': 5,  # 模拟ID
        'question': data['question'],
        'answer': data['answer'],
        'group': data.get('group', 'other')
    }
    
    return jsonify({
        "code": 200,
        "message": "添加常见问题成功",
        "data": new_question
    }), 200 