from flask import Blueprint, request, jsonify, g
from models import db, Warehouse
from config.log import get_logger
from datetime import datetime

# 创建蓝图
web_warehouse_api = Blueprint('web_warehouse_api', __name__, url_prefix='/api/web/warehouse')

# 获取logger
logger = get_logger(__name__)


@web_warehouse_api.route('/list', methods=['GET'])
def get_warehouse_list():
    """获取仓库列表"""
    try:
        merchant_id = g.merchant_id
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')  # 可选的状态筛选
        
        # 构建查询
        query = Warehouse.query.filter_by(merchant_id=merchant_id)
        
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 分页查询
        pagination = query.order_by(Warehouse.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        warehouses = []
        for warehouse in pagination.items:
            warehouses.append({
                'id': warehouse.id,
                'name': warehouse.name,
                'address': warehouse.detail_address,
                'province': warehouse.province,
                'city': warehouse.city,
                'district': warehouse.district,
                'contact_person': warehouse.contact_person,
                'contact_phone': warehouse.contact_phone,
                'remark': warehouse.remark,
                'status': warehouse.status,
                'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': warehouse.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'code': 200,
            'message': '获取仓库列表成功',
            'data': {
                'warehouses': warehouses,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"获取仓库列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '获取仓库列表失败',
            'data': None
        }), 500


@web_warehouse_api.route('/detail/<int:warehouse_id>', methods=['GET'])
def get_warehouse_detail(warehouse_id):
    """获取仓库详情"""
    try:
        merchant_id = g.merchant_id
        
        warehouse = Warehouse.query.filter_by(
            id=warehouse_id, 
            merchant_id=merchant_id
        ).first()
        
        if not warehouse:
            return jsonify({
                'code': 404,
                'message': '仓库不存在',
                'data': None
            }), 404
        
        warehouse_data = {
            'id': warehouse.id,
            'name': warehouse.name,
            'address': warehouse.detail_address,
            'province': warehouse.province,
            'city': warehouse.city,
            'district': warehouse.district,
            'contact_person': warehouse.contact_person,
            'contact_phone': warehouse.contact_phone,
            'remark': warehouse.remark,
            'status': warehouse.status,
            'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': warehouse.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            'code': 200,
            'message': '获取仓库详情成功',
            'data': warehouse_data
        })
        
    except Exception as e:
        logger.error(f"获取仓库详情失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '获取仓库详情失败',
            'data': None
        }), 500


