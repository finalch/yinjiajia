from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 假设 db 在 app.py 中初始化
# from app import db

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # 用户ID
    username = db.Column(db.String(64), unique=True, nullable=False)  # 用户名
    password = db.Column(db.String(128), nullable=False)  # 密码（加密存储）
    email = db.Column(db.String(120), unique=True)  # 邮箱
    phone = db.Column(db.String(20))  # 手机号
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    orders = db.relationship('Order', backref='user', lazy=True)  # 用户订单
    reviews = db.relationship('Review', backref='user', lazy=True)  # 用户评价

class Merchant(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)  # 商家ID
    name = db.Column(db.String(128), unique=True, nullable=False)  # 商家名称
    email = db.Column(db.String(120), unique=True)  # 商家邮箱
    phone = db.Column(db.String(20), unique=True, nullable=False)  # 商家电话（唯一）
    password = db.Column(db.String(128), nullable=False)  # 密码（加密存储）
    status = db.Column(db.String(16), default='active')  # 状态：active/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    # 关联关系
    products = db.relationship('Product', backref='merchant', lazy=True)  # 商家商品
    account = db.relationship('Account', backref='merchant', uselist=False)  # 商家账户
    # 商家分组（非外键模式，不定义关系）
    # groups = db.relationship('Group', primaryjoin='Merchant.id == foreign(Group.merchant_id)', lazy=True)
    order_items = db.relationship('OrderItem', backref='merchant', lazy=True)  # 商家订单项
    order_stats = db.relationship('MerchantOrderStats', backref='merchant', lazy=True)  # 商家订单统计

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)  # 分组ID
    name = db.Column(db.String(64), nullable=False)  # 分组名称
    description = db.Column(db.String(256))  # 分组描述
    icon_url = db.Column(db.String(256))  # 分组图标URL
    sort_order = db.Column(db.Integer, default=0)  # 排序权重
    status = db.Column(db.String(16), default='active')  # 状态：active/inactive
    merchant_id = db.Column(db.Integer, nullable=False)  # 所属商家ID（非外键）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    # 分组下的商品（非外键关系）
    # products = db.relationship('Product', backref='group_rel', lazy=True)
# 整个平台通用的全局商品分类
class Category(db.Model):
    __tablename__ = 'global_categories'
    id = db.Column(db.Integer, primary_key=True)  # 分类ID
    uuid = db.Column(db.String(64), nullable=False)  # 分类UUID
    name = db.Column(db.String(64), nullable=False)  # 分类名称
    description = db.Column(db.String(256))  # 分类描述
    icon_url = db.Column(db.String(256))  # 分类图标URL
    sort_order = db.Column(db.Integer, default=0)  # 排序权重
    status = db.Column(db.String(16), default='active')  # 状态：active/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    #  products = db.relationship('Product', backref='global_category_rel', lazy=True)  # 分类下的商品

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)  # 商品ID
    category_uuid = db.Column(db.String(64))  # 品类UUID
    name = db.Column(db.String(128), nullable=False)  # 商品名称
    description = db.Column(db.Text)  # 商品描述
    detail = db.Column(db.Text)  # 商品详情（富文本）
    price = db.Column(db.Float, nullable=False)  # 商品基础价格（最低价格）
    original_price = db.Column(db.Float)  # 原价（用于促销显示）
    stock = db.Column(db.Integer, default=0)  # 总库存数量
    image_url = db.Column(db.String(256))  # 商品图片URL
    video_url = db.Column(db.String(256))  # 商品视频URL
    # group = db.Column(db.String(64))  # 商品分组（兼容旧字段）
    group_id = db.Column(db.Integer)  # 分组ID（非外键）
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 所属商家ID
    status = db.Column(db.String(16), default='pending')  # 商品状态：pending(审核中)/on_sale(已上架)/off_sale(已下架)/rejected(审核失败)
    has_specs = db.Column(db.Boolean, default=False)  # 是否有规格
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关联关系
    reviews = db.relationship('Review', backref='product', lazy=True)  # 商品评价
    specs = db.relationship('ProductSpec', backref='product', lazy=True)  # 商品规格
    spec_combinations = db.relationship('ProductSpecCombination', backref='product', lazy=True)  # 规格组合

class ProductSpec(db.Model):
    __tablename__ = 'product_specs'
    id = db.Column(db.Integer, primary_key=True)  # 规格ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    name = db.Column(db.String(64), nullable=False)  # 规格名称（如：颜色、尺寸）
    values = db.Column(db.Text, nullable=False)  # 规格值列表，JSON格式存储
    sort_order = db.Column(db.Integer, default=0)  # 排序权重
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

