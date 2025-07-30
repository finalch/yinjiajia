from flask import Blueprint, jsonify, request
from models import db, Account, Order, Merchant
from datetime import datetime, timedelta
from sqlalchemy import func

web_finance_api = Blueprint('web_finance_api', __name__, url_prefix='/api/web/finance')

@web_finance_api.route('/account', methods=['GET'])
def get_account_info():
    """WEB端-获取账户信息"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    account = Account.query.filter_by(merchant_id=merchant_id).first()
    
    if not account:
        # 创建新账户
        account = Account(
            merchant_id=merchant_id,
            balance=0.0,
            bank_account=''
        )
        db.session.add(account)
        db.session.commit()
    
    # 计算可提现金额（总收入减去已提现）
    total_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    available_balance = total_income - account.balance
    
    account_data = {
        'id': account.id,
        'merchant_id': account.merchant_id,
        'balance': float(account.balance),
        'available_balance': float(available_balance),
        'total_income': float(total_income),
        'bank_account': account.bank_account,
        'created_at': account.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': account.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return jsonify({
        "code": 200,
        "message": "获取账户信息成功",
        "data": account_data
    }), 200

@web_finance_api.route('/account', methods=['PUT'])
def update_account_info():
    """WEB端-更新账户信息（主要是银行账户）"""
    merchant_id = request.args.get('merchant_id', type=int)
    data = request.json
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    if not data or 'bank_account' not in data:
        return jsonify({"code": 400, "message": "银行账户信息不能为空"}), 400
    
    account = Account.query.filter_by(merchant_id=merchant_id).first()
    
    if not account:
        return jsonify({"code": 404, "message": "账户不存在"}), 404
    
    account.bank_account = data['bank_account']
    account.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "账户信息更新成功",
            "data": {
                'id': account.id,
                'bank_account': account.bank_account
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"更新失败: {str(e)}"}), 500

@web_finance_api.route('/withdraw', methods=['POST'])
def request_withdraw():
    """WEB端-申请提现"""
    merchant_id = request.args.get('merchant_id', type=int)
    data = request.json
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    if not data or 'amount' not in data:
        return jsonify({"code": 400, "message": "提现金额不能为空"}), 400
    
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({"code": 400, "message": "提现金额必须大于0"}), 400
    except ValueError:
        return jsonify({"code": 400, "message": "提现金额格式错误"}), 400
    
    account = Account.query.filter_by(merchant_id=merchant_id).first()
    
    if not account:
        return jsonify({"code": 404, "message": "账户不存在"}), 404
    
    # 计算可提现金额
    total_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    available_balance = total_income - account.balance
    
    if amount > available_balance:
        return jsonify({"code": 400, "message": "可提现金额不足"}), 400
    
    # 更新账户余额
    account.balance += amount
    account.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "提现申请成功",
            "data": {
                'withdraw_amount': amount,
                'new_balance': float(account.balance),
                'available_balance': float(available_balance - amount)
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "message": f"提现失败: {str(e)}"}), 500

@web_finance_api.route('/transactions', methods=['GET'])
def get_transaction_history():
    """WEB端-获取交易记录"""
    merchant_id = request.args.get('merchant_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transaction_type = request.args.get('type', type=str)  # income, withdraw
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    # 收入记录（订单）
    income_query = Order.query.filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    )
    
    # 提现记录（这里需要创建提现记录表，暂时用账户余额变化模拟）
    # 实际实现需要创建 WithdrawRecord 表
    
    if transaction_type == 'income':
        query = income_query
    elif transaction_type == 'withdraw':
        # 暂时返回空，需要实现提现记录表
        return jsonify({
            "code": 200,
            "message": "获取提现记录成功",
            "data": {
                "list": [],
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": 0,
                    "pages": 0
                }
            }
        }), 200
    else:
        # 返回所有记录
        query = income_query
    
    # 分页
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    transactions = []
    for order in pagination.items:
        transaction = {
            'id': order.id,
            'type': 'income',
            'amount': float(order.total_amount),
            'description': f'订单收入 - 订单号: {order.id}',
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        transactions.append(transaction)
    
    return jsonify({
        "code": 200,
        "message": "获取交易记录成功",
        "data": {
            "list": transactions,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200

@web_finance_api.route('/statistics', methods=['GET'])
def get_finance_statistics():
    """WEB端-获取财务统计数据"""
    merchant_id = request.args.get('merchant_id', type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    today = datetime.utcnow().date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # 今日收入
    today_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        func.date(Order.created_at) == today,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 本月收入
    this_month_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= this_month_start,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 上月收入
    last_month_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.created_at >= last_month_start,
        Order.created_at < this_month_start,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 总收入
    total_income = db.session.query(func.sum(Order.total_amount)).filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    ).scalar() or 0
    
    # 账户信息
    account = Account.query.filter_by(merchant_id=merchant_id).first()
    account_balance = account.balance if account else 0.0
    available_balance = total_income - account_balance
    
    # 收入增长率
    growth_rate = 0
    if last_month_income > 0:
        growth_rate = ((this_month_income - last_month_income) / last_month_income) * 100
    
    return jsonify({
        "code": 200,
        "message": "获取财务统计成功",
        "data": {
            "today_income": float(today_income),
            "this_month_income": float(this_month_income),
            "last_month_income": float(last_month_income),
            "total_income": float(total_income),
            "account_balance": float(account_balance),
            "available_balance": float(available_balance),
            "growth_rate": round(growth_rate, 2)
        }
    }), 200

@web_finance_api.route('/bills', methods=['GET'])
def get_bill_details():
    """WEB端-获取账单明细"""
    merchant_id = request.args.get('merchant_id', type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if not merchant_id:
        return jsonify({"code": 400, "message": "商家ID不能为空"}), 400
    
    query = Order.query.filter(
        Order.merchant_id == merchant_id,
        Order.status.in_(['paid', 'shipped', 'delivered'])
    )
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Order.created_at >= start_dt)
        except ValueError:
            return jsonify({"code": 400, "message": "开始日期格式错误"}), 400
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Order.created_at <= end_dt)
        except ValueError:
            return jsonify({"code": 400, "message": "结束日期格式错误"}), 400
    
    # 分页
    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    bills = []
    for order in pagination.items:
        bill = {
            'id': order.id,
            'order_id': order.id,
            'amount': float(order.total_amount),
            'type': 'income',
            'description': f'订单收入',
            'status': order.status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        bills.append(bill)
    
    return jsonify({
        "code": 200,
        "message": "获取账单明细成功",
        "data": {
            "list": bills,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages
            }
        }
    }), 200 