@web_warehouse_api.route('/create', methods=['POST'])
def create_warehouse():
    """创建仓库"""
    try:
        merchant_id = g.merchant_id
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['name', 'address', 'contact_person', 'contact_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'code': 400,
                    'message': f'缺少必填字段: {field}',
                    'data': None
                }), 400
        
        # 检查仓库名称是否重复
        existing_warehouse = Warehouse.query.filter_by(
            merchant_id=merchant_id,
            name=data['name']
        ).first()
        
        if existing_warehouse:
            return jsonify({
                'code': 400,
                'message': '仓库名称已存在',
                'data': None
            }), 400
        
        # 创建新仓库
        warehouse = Warehouse(
            merchant_id=merchant_id,
            name=data['name'],
            address=data['address'],
            province=data['province'],
            city=data['city'],
            district=data['district'],
            contact_person=data['contact_person'],
            contact_phone=data['contact_phone'],
            remark=data.get('remark', ''),
            status=data.get('status', 'active')
        )
        
        db.session.add(warehouse)
        db.session.commit()
        
        logger.info(f"商家 {merchant_id} 创建仓库成功: {warehouse.name}")
        
        return jsonify({
            'code': 200,
            'message': '创建仓库成功',
            'data': {
                'id': warehouse.id,
                'name': warehouse.name,
                'address': warehouse.address,
                'province': warehouse.province,
                'city': warehouse.city,
                'district': warehouse.district,
                'contact_person': warehouse.contact_person,
                'contact_phone': warehouse.contact_phone,
                'remark': warehouse.remark,
                'status': warehouse.status,
                'created_at': warehouse.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"创建仓库失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '创建仓库失败',
            'data': None
        }), 500


@web_warehouse_api.route('/update/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    """更新仓库信息"""
    try:
        merchant_id = g.merchant_id
        data = request.get_json()
        
        warehouse = Warehouse.query.filter_by(
            id=warehouse_id,
            merchant_id=merchant_id
        ).first()
        
        if not warehouse:
            return jsonify({
                'code': 404,
                'message': '仓库不存在',
                'data': None
            }), 404
        
        # 如果更新仓库名称，检查是否重复
        if 'name' in data and data['name'] != warehouse.name:
            existing_warehouse = Warehouse.query.filter_by(
                merchant_id=merchant_id,
                name=data['name']
            ).first()
            
            if existing_warehouse:
                return jsonify({
                    'code': 400,
                    'message': '仓库名称已存在',
                    'data': None
                }), 400
        
        # 更新字段
        if 'name' in data:
            warehouse.name = data['name']
        if 'address' in data:
            warehouse.address = data['address']
        if 'province' in data:
            warehouse.province = data['province']
        if 'city' in data:
            warehouse.city = data['city']
        if 'district' in data:
            warehouse.district = data['district']
        if 'contact_person' in data:
            warehouse.contact_person = data['contact_person']
        if 'contact_phone' in data:
            warehouse.contact_phone = data['contact_phone']
        if 'remark' in data:
            warehouse.remark = data['remark']
        if 'status' in data:
            warehouse.status = data['status']
        
        warehouse.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"商家 {merchant_id} 更新仓库成功: {warehouse.name}")
        
        return jsonify({
            'code': 200,
            'message': '更新仓库成功',
            'data': {
                'id': warehouse.id,
                'name': warehouse.name,
                'address': warehouse.address,
                'province': warehouse.province,
                'city': warehouse.city,
                'district': warehouse.district,
                'contact_person': warehouse.contact_person,
                'contact_phone': warehouse.contact_phone,
                'remark': warehouse.remark,
                'status': warehouse.status,
                'updated_at': warehouse.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新仓库失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '更新仓库失败',
            'data': None
        }), 500


@web_warehouse_api.route('/toggle-status/<int:warehouse_id>', methods=['PUT'])
def toggle_warehouse_status(warehouse_id):
    """切换仓库状态"""
    try:
        merchant_id = g.merchant_id
        
        warehouse = Warehouse.query.filter_by(
            id=warehouse_id,
            merchant_id=merchant_id
        ).first()
        
        if not warehouse:
            return jsonify({
                'code': 404,
                'message': '仓库不存在',
                'data': None
            }), 404
        
        # 切换状态
        warehouse.status = 'inactive' if warehouse.status == 'active' else 'active'
        warehouse.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"商家 {merchant_id} 切换仓库状态成功: {warehouse.name} -> {warehouse.status}")
        
        return jsonify({
            'code': 200,
            'message': f'仓库状态已切换为{"启用" if warehouse.status == "active" else "禁用"}',
            'data': {
                'id': warehouse.id,
                'name': warehouse.name,
                'status': warehouse.status,
                'updated_at': warehouse.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"切换仓库状态失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '切换仓库状态失败',
            'data': None
        }), 500


@web_warehouse_api.route('/delete/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    """删除仓库"""
    try:
        merchant_id = g.merchant_id
        
        warehouse = Warehouse.query.filter_by(
            id=warehouse_id,
            merchant_id=merchant_id
        ).first()
        
        if not warehouse:
            return jsonify({
                'code': 404,
                'message': '仓库不存在',
                'data': None
            }), 404
        
        warehouse_name = warehouse.name
        db.session.delete(warehouse)
        db.session.commit()
        
        logger.info(f"商家 {merchant_id} 删除仓库成功: {warehouse_name}")
        
        return jsonify({
            'code': 200,
            'message': '删除仓库成功',
            'data': None
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除仓库失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '删除仓库失败',
            'data': None
        }), 500


@web_warehouse_api.route('/batch-delete', methods=['DELETE'])
def batch_delete_warehouses():
    """批量删除仓库"""
    try:
        merchant_id = g.merchant_id
        data = request.get_json()
        
        warehouse_ids = data.get('warehouse_ids', [])
        if not warehouse_ids:
            return jsonify({
                'code': 400,
                'message': '请选择要删除的仓库',
                'data': None
            }), 400
        
        # 查询要删除的仓库
        warehouses = Warehouse.query.filter(
            Warehouse.id.in_(warehouse_ids),
            Warehouse.merchant_id == merchant_id
        ).all()
        
        if not warehouses:
            return jsonify({
                'code': 404,
                'message': '未找到要删除的仓库',
                'data': None
            }), 404
        
        # 删除仓库
        warehouse_names = [w.name for w in warehouses]
        for warehouse in warehouses:
            db.session.delete(warehouse)
        
        db.session.commit()
        
        logger.info(f"商家 {merchant_id} 批量删除仓库成功: {warehouse_names}")
        
        return jsonify({
            'code': 200,
            'message': f'成功删除 {len(warehouses)} 个仓库',
            'data': {
                'deleted_count': len(warehouses),
                'deleted_names': warehouse_names
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"批量删除仓库失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'message': '批量删除仓库失败',
            'data': None
        }), 500
