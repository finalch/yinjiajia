import base64
import random
from config.log import get_logger
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from models import db, Merchant

web_auth_api = Blueprint('web_auth_api', __name__, url_prefix='/api/web/auth')
logger = get_logger(__name__)


def generate_global_merchant_number() -> str:
    """生成全局唯一商家编号（纯数字）：时间戳毫秒 + 4位随机数"""
    epoch_ms = int(datetime.utcnow().timestamp() * 1000)
    rand_suffix = random.randint(1000, 9999)
    return f"M{epoch_ms}{rand_suffix}"


def generate_token(merchant_id: int) -> dict:
    """生成简单token（演示用途）：base64(merchant_id:epoch_ms:rand)
    并提供过期时间（7天）
    """
    epoch_ms = int(datetime.utcnow().timestamp() * 1000)
    rand_suffix = random.randint(100000, 999999)
    raw = f"{merchant_id}:{epoch_ms}:{rand_suffix}".encode('utf-8')
    token = base64.b64encode(raw).decode('utf-8')
    expires_at = datetime.utcnow() + timedelta(days=7)
    return {
        'token': token,
        'expires_at': expires_at.isoformat() + 'Z',
        'expires_in': 7 * 24 * 60 * 60
    }


def parse_token(token: str) -> dict:
    try:
        raw = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        parts = raw.split(':')
        if len(parts) != 3:
            return {}
        merchant_id = int(parts[0])
        epoch_ms = int(parts[1])
        issued_at = datetime.utcfromtimestamp(epoch_ms / 1000.0)
        return {'merchant_id': merchant_id, 'issued_at': issued_at}
    except Exception:
        return {}


@web_auth_api.route('/register', methods=['POST'])
def register():
    """商家端-商家注册：手机号+密码
    规则：
    - 手机号唯一
    - 密码使用base64编码后存储（仅演示，生产请使用强哈希）
    - 生成全局唯一编号，写入Merchant.name（作为唯一ID）
    """
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not phone or not password:
        return jsonify({'code': 400, 'message': '手机号与密码不能为空'}), 400

    try:
        # 校验唯一性
        existing = Merchant.query.filter_by(phone=phone).first()
        if existing:
            return jsonify({'code': 400, 'message': '该手机号已注册'}), 400

        # 生成唯一编号并确保不冲突
        for _ in range(3):
            merchant_number = generate_global_merchant_number()
            conflict = Merchant.query.filter_by(name=merchant_number).first()
            if not conflict:
                break
        else:
            return jsonify({'code': 500, 'message': '生成商家编号失败，请重试'}), 500

        # base64编码密码（演示用）
        encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')

        merchant = Merchant(
            name=merchant_number,
            phone=phone,
            password=encoded_password
        )
        db.session.add(merchant)
        db.session.commit()

        logger.info(f"商家注册成功: merchant_id={merchant.id}, phone={phone}")

        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': {
                'merchant_id': merchant.id,
                'merchant_number': merchant.name,
                'phone': merchant.phone,
                'created_at': merchant.created_at.isoformat() if merchant.created_at else None
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"商家注册失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@web_auth_api.route('/login', methods=['POST'])
def login():
    """商家端-商家登录：手机号+密码（base64 比对）"""
    data = request.get_json(silent=True) or {}
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not phone or not password:
        return jsonify({'code': 400, 'message': '手机号与密码不能为空'}), 400

    try:
        merchant = Merchant.query.filter_by(phone=phone).first()
        if not merchant:
            return jsonify({'code': 400, 'message': '商家不存在'}), 400

        if merchant.status != 'active':
            return jsonify({'code': 400, 'message': '商家账户已被禁用'}), 400

        encoded_password = base64.b64encode(password.encode('utf-8')).decode('utf-8')
        if merchant.password != encoded_password:
            return jsonify({'code': 400, 'message': '手机号或密码不正确'}), 400

        token_info = generate_token(merchant.id)
        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'user_info': {
                    'merchant_id': merchant.id,
                    'merchant_number': merchant.name,
                    'status': merchant.status
                },
                'token_info': {
                    **token_info
                }

            }
        }), 200
    except Exception as e:
        logger.error(f"商家登录失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'登录失败: {str(e)}'}), 500


@web_auth_api.route('/validate', methods=['GET'])
def validate():
    """校验token是否有效（演示版：解析并校验是否未超过7天）"""
    token = request.headers.get('authorization', '').strip()
    if not token:
        return jsonify({'code': 400, 'message': '缺少token'}), 400

    parsed = parse_token(token)
    if not parsed:
        return jsonify({'code': 200, 'data': {'valid': False}}), 200

    issued_at = parsed['issued_at']
    if datetime.utcnow() - issued_at > timedelta(days=7):
        return jsonify({'code': 200, 'data': {'valid': False}}), 200

    return jsonify({'code': 200, 'data': {'valid': True, 'merchant_id': parsed['merchant_id']}}), 200


@web_auth_api.route('/profile', methods=['GET'])
def get_profile():
    """获取商家信息"""
    token = request.args.get('token', '').strip()
    if not token:
        return jsonify({'code': 400, 'message': '缺少token'}), 400

    parsed = parse_token(token)
    if not parsed:
        return jsonify({'code': 400, 'message': 'token无效'}), 400

    merchant_id = parsed['merchant_id']
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return jsonify({'code': 400, 'message': '商家不存在'}), 400

    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': {
            'merchant_id': merchant.id,
            'merchant_number': merchant.name,
            'phone': merchant.phone,
            'email': merchant.email,
            'status': merchant.status,
            'created_at': merchant.created_at.isoformat() if merchant.created_at else None,
            'updated_at': merchant.updated_at.isoformat() if merchant.updated_at else None
        }
    }), 200
