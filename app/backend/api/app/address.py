from flask import Blueprint, jsonify, request
from models import db, Address, User

app_address_api = Blueprint('app_address_api', __name__, url_prefix='/api/app/address')

@app_address_api.route('/', methods=['GET'])
def get_addresses():
    """APP端-获取用户收货地址列表"""
    # TODO: 这里应该从JWT token中获取用户ID，暂时使用参数
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({
            'code': 400,
            'message': '用户ID不能为空'
        }), 400
    
    addresses = Address.query.filter_by(user_id=user_id).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    
    address_list = []
    for address in addresses:
        address_list.append({
            'id': address.id,
            'receiver_name': address.receiver_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'detail_address': address.detail_address,
            'is_default': address.is_default,
            'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}",
            'created_at': address.created_at.isoformat() if address.created_at else None,
            'updated_at': address.updated_at.isoformat() if address.updated_at else None
        })
    
    return jsonify({
        'code': 200,
        'message': '获取收货地址列表成功',
        'data': address_list
    })

@app_address_api.route('/', methods=['POST'])
def create_address():
    """APP端-创建收货地址"""
    data = request.get_json()
    
    # 验证必填字段
    required_fields = ['user_id', 'receiver_name', 'phone', 'province', 'city', 'district', 'detail_address']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'code': 400,
                'message': f'{field}不能为空'
            }), 400
    
    user_id = data['user_id']
    receiver_name = data['receiver_name']
    phone = data['phone']
    province = data['province']
    city = data['city']
    district = data['district']
    detail_address = data['detail_address']
    is_default = data.get('is_default', False)
    
    # 如果设置为默认地址，需要将其他地址设为非默认
    if is_default:
        Address.query.filter_by(user_id=user_id, is_default=True).update({'is_default': False})
    
    # 创建新地址
    new_address = Address(
        user_id=user_id,
        receiver_name=receiver_name,
        phone=phone,
        province=province,
        city=city,
        district=district,
        detail_address=detail_address,
        is_default=is_default
    )
    
    try:
        db.session.add(new_address)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建收货地址成功',
            'data': {
                'id': new_address.id,
                'receiver_name': new_address.receiver_name,
                'phone': new_address.phone,
                'province': new_address.province,
                'city': new_address.city,
                'district': new_address.district,
                'detail_address': new_address.detail_address,
                'is_default': new_address.is_default,
                'full_address': f"{new_address.province}{new_address.city}{new_address.district}{new_address.detail_address}",
                'created_at': new_address.created_at.isoformat() if new_address.created_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建收货地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """APP端-更新收货地址"""
    data = request.get_json()
    
    address = Address.query.get(address_id)
    if not address:
        return jsonify({
            'code': 404,
            'message': '收货地址不存在'
        }), 404
    
    # 更新字段
    if 'receiver_name' in data:
        address.receiver_name = data['receiver_name']
    if 'phone' in data:
        address.phone = data['phone']
    if 'province' in data:
        address.province = data['province']
    if 'city' in data:
        address.city = data['city']
    if 'district' in data:
        address.district = data['district']
    if 'detail_address' in data:
        address.detail_address = data['detail_address']
    
    # 处理默认地址设置
    if 'is_default' in data:
        is_default = data['is_default']
        if is_default:
            # 将其他地址设为非默认
            Address.query.filter_by(user_id=address.user_id, is_default=True).update({'is_default': False})
        address.is_default = is_default
    
    try:
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新收货地址成功',
            'data': {
                'id': address.id,
                'receiver_name': address.receiver_name,
                'phone': address.phone,
                'province': address.province,
                'city': address.city,
                'district': address.district,
                'detail_address': address.detail_address,
                'is_default': address.is_default,
                'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}",
                'updated_at': address.updated_at.isoformat() if address.updated_at else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新收货地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """APP端-删除收货地址"""
    address = Address.query.get(address_id)
    if not address:
        return jsonify({
            'code': 404,
            'message': '收货地址不存在'
        }), 404
    
    try:
        db.session.delete(address)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除收货地址成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除收货地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>/set-default', methods=['PUT'])
def set_default_address(address_id):
    """APP端-设置默认收货地址"""
    address = Address.query.get(address_id)
    if not address:
        return jsonify({
            'code': 404,
            'message': '收货地址不存在'
        }), 404
    
    try:
        # 将其他地址设为非默认
        Address.query.filter_by(user_id=address.user_id, is_default=True).update({'is_default': False})
        # 设置当前地址为默认
        address.is_default = True
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '设置默认地址成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'设置默认地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['GET'])
def get_address_detail(address_id):
    """APP端-获取收货地址详情"""
    address = Address.query.get(address_id)
    if not address:
        return jsonify({
            'code': 404,
            'message': '收货地址不存在'
        }), 404
    
    return jsonify({
        'code': 200,
        'message': '获取收货地址详情成功',
        'data': {
            'id': address.id,
            'receiver_name': address.receiver_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'detail_address': address.detail_address,
            'is_default': address.is_default,
            'full_address': f"{address.province}{address.city}{address.district}{address.detail_address}",
            'created_at': address.created_at.isoformat() if address.created_at else None,
            'updated_at': address.updated_at.isoformat() if address.updated_at else None
        }
    }) 