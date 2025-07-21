from flask import Blueprint, request, jsonify
from models import db, Category, Merchant
from datetime import datetime
import logging
import os

# 创建蓝图
category_bp = Blueprint('web_category_api', __name__, url_prefix='/api/web/categories')
logger = logging.getLogger(__name__)
# 获取分类列表
@category_bp.route('/', methods=['GET'])
def get_categories():
    logger.info("get_categories")
    try:
        # 获取查询参数
        merchant_id = request.args.get('merchant_id', type=int)
        status = request.args.get('status', 'active')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 构建查询
        query = Category.query
        
        if merchant_id:
            query = query.filter(Category.merchant_id == merchant_id)
        
        if status:
            query = query.filter(Category.status == status)
        
        # 按排序权重和创建时间排序
        query = query.order_by(Category.sort_order.desc(), Category.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        categories = pagination.items
        
        # 格式化返回数据
        result = {
            'code': 200,
            'message': '获取分类列表成功',
            'data': {
                'list': [{
                    'id': cat.id,
                    'name': cat.name,
                    'description': cat.description,
                    'icon_url': cat.icon_url,
                    'sort_order': cat.sort_order,
                    'status': cat.status,
                    'merchant_id': cat.merchant_id,
                    'product_count': len(cat.products),
                    'created_at': cat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': cat.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                } for cat in categories],
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
        return jsonify({
            'code': 500,
            'message': f'获取分类列表失败: {str(e)}',
            'data': None
        }), 500

# 获取单个分类详情
@category_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        result = {
            'code': 200,
            'message': '获取分类详情成功',
            'data': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon_url': category.icon_url,
                'sort_order': category.sort_order,
                'status': category.status,
                'merchant_id': category.merchant_id,
                'product_count': len(category.products),
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': category.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取分类详情失败: {str(e)}',
            'data': None
        }), 500

# 创建新分类
@category_bp.route('/categories', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name'):
            return jsonify({
                'code': 400,
                'message': '分类名称不能为空',
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
        
        # 检查分类名称是否已存在（同一商家下）
        existing_category = Category.query.filter_by(
            name=data['name'], 
            merchant_id=data['merchant_id']
        ).first()
        
        if existing_category:
            return jsonify({
                'code': 400,
                'message': '该分类名称已存在',
                'data': None
            }), 400
        
        # 创建新分类
        new_category = Category()
        new_category.name = data['name']
        new_category.description = data.get('description', '')
        new_category.icon_url = data.get('icon_url', '')
        new_category.sort_order = data.get('sort_order', 0)
        new_category.status = data.get('status', 'active')
        new_category.merchant_id = data['merchant_id']
        
        db.session.add(new_category)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '创建分类成功',
            'data': {
                'id': new_category.id,
                'name': new_category.name,
                'description': new_category.description,
                'icon_url': new_category.icon_url,
                'sort_order': new_category.sort_order,
                'status': new_category.status,
                'merchant_id': new_category.merchant_id,
                'created_at': new_category.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': new_category.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'创建分类失败: {str(e)}',
            'data': None
        }), 500

# 更新分类
@category_bp.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            # 检查名称是否重复（排除自己）
            existing_category = Category.query.filter_by(
                name=data['name'], 
                merchant_id=category.merchant_id
            ).filter(Category.id != category_id).first()
            
            if existing_category:
                return jsonify({
                    'code': 400,
                    'message': '该分类名称已存在',
                    'data': None
                }), 400
            
            category.name = data['name']
        
        if 'description' in data:
            category.description = data['description']
        
        if 'icon_url' in data:
            category.icon_url = data['icon_url']
        
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        if 'status' in data:
            category.status = data['status']
        
        category.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '更新分类成功',
            'data': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon_url': category.icon_url,
                'sort_order': category.sort_order,
                'status': category.status,
                'merchant_id': category.merchant_id,
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': category.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'更新分类失败: {str(e)}',
            'data': None
        }), 500

# 删除分类
@category_bp.route('/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # 检查是否有商品使用此分类
        if category.products:
            return jsonify({
                'code': 400,
                'message': '该分类下还有商品，无法删除',
                'data': None
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': '删除分类成功',
            'data': None
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'删除分类失败: {str(e)}',
            'data': None
        }), 500

# 批量删除分类
@category_bp.route('/categories/batch', methods=['DELETE'])
def batch_delete_categories():
    try:
        data = request.get_json()
        category_ids = data.get('category_ids', [])
        
        if not category_ids:
            return jsonify({
                'code': 400,
                'message': '请选择要删除的分类',
                'data': None
            }), 400
        
        # 检查是否有分类下有商品
        categories_with_products = Category.query.filter(
            Category.id.in_(category_ids),
            Category.products.any()
        ).all()
        
        if categories_with_products:
            category_names = [cat.name for cat in categories_with_products]
            return jsonify({
                'code': 400,
                'message': f'以下分类下还有商品，无法删除: {", ".join(category_names)}',
                'data': None
            }), 400
        
        # 删除分类
        deleted_count = Category.query.filter(Category.id.in_(category_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        result = {
            'code': 200,
            'message': f'成功删除 {deleted_count} 个分类',
            'data': {
                'deleted_count': deleted_count
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': f'批量删除分类失败: {str(e)}',
            'data': None
        }), 500 