class ProductSpecCombination(db.Model):
    __tablename__ = 'product_spec_combinations'
    id = db.Column(db.Integer, primary_key=True)  # 规格组合ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    spec_values = db.Column(db.Text, nullable=False)  # 规格值组合，JSON格式存储
    price = db.Column(db.Float, nullable=False)  # 该规格组合的价格
    stock = db.Column(db.Integer, default=0)  # 该规格组合的库存
    image_url = db.Column(db.String(256))  # 该规格组合的图片
    status = db.Column(db.String(16), default='active')  # 状态：active/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)  # 订单ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 下单用户ID
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # 订单号
    total_amount = db.Column(db.Float, nullable=False)  # 订单总金额
    status = db.Column(db.String(32), default='pending')  # 订单状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    # 关联关系
    logistics = db.relationship('Logistics', backref='order', uselist=False)  # 物流信息

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)  # 订单商品ID
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # 订单ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    spec_combination_id = db.Column(db.Integer, db.ForeignKey('product_spec_combinations.id'))  # 规格组合ID
    price = db.Column(db.Float, nullable=False)  # 商品价格
    quantity = db.Column(db.Integer, nullable=False)  # 商品数量
    subtotal = db.Column(db.Float, nullable=False)  # 小计金额
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 商家ID
    item_status = db.Column(db.String(32), default='pending')  # 商品状态：pending(待处理)/shipped(已发货)/delivered(已送达)/refunded(已退款)
    shipping_company = db.Column(db.String(64))  # 物流公司
    tracking_number = db.Column(db.String(64))  # 物流单号
    shipped_at = db.Column(db.DateTime)  # 发货时间
    delivered_at = db.Column(db.DateTime)  # 送达时间
    refund_reason = db.Column(db.Text)  # 退款原因
    refunded_at = db.Column(db.DateTime)  # 退款时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    # 关联关系
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')
    spec_combination = db.relationship('ProductSpecCombination', backref='order_items')
    # merchant = db.relationship('Merchant', backref='order_items')

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)  # 购物车ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    spec_combination_id = db.Column(db.Integer, db.ForeignKey('product_spec_combinations.id'))  # 规格组合ID
    quantity = db.Column(db.Integer, nullable=False, default=1)  # 数量
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关联关系
    user = db.relationship('User', backref='cart_items')
    product = db.relationship('Product', backref='cart_items')
    spec_combination = db.relationship('ProductSpecCombination', backref='cart_items')

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)  # 评价ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户ID
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # 商品ID
    content = db.Column(db.Text)  # 评价内容
    rating = db.Column(db.Integer)  # 评分
    image_url = db.Column(db.String(256))  # 评价图片URL
    video_url = db.Column(db.String(256))  # 评价视频URL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)  # 账户ID
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 商家ID
    balance = db.Column(db.Float, default=0.0)  # 账户余额
    bank_account = db.Column(db.String(64))  # 银行账户
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

class Logistics(db.Model):
    __tablename__ = 'logistics'
    id = db.Column(db.Integer, primary_key=True)  # 物流ID
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # 订单ID
    company = db.Column(db.String(64))  # 物流公司名称
    tracking_number = db.Column(db.String(64))  # 物流单号
    status = db.Column(db.String(32))  # 当前物流状态
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间

class OrderItemLogistics(db.Model):
    __tablename__ = 'order_item_logistics'
    id = db.Column(db.Integer, primary_key=True)  # 物流ID
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False)  # 订单商品ID
    company = db.Column(db.String(64), nullable=False)  # 物流公司
    tracking_number = db.Column(db.String(64), nullable=False)  # 物流单号
    status = db.Column(db.String(32), default='shipped')  # 物流状态：shipped(已发货)/in_transit(运输中)/delivered(已送达)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关联关系
    order_item = db.relationship('OrderItem', backref='logistics')

class MerchantOrderStats(db.Model):
    __tablename__ = 'merchant_order_stats'
    id = db.Column(db.Integer, primary_key=True)  # 统计ID
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 商家ID
    stat_date = db.Column(db.Date, nullable=False)  # 统计日期
    total_orders = db.Column(db.Integer, default=0)  # 订单总数
    total_sales = db.Column(db.Float, default=0.0)  # 销售总额
    pending_orders = db.Column(db.Integer, default=0)  # 待处理订单数
    paid_orders = db.Column(db.Integer, default=0)  # 已付款订单数
    shipped_orders = db.Column(db.Integer, default=0)  # 已发货订单数
    delivered_orders = db.Column(db.Integer, default=0)  # 已送达订单数
    cancelled_orders = db.Column(db.Integer, default=0)  # 已取消订单数
    refunded_orders = db.Column(db.Integer, default=0)  # 已退款订单数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关联关系
    # merchant = db.relationship('Merchant', backref='order_stats')  # 已在Merchant模型中定义
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('merchant_id', 'stat_date', name='uk_merchant_date'),
    )

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)  # 地址ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 用户ID
    receiver_name = db.Column(db.String(64), nullable=False)  # 收货人姓名
    phone = db.Column(db.String(20), nullable=False)  # 收货人电话
    province = db.Column(db.String(32), nullable=False)  # 省份
    city = db.Column(db.String(32), nullable=False)  # 城市
    district = db.Column(db.String(32), nullable=False)  # 区县
    detail_address = db.Column(db.String(256), nullable=False)  # 详细地址
    is_default = db.Column(db.Boolean, default=False)  # 是否默认地址
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    # 关联关系
    user = db.relationship('User', backref='addresses')
