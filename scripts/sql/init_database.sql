-- 电商平台数据库初始化脚本
-- 创建时间: 2024-01-01
-- 说明: 包含所有表结构和基础测试数据

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ecommerce DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ecommerce;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(128) NOT NULL COMMENT '密码（加密存储）',
    email VARCHAR(120) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '手机号',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 创建商家表
CREATE TABLE IF NOT EXISTS merchants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL COMMENT '商家名称',
    email VARCHAR(120) UNIQUE COMMENT '商家邮箱',
    phone VARCHAR(20) COMMENT '商家电话',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_name (name),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商家表';

-- 创建商品分类表
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT '分类名称',
    description VARCHAR(256) COMMENT '分类描述',
    icon_url VARCHAR(256) COMMENT '分类图标URL',
    sort_order INT DEFAULT 0 COMMENT '排序权重',
    status VARCHAR(16) DEFAULT 'active' COMMENT '状态：active/inactive',
    merchant_id INT NOT NULL COMMENT '所属商家ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_status (status),
    INDEX idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 创建商品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(128) NOT NULL COMMENT '商品名称',
    description TEXT COMMENT '商品描述',
    price FLOAT NOT NULL COMMENT '商品价格',
    stock INT DEFAULT 0 COMMENT '库存数量',
    image_url VARCHAR(256) COMMENT '商品图片URL',
    video_url VARCHAR(256) COMMENT '商品视频URL',
    category VARCHAR(64) COMMENT '商品分类（兼容旧字段）',
    category_id INT COMMENT '分类ID（新字段）',
    merchant_id INT NOT NULL COMMENT '所属商家ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_category_id (category_id),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 创建订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '下单用户ID',
    merchant_id INT NOT NULL COMMENT '商家ID',
    total_amount FLOAT NOT NULL COMMENT '订单总金额',
    status VARCHAR(32) DEFAULT 'pending' COMMENT '订单状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_merchant_id (merchant_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 创建评价表
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    product_id INT NOT NULL COMMENT '商品ID',
    content TEXT COMMENT '评价内容',
    rating INT COMMENT '评分',
    image_url VARCHAR(256) COMMENT '评价图片URL',
    video_url VARCHAR(256) COMMENT '评价视频URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='评价表';

-- 创建账户表
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant_id INT NOT NULL COMMENT '商家ID',
    balance FLOAT DEFAULT 0.0 COMMENT '账户余额',
    bank_account VARCHAR(64) COMMENT '银行账户',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE CASCADE,
    INDEX idx_merchant_id (merchant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账户表';

-- 创建物流表
CREATE TABLE IF NOT EXISTS logistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    company VARCHAR(64) COMMENT '物流公司名称',
    tracking_number VARCHAR(64) COMMENT '物流单号',
    status VARCHAR(32) COMMENT '当前物流状态',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_tracking_number (tracking_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物流表';

-- 插入测试数据

-- 插入测试用户
INSERT IGNORE INTO users (id, username, password, email, phone, created_at, updated_at) VALUES
(1, 'testuser', 'password123', 'user@example.com', '13900139000', NOW(), NOW());

-- 插入测试商家
INSERT IGNORE INTO merchants (id, name, email, phone, created_at, updated_at) VALUES
(1, '测试商家', 'merchant@example.com', '13800138000', NOW(), NOW());

-- 插入测试分类
INSERT IGNORE INTO categories (id, name, description, icon_url, sort_order, status, merchant_id, created_at, updated_at) VALUES
(1, '手机数码', '智能手机、平板电脑、数码配件等', 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 1, 'active', 1, NOW(), NOW()),
(2, '服装配饰', '男装、女装、童装、鞋靴、箱包等', 'https://img.alicdn.com/imgextra/i3/O1CN01c26iB51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 2, 'active', 1, NOW(), NOW()),
(3, '家居生活', '家具、家纺、厨具、清洁用品等', 'https://img.alicdn.com/imgextra/i4/O1CN01FgolV51UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 3, 'active', 1, NOW(), NOW()),
(4, '美妆护肤', '护肤、彩妆、香水、个人护理等', 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 4, 'active', 1, NOW(), NOW()),
(5, '运动户外', '运动鞋服、健身器材、户外装备等', '', 5, 'inactive', 1, NOW(), NOW()),
(6, '食品饮料', '零食、饮料、生鲜、保健品等', '', 6, 'active', 1, NOW(), NOW()),
(7, '图书音像', '图书、音像制品、教育用品等', '', 7, 'active', 1, NOW(), NOW()),
(8, '母婴用品', '奶粉、尿布、玩具、童装等', '', 8, 'active', 1, NOW(), NOW());

-- 插入测试商品
INSERT IGNORE INTO products (id, name, description, price, stock, image_url, category_id, merchant_id, created_at, updated_at) VALUES
(1, 'iPhone 15 Pro', '苹果最新旗舰手机，搭载A17 Pro芯片', 7999.00, 50, 'https://img.alicdn.com/imgextra/i1/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 1, 1, NOW(), NOW()),
(2, '华为 Mate 60 Pro', '华为旗舰手机，搭载麒麟芯片', 6999.00, 30, 'https://img.alicdn.com/imgextra/i2/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 1, 1, NOW(), NOW()),
(3, 'Nike Air Max', '经典运动鞋，舒适透气', 899.00, 100, 'https://img.alicdn.com/imgextra/i3/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 2, 1, NOW(), NOW()),
(4, '小米空气净化器', '智能空气净化器，除甲醛', 1299.00, 25, 'https://img.alicdn.com/imgextra/i4/O1CN01Z5paLz1UyR3MKMFvk_!!6000000002585-0-tps-400-400.jpg', 3, 1, NOW(), NOW());

-- 插入测试账户
INSERT IGNORE INTO accounts (id, merchant_id, balance, bank_account, created_at, updated_at) VALUES
(1, 1, 10000.00, '6222021234567890123', NOW(), NOW());

-- 显示创建结果
SELECT 'Database initialization completed successfully!' as message;
SELECT COUNT(*) as total_categories FROM categories;
SELECT COUNT(*) as total_products FROM products;
SELECT COUNT(*) as total_merchants FROM merchants; 