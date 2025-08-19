from flask import Blueprint, jsonify, request, g
from address_service import AddressService

app_address_api = Blueprint('app_address_api', __name__, url_prefix='/api/app/address')

@app_address_api.route('/', methods=['GET'])
def get_addresses():
    """APP端-获取用户地址列表"""
    user_id = g.user_id
    
    try:
        addresses = AddressService.get_user_addresses(user_id)
        
        return jsonify({
            'code': 200,
            'message': '获取地址列表成功',
            'data': addresses
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取地址列表失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['GET'])
def get_address(address_id):
    """APP端-获取单个地址详情"""
    user_id = g.user_id
    
    try:
        address = AddressService.get_address_by_id(address_id, user_id)
        
        if not address:
            return jsonify({
                'code': 404,
                'message': '地址不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取地址详情成功',
            'data': address
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取地址详情失败: {str(e)}'
        }), 500

@app_address_api.route('/', methods=['POST'])
def create_address():
    """APP端-创建新地址"""
    user_id = g.user_id
    address_data = {
        'receiver_name': request.json.get('receiver_name'),
        'phone': request.json.get('phone'),
        'province': request.json.get('province'),
        'city': request.json.get('city'),
        'district': request.json.get('district'),
        'detail_address': request.json.get('detail_address'),
        'is_default': request.json.get('is_default', False)
    }
    
    # 验证必填字段
    required_fields = ['receiver_name', 'phone', 'province', 'city', 'district', 'detail_address']
    for field in required_fields:
        if not address_data[field]:
            return jsonify({
                'code': 400,
                'message': f'缺少必填字段: {field}'
            }), 400
    
    try:
        new_address = AddressService.create_address(user_id, address_data)
        
        return jsonify({
            'code': 200,
            'message': '创建地址成功',
            'data': new_address
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'创建地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """APP端-更新地址"""
    user_id = g.user_id
    address_data = {
        'receiver_name': request.json.get('receiver_name'),
        'phone': request.json.get('phone'),
        'province': request.json.get('province'),
        'city': request.json.get('city'),
        'district': request.json.get('district'),
        'detail_address': request.json.get('detail_address'),
        'is_default': request.json.get('is_default', False)
    }
    
    # 移除None值
    address_data = {k: v for k, v in address_data.items() if v is not None}
    
    try:
        updated_address = AddressService.update_address(address_id, user_id, address_data)
        
        if not updated_address:
            return jsonify({
                'code': 404,
                'message': '地址不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '更新地址成功',
            'data': updated_address
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'更新地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """APP端-删除地址"""
    user_id = g.user_id
    
    try:
        success = AddressService.delete_address(address_id, user_id)
        
        if not success:
            return jsonify({
                'code': 404,
                'message': '地址不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '删除地址成功'
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'删除地址失败: {str(e)}'
        }), 500

@app_address_api.route('/default', methods=['GET'])
def get_default_address():
    """APP端-获取用户默认地址"""
    user_id = g.user_id
    
    try:
        default_address = AddressService.get_default_address(user_id)
        
        return jsonify({
            'code': 200,
            'message': '获取默认地址成功',
            'data': default_address
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取默认地址失败: {str(e)}'
        }), 500

@app_address_api.route('/<int:address_id>/set-default', methods=['PUT'])
def set_default_address(address_id):
    """APP端-设置默认地址"""
    user_id = g.user_id
    
    try:
        success = AddressService.set_default_address(address_id, user_id)
        
        if not success:
            return jsonify({
                'code': 404,
                'message': '地址不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '设置默认地址成功'
        }), 200
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'设置默认地址失败: {str(e)}'
        }), 500 