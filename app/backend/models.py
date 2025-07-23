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
    price = db.Column(db.Float, nullable=False)  # 商品价格
    stock = db.Column(db.Integer, default=0)  # 库存数量
    image_url = db.Column(db.String(256))  # 商品图片URL
    video_url = db.Column(db.String(256))  # 商品视频URL
    category = db.Column(db.String(64))  # 商品分类（兼容旧字段）
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # 分类ID（新字段）
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 所属商家ID
    status = db.Column(db.String(16), default='pending')  # 商品状态：pending(审核中)/on_sale(已上架)/off_sale(已下架)/rejected(审核失败)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    reviews = db.relationship('Review', backref='product', lazy=True)  # 商品评价

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)  # 订单ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 下单用户ID
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)  # 商家ID
    total_amount = db.Column(db.Float, nullable=False)  # 订单总金额
    status = db.Column(db.String(32), default='pending')  # 订单状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    logistics = db.relationship('Logistics', backref='order', uselist=False)  # 物流信息

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
