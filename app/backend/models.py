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
    phone = db.Column(db.String(20))  # 商家电话
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    products = db.relationship('Product', backref='merchant', lazy=True)  # 商家商品
    orders = db.relationship('Order', backref='merchant', lazy=True)  # 商家订单
    account = db.relationship('Account', backref='merchant', uselist=False)  # 商家账户
    categories = db.relationship('Category', backref='merchant', lazy=True)  # 商家分类

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)  # 分类ID
    name = db.Column(db.String(64), nullable=False)  # 分类名称
    description = db.Column(db.String(256))  # 分类描述
    icon_url = db.Column(db.String(256))  # 分类图标URL
    sort_order = db.Column(db.Integer, default=0)  # 排序权重
    status = db.Column(db.String(16), default='active')  # 状态：active/inactive
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 所属商家ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    products = db.relationship('Product', backref='category_rel', lazy=True)  # 分类下的商品

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)  # 商品ID
    name = db.Column(db.String(128), nullable=False)  # 商品名称
    description = db.Column(db.Text)  # 商品描述
    detail = db.Column(db.Text)  # 商品详情（富文本）
    price = db.Column(db.Float, nullable=False)  # 商品基础价格（最低价格）
    original_price = db.Column(db.Float)  # 原价（用于促销显示）
    stock = db.Column(db.Integer, default=0)  # 总库存数量
    image_url = db.Column(db.String(256))  # 商品图片URL
    video_url = db.Column(db.String(256))  # 商品视频URL
    category = db.Column(db.String(64))  # 商品分类（兼容旧字段）
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 分类ID（新字段）
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
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 商家ID
    order_number = db.Column(db.String(50), unique=True, nullable=False)  # 订单号
    total_amount = db.Column(db.Float, nullable=False)  # 订单总金额
    status = db.Column(db.String(32), default='pending')  # 订单状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    # 关联关系
    order = db.relationship('Order', backref='items')
    product = db.relationship('Product', backref='order_items')
    spec_combination = db.relationship('ProductSpecCombination', backref='order_items')

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
