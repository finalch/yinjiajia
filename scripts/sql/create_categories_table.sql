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

-- 为products表添加category_id字段（如果不存在）
ALTER TABLE products ADD COLUMN IF NOT EXISTS category_id INT COMMENT '分类ID';
ALTER TABLE products ADD CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL; 