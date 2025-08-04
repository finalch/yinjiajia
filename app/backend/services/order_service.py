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
        """创建订单"""
        logger.info(f"开始创建订单: user_id={user_id}, address_id={address_id}, cart_items={cart_item_ids}, direct_buy={direct_buy}")
        
        # 验证地址是否存在且属于该用户
        address = Address.query.filter_by(id=address_id, user_id=user_id).first()
        if not address:
            logger.error(f"地址不存在或不属于用户: address_id={address_id}, user_id={user_id}")
            raise ValueError("收货地址不存在")
        
        # 生成订单号
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"生成订单号: {order_number}")
        
        # 创建订单
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status='pending',
            total_amount=0
        )
        
        db.session.add(order)
        db.session.flush()  # 获取order.id
        
        total_amount = 0
        order_items = []
        
        # 处理购物车商品
        if cart_item_ids:
            logger.info(f"处理购物车商品: {cart_item_ids}")
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
                        
                        # 检查库存
                        if stock < cart_item.quantity:
                            logger.warning(f"商品库存不足: product_id={product.id}, stock={stock}, quantity={cart_item.quantity}")
                            raise ValueError(f"商品 {product.name} 库存不足")
                        
                        # 创建订单项
                        order_item = OrderItem(
                            order_id=order.id,
                            product_id=product.id,
                            price=price,
                            quantity=cart_item.quantity,
                            subtotal=price * cart_item.quantity,
                            spec_combination_id=cart_item.spec_combination_id
                        )
                        db.session.add(order_item)
                        order_items.append(order_item)
                        
                        # 更新库存
                        if cart_item.spec_combination_id:
                            spec_combo.stock -= cart_item.quantity
                        else:
                            product.stock -= cart_item.quantity
                        
                        total_amount += order_item.subtotal
                        
                        # 删除购物车项
                        db.session.delete(cart_item)
                        logger.info(f"购物车商品处理完成: product_id={product.id}, quantity={cart_item.quantity}, price={price}")
        
        # 处理直接购买商品
        if direct_buy:
            logger.info(f"处理直接购买商品: {direct_buy}")
            product_id = direct_buy['product_id']
            quantity = direct_buy['quantity']
            spec_combination_id = direct_buy.get('spec_combination_id')
            
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
                
                # 检查库存
                if stock < quantity:
                    logger.warning(f"商品库存不足: product_id={product.id}, stock={stock}, quantity={quantity}")
                    raise ValueError(f"商品 {product.name} 库存不足")
                
                # 创建订单项
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    price=price,
                    quantity=quantity,
                    subtotal=price * quantity,
                    spec_combination_id=spec_combination_id
                )
                db.session.add(order_item)
                order_items.append(order_item)
                
                # 更新库存
                if spec_combination_id:
                    spec_combo.stock -= quantity
                else:
                    product.stock -= quantity
                
                total_amount += order_item.subtotal
                logger.info(f"直接购买商品处理完成: product_id={product.id}, quantity={quantity}, price={price}")
        
        # 更新订单总金额
        order.total_amount = total_amount
        
        try:
            db.session.commit()
            logger.info(f"订单创建成功: order_id={order.id}, order_number={order_number}, total_amount={total_amount}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"订单创建失败: {str(e)}", exc_info=True)
            raise
        
        return {
            'order_id': order.id,
            'order_number': order.order_number,
            'total_amount': total_amount,
            'items': order_items
        }
    
    @staticmethod
    def get_user_orders(user_id: int, status: str = '', page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """获取用户订单列表"""
        from models import Logistics
        
        query = Order.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
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
                    'spec_combination_id': item.spec_combination_id
                })
            
            logistics = Logistics.query.filter_by(order_id=order.id).first()
            logistics_info = None
            if logistics:
                logistics_info = {
                    'id': logistics.id,
                    'tracking_number': logistics.tracking_number,
                    'carrier': logistics.carrier,
                    'status': logistics.status,
                    'updated_at': logistics.updated_at.isoformat() if logistics.updated_at else None
                }
            
            orders.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'status_text': OrderService._get_order_status_text(order.status),
                'total_amount': float(order.total_amount),
                'items': items,
                'logistics': logistics_info,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'updated_at': order.updated_at.isoformat() if order.updated_at else None
            })
        
        return {
            'list': orders,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }
    
    @staticmethod
    def _get_order_status_text(status: str) -> str:
        """获取订单状态文本"""
        status_map = {
            'pending': '待付款',
            'paid': '已付款',
            'shipped': '已发货',
            'delivered': '已送达',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        return status_map.get(status, '未知状态') 