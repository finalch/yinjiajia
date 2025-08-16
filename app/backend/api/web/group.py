from flask import Blueprint, request, jsonify
from models import db, Group, Merchant
from datetime import datetime
import logging
import os

# 创建蓝图
web_group_api = Blueprint('web_group_api', __name__, url_prefix='/api/web/groups')
logger = logging.getLogger(__name__)

# 获取分组列表
@web_group_api.route('/', methods=['GET'])
def get_groups():
    logger.info("get_groups")
    try:
        # 获取查询参数
        merchant_id = request.args.get('merchant_id', type=int)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建查询
        query = Group.query
        
        if merchant_id:
            query = query.filter(Group.merchant_id == merchant_id)
        
        if status:
            query = query.filter(Group.status == status)
        
        # 按排序权重和创建时间排序
        query = query.order_by(Group.sort_order.desc(), Group.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        groups = pagination.items
        
        # 格式化返回数据
        result = {
            'code': 200,
            'message': '获取分组列表成功',
            'data': {
                'list': [{
                    'id': grp.id,
                    'name': grp.name,
                    'description': grp.description,
                    'icon_url': grp.icon_url,
                    'sort_order': grp.sort_order,
                    'status': grp.status,
                    'merchant_id': grp.merchant_id,
                    'product_count': 0,  # 非外键模式，暂时设为0
                    'created_at': grp.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': grp.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                } for grp in groups],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取分组列表失败: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'获取分组列表失败: {str(e)}',
            'data': None
        }), 500

# 获取单个分组详情
@web_group_api.route('/<int:group_id>', methods=['GET'])
def get_group(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        
        result = {
            'code': 200,
            'message': '获取分组详情成功',
            'data': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'icon_url': group.icon_url,
                'sort_order': group.sort_order,
                'status': group.status,
                'merchant_id': group.merchant_id,
                'product_count': 0,  # 非外键模式，暂时设为0
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': group.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分组详情失败: {str(e)}',
            'data': None
        }), 500

# 创建新分组
@web_group_api.route('/', methods=['POST'])
def create_group():
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '分组名称不能为空',
                'data': None
            }), 400
        
        if not data.get('merchant_id'):
            return jsonify({
                'code': 400,
                'message': '商家ID不能为空',
                'data': None
            }), 400
        
        # 检查商家是否存在
        merchant = Merchant.query.get(data['merchant_id'])
        if not merchant:
            return jsonify({
                'code': 404,
                'message': '商家不存在',
                'data': None
            }), 404
        
        # 检查分组名称是否已存在（同一商家下）
        existing_group = Group.query.filter_by(
            name=data['name'], 
            merchant_id=data['merchant_id']
        ).first()
        
        if existing_group:
            return jsonify({
                'code': 400,
                'message': '该分组名称已存在',
                'data': None
            }), 400
        
        # 创建新分组
        new_group = Group()
        new_group.name = data['name']
        new_group.description = data.get('description', '')
        new_group.icon_url = data.get('icon_url', '')
        new_group.sort_order = data.get('sort_order', 0)
        new_group.status = data.get('status', 'active')
        new_group.merchant_id = data['merchant_id']
        
        db.session.add(new_group)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '创建分组成功',
            'data': {
                'id': new_group.id,
                'name': new_group.name,
                'description': new_group.description,
                'icon_url': new_group.icon_url,
                'sort_order': new_group.sort_order,
                'status': new_group.status,
                'merchant_id': new_group.merchant_id,
                'created_at': new_group.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': new_group.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建分组失败: {str(e)}',
            'data': None
        }), 500

# 更新分组
@web_group_api.route('/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复（排除自己）
            existing_group = Group.query.filter_by(
                name=data['name'], 
                merchant_id=group.merchant_id
            ).filter(Group.id != group_id).first()
            
            if existing_group:
                return jsonify({
                    'code': 400,
                    'message': '该分组名称已存在',
                    'data': None
                }), 400
            
            group.name = data['name']
        
        if 'description' in data:
            group.description = data['description']
        
        if 'icon_url' in data:
            group.icon_url = data['icon_url']
        
        if 'sort_order' in data:
            group.sort_order = data['sort_order']
        
        if 'status' in data:
            group.status = data['status']
        
        group.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '更新分组成功',
            'data': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'icon_url': group.icon_url,
                'sort_order': group.sort_order,
                'status': group.status,
                'merchant_id': group.merchant_id,
                'created_at': group.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': group.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新分组失败: {str(e)}',
            'data': None
        }), 500

# 删除分组
@web_group_api.route('/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    try:
        group = Group.query.get_or_404(group_id)
        
        # 检查是否有商品使用此分组
        if group.products:
            return jsonify({
                'code': 500,
                'message': '该分组下还有商品，无法删除',
                'data': None
            }), 400
        
        db.session.delete(group)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '删除分组成功',
            'data': None
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除分组失败: {str(e)}',
            'data': None
        }), 500

# 批量删除分组
@web_group_api.route('/batch', methods=['DELETE'])
def batch_delete_groups():
    try:
        data = request.get_json()
        group_ids = data.get('group_ids', [])
        
        if not group_ids:
            return jsonify({
                'code': 400,
                'message': '请选择要删除的分组',
                'data': None
            }), 400
        
        # 检查是否有分组下有商品
        groups_with_products = Group.query.filter(
            Group.id.in_(group_ids),
            Group.products.any()
        ).all()
        
        if groups_with_products:
            group_names = [grp.name for grp in groups_with_products]
            return jsonify({
                'code': 400,
                'message': f'以下分组下还有商品，无法删除: {", ".join(group_names)}',
                'data': None
            }), 400
        
        # 删除分组
        deleted_count = Group.query.filter(Group.id.in_(group_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': f'成功删除 {deleted_count} 个分组',
            'data': {
                'deleted_count': deleted_count
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'批量删除分组失败: {str(e)}',
            'data': None
        }), 500
