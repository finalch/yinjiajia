-- 基于 models.py 生成的建表语句
-- 创建数据库表结构

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 商家表
CREATE TABLE merchants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    status VARCHAR(16) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 商家分组表
CREATE TABLE groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    description VARCHAR(256),
    icon_url VARCHAR(256),
    sort_order INT DEFAULT 0,
    status VARCHAR(16) DEFAULT 'active',
    merchant_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 商品分类表
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(64) NOT NULL,
    name VARCHAR(64) NOT NULL,
    description VARCHAR(256),
    icon_url VARCHAR(256),
    sort_order INT DEFAULT 0,
    status VARCHAR(16) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 商品表
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_uuid VARCHAR(64),
    name VARCHAR(128) NOT NULL,
    description TEXT,
    detail TEXT,
    price FLOAT NOT NULL,
    original_price FLOAT,
    stock INT DEFAULT 0,
    image_url VARCHAR(256),
    video_url VARCHAR(256),
    group_id INT,
    merchant_id INT NOT NULL,
    status VARCHAR(16) DEFAULT 'pending',
    has_specs BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
);

-- 商品规格表
CREATE TABLE product_specs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(64) NOT NULL,
    values TEXT NOT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 商品规格组合表
CREATE TABLE product_spec_combinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    spec_values TEXT NOT NULL,
    price FLOAT NOT NULL,
    stock INT DEFAULT 0,
    image_url VARCHAR(256),
    status VARCHAR(16) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 订单表
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount FLOAT NOT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 订单商品表
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    spec_combination_id INT,
    price FLOAT NOT NULL,
    quantity INT NOT NULL,
    subtotal FLOAT NOT NULL,
    merchant_id INT NOT NULL,
    item_status VARCHAR(32) DEFAULT 'pending',
    shipping_company VARCHAR(64),
    tracking_number VARCHAR(64),
    shipped_at DATETIME,
    delivered_at DATETIME,
    refund_reason TEXT,
    refunded_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (spec_combination_id) REFERENCES product_spec_combinations(id),
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
);

-- 购物车表
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    spec_combination_id INT,
    quantity INT NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (spec_combination_id) REFERENCES product_spec_combinations(id)
);

-- 评价表
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    content TEXT,
    rating INT,
    image_url VARCHAR(256),
    video_url VARCHAR(256),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 商家账户表
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT NOT NULL,
    balance FLOAT DEFAULT 0.0,
    bank_account VARCHAR(64),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id)
);

-- 物流表
CREATE TABLE logistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    company VARCHAR(64),
    tracking_number VARCHAR(64),
    status VARCHAR(32),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- 订单商品物流表
CREATE TABLE order_item_logistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    company VARCHAR(64) NOT NULL,
    tracking_number VARCHAR(64) NOT NULL,
    status VARCHAR(32) DEFAULT 'shipped',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_item_id) REFERENCES order_items(id)
);

-- 商家订单统计表
CREATE TABLE merchant_order_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT NOT NULL,
    stat_date DATE NOT NULL,
    total_orders INT DEFAULT 0,
    total_sales FLOAT DEFAULT 0.0,
    pending_orders INT DEFAULT 0,
    paid_orders INT DEFAULT 0,
    shipped_orders INT DEFAULT 0,
    delivered_orders INT DEFAULT 0,
    cancelled_orders INT DEFAULT 0,
    refunded_orders INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id),
    UNIQUE KEY uk_merchant_date (merchant_id, stat_date)
);

-- 地址表
CREATE TABLE addresses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receiver_name VARCHAR(64) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(32) NOT NULL,
    city VARCHAR(32) NOT NULL,
    district VARCHAR(32) NOT NULL,
    detail_address VARCHAR(256) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 创建索引以提高查询性能
CREATE INDEX idx_products_merchant_id ON products(merchant_id);
CREATE INDEX idx_products_category_uuid ON products(category_uuid);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_order_items_merchant_id ON order_items(merchant_id);
CREATE INDEX idx_order_items_status ON order_items(item_status);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_cart_user_id ON cart(user_id);
CREATE INDEX idx_reviews_product_id ON reviews(product_id);
CREATE INDEX idx_groups_merchant_id ON groups(merchant_id);
