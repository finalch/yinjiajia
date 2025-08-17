from models import db, Product, Order, OrderItem, Cart, ProductSpecCombination, Address
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional
from config.log import get_logger

logger = get_logger(__name__)

class OrderService:
    """订单服务层 - 封装订单相关的业务逻辑"""
    
    @staticmethod
    def get_checkout_products(user_id: int, cart_item_ids: List[str] = None, 
                            product_id: int = None, quantity: int = 1, 
                            spec_combination_id: int = None) -> Dict[str, Any]:
        """获取下单商品信息"""
        logger.info(f"获取下单商品信息: user_id={user_id}, cart_items={cart_item_ids}, product_id={product_id}, quantity={quantity}, spec_combination_id={spec_combination_id}")
        
        products = []
        total_amount = 0
        
        # 处理购物车商品
        if cart_item_ids and cart_item_ids[0]:
            for cart_item_id in cart_item_ids:
                cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user_id).first()
                if cart_item:
                    product = Product.query.get(cart_item.product_id)
                    if product and product.status == 'on_sale':
                        # 获取价格和库存信息
                        price = float(product.price)
                        stock = product.stock
                        
                        # 如果有规格组合，使用规格组合的价格和库存
                        if cart_item.spec_combination_id:
                            spec_combo = ProductSpecCombination.query.get(cart_item.spec_combination_id)
                            if spec_combo and spec_combo.status == 'active':
                                price = float(spec_combo.price)
                                stock = spec_combo.stock
                        
                        item_total = price * cart_item.quantity
                        total_amount += item_total
                        products.append({
                            'cart_item_id': cart_item.id,
                            'product_id': product.id,
                            'product_name': product.name,
                            'product_image': product.image_url,
                            'price': price,
                            'quantity': cart_item.quantity,
                            'subtotal': item_total,
                            'spec_combination_id': cart_item.spec_combination_id
                        })
        
        # 处理直接购买商品
        if product_id:
            product = Product.query.get(product_id)
            if product and product.status == 'on_sale':
                # 获取价格和库存信息
                price = float(product.price)
                stock = product.stock
                
                # 如果有规格组合，使用规格组合的价格和库存
                if spec_combination_id:
                    spec_combo = ProductSpecCombination.query.get(spec_combination_id)
                    if spec_combo and spec_combo.product_id == product_id and spec_combo.status == 'active':
                        price = float(spec_combo.price)
                        stock = spec_combo.stock
                
                item_total = price * quantity
                total_amount += item_total
                products.append({
                    'cart_item_id': None,
                    'product_id': product.id,
                    'product_name': product.name,
                    'product_image': product.image_url,
                    'price': price,
                    'quantity': quantity,
                    'subtotal': item_total,
                    'spec_combination_id': spec_combination_id
                })
        
        logger.info(f"下单商品信息获取成功: 商品数量={len(products)}, 总金额={total_amount}")
        
        return {
            'products': products,
            'total_amount': total_amount,
            'product_count': len(products)
        }
    
    @staticmethod
    def create_order(user_id: int, address_id: int, cart_item_ids: List[int] = None, 
                    direct_buy: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建订单
        - 购物车下单：按商家拆单创建多个订单
        - 直接购买：创建单个订单
        返回：orders 列表 + total_amount 汇总
        """
        logger.info(f"开始创建订单: user_id={user_id}, address_id={address_id}, cart_items={cart_item_ids}, direct_buy={direct_buy}")
        
        # 验证地址是否存在且属于该用户
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            logger.error(f"地址不存在或不属于用户: address_id={address_id}, user_id={user_id}")
            raise ValueError("收货地址不存在")
        
        created_orders = []
        total_amount_all = 0.0

        # 处理购物车商品：按商家拆单
        if cart_item_ids:
            logger.info(f"处理购物车商品(按商家拆单): {cart_item_ids}")
            # 先收集购物车项并按商家分组
            merchant_to_cart_items: Dict[int, List[Cart]] = {}
            cart_items_found: List[Cart] = []
            for cart_item_id in cart_item_ids:
                cart_item = Cart.query.filter_by(id=cart_item_id, user_id=user_id).first()
                if not cart_item:
                    continue
                product = Product.query.get(cart_item.product_id)
                if not product or product.status != 'on_sale':
                    continue
                merchant_id = product.merchant_id
                merchant_to_cart_items.setdefault(merchant_id, []).append(cart_item)
                cart_items_found.append(cart_item)

            # 为每个商家创建一个订单
            for merchant_id, grouped_cart_items in merchant_to_cart_items.items():
                order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
                order = Order(
                    user_id=user_id,
                    order_number=order_number,
                    status='pending',
                    total_amount=0
                )
                db.session.add(order)
                db.session.flush()

                order_total = 0.0
                for cart_item in grouped_cart_items:
                    product = Product.query.get(cart_item.product_id)
                    if not product or product.status != 'on_sale':
                        continue
                    price = float(product.price)
                    stock = product.stock
                    spec_combo = None
                    if cart_item.spec_combination_id:
                        spec_combo = ProductSpecCombination.query.get(cart_item.spec_combination_id)
                        if spec_combo and spec_combo.status == 'active':
                            price = float(spec_combo.price)
                            stock = spec_combo.stock
                    # 库存校验
                    if stock < cart_item.quantity:
                        raise ValueError(f"商品 {product.name} 库存不足")
                    # 创建订单项
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        price=price,
                        quantity=cart_item.quantity,
                        subtotal=price * cart_item.quantity,
                        spec_combination_id=cart_item.spec_combination_id,
                        merchant_id=product.merchant_id
                    )
                    db.session.add(order_item)
                    # 扣减库存
                    if spec_combo:
                        spec_combo.stock -= cart_item.quantity
                    else:
                        product.stock -= cart_item.quantity
                    order_total += order_item.subtotal
                order.total_amount = order_total
                total_amount_all += order_total
                created_orders.append({
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'total_amount': order_total
                })

            # 删除已处理的购物车项
            for ci in cart_items_found:
                try:
                    db.session.delete(ci)
                except Exception:
                    pass

        # 处理直接购买（单单）
        if direct_buy and not cart_item_ids:
            logger.info(f"处理直接购买商品: {direct_buy}")
            product_id = direct_buy['product_id']
            quantity = direct_buy['quantity']
            spec_combination_id = direct_buy.get('spec_combination_id')

            product = Product.query.get(product_id)
            if product and product.status == 'on_sale':
                price = float(product.price)
                stock = product.stock
                spec_combo = None
                if spec_combination_id:
                    spec_combo = ProductSpecCombination.query.get(spec_combination_id)
                    if spec_combo and spec_combo.product_id == product_id and spec_combo.status == 'active':
                        price = float(spec_combo.price)
                        stock = spec_combo.stock
                if stock < quantity:
                    raise ValueError(f"商品 {product.name} 库存不足")
                order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
                order = Order(
                    user_id=user_id,
                    order_number=order_number,
                    status='pending',
                    total_amount=0
                )
                db.session.add(order)
                db.session.flush()
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    price=price,
                    quantity=quantity,
                    subtotal=price * quantity,
                    spec_combination_id=spec_combination_id,
                    merchant_id=product.merchant_id
                )
                db.session.add(order_item)
                if spec_combo:
                    spec_combo.stock -= quantity
                else:
                    product.stock -= quantity
                order.total_amount = order_item.subtotal
                total_amount_all += order.total_amount
                created_orders.append({
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'total_amount': order.total_amount
                })

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"订单创建失败: {str(e)}", exc_info=True)
            raise

        return {
            'orders': created_orders,
            'total_amount': total_amount_all
        }
    
    @staticmethod
    def get_user_orders(user_id: int, status: str = '', page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """获取用户订单列表"""
        
        query = Order.query.filter_by(user_id=user_id)
        # 注意：状态筛选现在在应用层处理，因为状态是基于OrderItem计算的
        query = query.order_by(Order.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        orders = []
        for order in pagination.items:
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            items = []
            for item in order_items:
                product = Product.query.get(item.product_id)
                items.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': product.name if product else '',
                    'product_image': product.image_url if product else '',
                    'price': float(item.price),
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal),
                    'spec_combination_id': item.spec_combination_id,
                    'merchant_id': item.merchant_id,
                    'merchant_name': (product.merchant.name if getattr(product, 'merchant', None) else '')
                })
            
            # 从OrderItem中获取物流信息
            logistics_info = None
            shipped_items = [item for item in order_items if item.shipping_company and item.tracking_number]
            
            if shipped_items:
                # 使用第一个有物流信息的商品作为主要物流信息
                main_item = shipped_items[0]
                logistics_info = {
                    'tracking_number': main_item.tracking_number,
                    'carrier': main_item.shipping_company,
                    'status': main_item.item_status,
                    'updated_at': main_item.shipped_at.isoformat() if main_item.shipped_at else None
                }
            
            # 计算物流驱动的状态，并与订单自身状态合并
            derived_status = OrderService._calculate_order_status(order_items)
            order_status = order.status
            if order_status not in ('cancelled', 'refunded', 'completed') and derived_status in ('shipped', 'delivered'):
                order_status = derived_status
            
            # 如果指定了状态筛选，检查订单状态是否匹配
            if status and order_status != status:
                continue
            
            orders.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order_status,
                'status_text': OrderService._get_order_status_text(order_status),
                'total_amount': float(order.total_amount),
                'items': items,
                'logistics': logistics_info,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            })
        
        # 重新计算分页信息，因为筛选可能改变了结果数量
        total_filtered = len(orders)
        pages = (total_filtered + per_page - 1) // per_page if total_filtered > 0 else 0
        
        return {
            'list': orders,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_filtered,
                'pages': pages,
                'has_prev': page > 1,
                'has_next': page < pages
            }
        }
    
    @staticmethod
    def _calculate_order_status(order_items: List[OrderItem]) -> str:
        """根据订单项状态计算订单整体状态"""
        if not order_items:
            return 'pending'
        
        # 统计各状态的数量
        status_counts = {}
        for item in order_items:
            status = item.item_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_items = len(order_items)
        
        # 如果所有商品都已送达，订单状态为已送达
        if status_counts.get('delivered', 0) == total_items:
            return 'delivered'
        
        # 如果有任何商品已发货，订单状态为已发货
        if status_counts.get('shipped', 0) > 0 or status_counts.get('delivered', 0) > 0:
            return 'shipped'
        
        # 如果所有商品都是待处理状态，则保持待付款
        if status_counts.get('pending', 0) == total_items:
            return 'pending'
        
        # 默认：未发货/未送达，保持待付款
        return 'pending'
    
    @staticmethod
    def _get_order_status_text(status: str) -> str:
        """获取订单状态文本"""
        status_map = {
            'pending': '待付款',
            'paid': '已付款',
            'shipped': '已发货',
            'delivered': '已送达',
            'completed': '已完成',
            'cancelled': '已取消',
            'refunded': '已退款'
        }
        return status_map.get(status, '未知状态') 